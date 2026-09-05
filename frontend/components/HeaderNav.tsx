"use client";

import Link from "next/link";
import { useAuth } from "@/lib/AuthContext";
import { LogIn, LogOut, User, UserCheck } from "lucide-react";

export function HeaderNav() {
  const { profile, signOut } = useAuth();

  return (
    <header className="bg-slate-900 text-white shadow-md border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-indigo-600 text-white p-2 rounded-lg font-bold text-lg">
            🛡️
          </div>
          <Link href="/" className="text-xl font-bold tracking-tight hover:text-indigo-300 transition">
            Referral Guardian
          </Link>
          <span className="bg-indigo-900/80 text-indigo-300 text-xs font-semibold px-2.5 py-0.5 rounded border border-indigo-700 hidden sm:inline">
            Continuity MVP
          </span>
        </div>

        {/* Portal Switcher & Auth Controls */}
        <nav className="flex items-center space-x-2 sm:space-x-4 text-sm font-medium">
          <Link
            href="/"
            className="px-3 py-1.5 rounded-lg bg-slate-800 text-indigo-300 hover:bg-slate-700 transition flex items-center space-x-1.5 border border-slate-700 text-xs sm:text-sm"
          >
            <span>📋</span>
            <span>Coordinator</span>
          </Link>

          <Link
            href="/educator"
            className="px-3 py-1.5 rounded-lg bg-purple-900/50 text-purple-300 hover:bg-purple-800/60 transition flex items-center space-x-1.5 border border-purple-700/60 text-xs sm:text-sm"
          >
            <span>🎓</span>
            <span>Special Educator</span>
          </Link>

          {profile ? (
            <div className="flex items-center space-x-2 bg-slate-800/90 pl-3 pr-1 py-1 rounded-full border border-slate-700">
              <div className="flex items-center space-x-1.5">
                {profile.role === "special_educator" ? (
                  <UserCheck className="w-3.5 h-3.5 text-purple-400" />
                ) : (
                  <User className="w-3.5 h-3.5 text-indigo-400" />
                )}
                <span className="text-xs text-slate-200 max-w-[120px] truncate font-medium">
                  {profile.fullName}
                </span>
              </div>
              <button
                onClick={signOut}
                className="p-1 text-slate-400 hover:text-rose-400 rounded-full transition"
                title="Sign out"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <Link
                href="/login"
                className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white transition text-xs font-semibold flex items-center space-x-1 shadow-xs"
              >
                <LogIn className="w-3.5 h-3.5" />
                <span>Sign In</span>
              </Link>
            </div>
          )}
        </nav>
      </div>
    </header>
  );
}
