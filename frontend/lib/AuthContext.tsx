"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { User, Session } from "@supabase/supabase-js";
import { supabase } from "@/lib/supabase";

export type UserRole = "coordinator" | "special_educator";

interface UserProfile {
  id: string;
  email: string;
  role: UserRole;
  fullName: string;
}

interface AuthContextType {
  user: User | null;
  session: Session | null;
  profile: UserProfile | null;
  loading: boolean;
  signOut: () => Promise<void>;
  setDemoUser: (role: UserRole, email: string, name: string) => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  session: null,
  profile: null,
  loading: true,
  signOut: async () => {},
  setDemoUser: () => {},
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 1. Check active Supabase session
    const getInitialSession = async () => {
      try {
        const { data: { session: currentSession } } = await supabase.auth.getSession();
        if (currentSession) {
          setSession(currentSession);
          setUser(currentSession.user);
          const metaRole = (currentSession.user.user_metadata?.role as UserRole) || "coordinator";
          const fullName = currentSession.user.user_metadata?.full_name || currentSession.user.email?.split("@")[0] || "User";
          setProfile({
            id: currentSession.user.id,
            email: currentSession.user.email || "",
            role: metaRole,
            fullName,
          });
        } else {
          // Check local storage for quick session/demo state
          const savedRole = localStorage.getItem("rg_role") as UserRole;
          const savedEmail = localStorage.getItem("rg_email");
          const savedName = localStorage.getItem("rg_name");
          if (savedRole && savedEmail) {
            setProfile({
              id: "local-user",
              email: savedEmail,
              role: savedRole,
              fullName: savedName || savedEmail.split("@")[0],
            });
          }
        }
      } catch (err) {
        console.error("Session check error:", err);
      } finally {
        setLoading(false);
      }
    };

    getInitialSession();

    // 2. Subscribe to auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, newSession) => {
      setSession(newSession);
      setUser(newSession?.user ?? null);
      if (newSession?.user) {
        const metaRole = (newSession.user.user_metadata?.role as UserRole) || "coordinator";
        const fullName = newSession.user.user_metadata?.full_name || newSession.user.email?.split("@")[0] || "User";
        setProfile({
          id: newSession.user.id,
          email: newSession.user.email || "",
          role: metaRole,
          fullName,
        });
      } else {
        const savedRole = localStorage.getItem("rg_role") as UserRole;
        if (!savedRole) {
          setProfile(null);
        }
      }
      setLoading(false);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const signOut = async () => {
    try {
      await supabase.auth.signOut();
    } catch {
      // Ignore
    }
    localStorage.removeItem("rg_role");
    localStorage.removeItem("rg_email");
    localStorage.removeItem("rg_name");
    setUser(null);
    setSession(null);
    setProfile(null);
  };

  const setDemoUser = (role: UserRole, email: string, name: string) => {
    localStorage.setItem("rg_role", role);
    localStorage.setItem("rg_email", email);
    localStorage.setItem("rg_name", name);
    setProfile({
      id: "demo-user-" + Date.now(),
      email,
      role,
      fullName: name,
    });
  };

  return (
    <AuthContext.Provider value={{ user, session, profile, loading, signOut, setDemoUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
