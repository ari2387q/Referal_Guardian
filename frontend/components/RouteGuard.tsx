"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { portalPath, useAuth, UserRole } from "@/lib/AuthContext";

interface RouteGuardProps {
  /** Which role(s) are allowed. Omit to allow any authenticated user. */
  allowedRoles?: UserRole[];
  children: React.ReactNode;
}

/**
 * Wraps protected pages:
 *  - Unauthenticated → /login
 *  - Wrong role      → their own portal (/ or /educator)
 * Shows a spinner while auth is resolving (no content flash).
 */
export default function RouteGuard({ allowedRoles, children }: RouteGuardProps) {
  const { profile, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;
    if (!profile) {
      router.replace("/login");
      return;
    }
    if (allowedRoles && !allowedRoles.includes(profile.role)) {
      router.replace(portalPath(profile.role));
    }
  }, [loading, profile, allowedRoles, router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3 text-slate-500">
          <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm font-medium">Checking credentials…</p>
        </div>
      </div>
    );
  }

  // Redirect in-flight — render nothing to avoid flicker
  if (!profile) return null;
  if (allowedRoles && !allowedRoles.includes(profile.role)) return null;

  return <>{children}</>;
}
