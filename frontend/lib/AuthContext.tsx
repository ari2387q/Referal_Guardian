"use client";

import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import { User, Session } from "@supabase/supabase-js";
import { supabase } from "@/lib/supabase";

export type UserRole = "coordinator" | "special_educator";

export interface UserProfile {
  id: string;
  email: string;
  role: UserRole;
  fullName: string;
  isDemo?: boolean;
}

export function portalPath(role: UserRole) {
  return role === "special_educator" ? "/educator" : "/";
}

export function isUserRole(value: unknown): value is UserRole {
  return value === "coordinator" || value === "special_educator";
}

function profileFromUser(user: User, fallbackRole: UserRole = "coordinator"): UserProfile {
  const metaRole = user.user_metadata?.role;
  return {
    id: user.id,
    email: user.email || "",
    role: isUserRole(metaRole) ? metaRole : fallbackRole,
    fullName: user.user_metadata?.full_name || user.email?.split("@")[0] || "User",
    isDemo: false,
  };
}

function readDemoProfile(): UserProfile | null {
  if (typeof window === "undefined") return null;
  const role = localStorage.getItem("rg_role");
  const email = localStorage.getItem("rg_email");
  const name = localStorage.getItem("rg_name");
  if (!isUserRole(role) || !email) return null;
  return {
    id: "local-demo-user",
    email,
    role,
    fullName: name || email.split("@")[0],
    isDemo: true,
  };
}

function writeDemoProfile(role: UserRole, email: string, name: string) {
  localStorage.setItem("rg_role", role);
  localStorage.setItem("rg_email", email);
  localStorage.setItem("rg_name", name);
}

function clearDemoStorage() {
  if (typeof window === "undefined") return;
  localStorage.removeItem("rg_role");
  localStorage.removeItem("rg_email");
  localStorage.removeItem("rg_name");
}

interface AuthContextType {
  user: User | null;
  session: Session | null;
  profile: UserProfile | null;
  loading: boolean;
  signOut: () => Promise<void>;
  setDemoUser: (role: UserRole, email: string, name: string) => UserProfile;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  session: null,
  profile: null,
  loading: true,
  signOut: async () => {},
  setDemoUser: () => ({
    id: "demo",
    email: "demo@school.org",
    role: "coordinator",
    fullName: "Coordinator",
    isDemo: true,
  }),
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  const applySession = useCallback((next: Session | null) => {
    setSession(next);
    setUser(next?.user ?? null);
    if (next?.user) {
      clearDemoStorage();
      setProfile(profileFromUser(next.user));
      return;
    }
    setProfile(readDemoProfile());
  }, []);

  useEffect(() => {
    let mounted = true;

    const init = async () => {
      try {
        const { data } = await supabase.auth.getSession();
        if (!mounted) return;
        applySession(data.session);
      } catch (err) {
        console.warn("Supabase session check failed:", err);
        if (mounted) setProfile(readDemoProfile());
      } finally {
        if (mounted) setLoading(false);
      }
    };

    init();

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, next) => {
      if (!mounted) return;
      applySession(next);
      setLoading(false);
    });

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, [applySession]);

  const signOut = async () => {
    clearDemoStorage();
    setUser(null);
    setSession(null);
    setProfile(null);
    try {
      await supabase.auth.signOut();
    } catch {
      // Ignore network errors on sign out
    }
  };

  const setDemoUser = (role: UserRole, email: string, name: string): UserProfile => {
    writeDemoProfile(role, email, name);
    const next: UserProfile = {
      id: "local-demo-user",
      email,
      role,
      fullName: name,
      isDemo: true,
    };
    setUser(null);
    setSession(null);
    setProfile(next);
    void supabase.auth.signOut({ scope: "local" }).catch(() => {});
    return next;
  };

  return (
    <AuthContext.Provider value={{ user, session, profile, loading, signOut, setDemoUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
