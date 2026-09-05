"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { supabase } from "@/lib/supabase";
import { UserRole } from "@/lib/AuthContext";
import {
  Lock,
  Mail,
  ShieldAlert,
  ArrowRight,
  User,
  CheckCircle2,
  Eye,
  EyeOff,
} from "lucide-react";

export default function SignupPage() {
  const router = useRouter();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>("coordinator");

  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!fullName || !email || !password) return;

    setLoading(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,

        options: {
          data: {
            full_name: fullName,
            role,
          },
        },
      });

      if (error) {
        setErrorMsg(error.message);
        return;
      }

      if (data.user) {
        setSuccessMsg(
          "Account created successfully. You can now sign in."
        );

        setTimeout(() => {
          router.replace("/login");
        }, 1500);
      }
    } catch (err) {
      setErrorMsg(
        err instanceof Error
          ? err.message
          : "An unexpected error occurred during registration."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-6 px-4">
      <div className="max-w-md w-full space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-indigo-600 text-white text-2xl shadow-lg shadow-indigo-600/30">
            🛡️
          </div>

          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Create Referral Guardian Account
          </h1>

          <p className="text-xs text-slate-500">
            Create one account and select your role
          </p>
        </div>

        {/* Signup Card */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          {errorMsg && (
            <div className="mb-4 bg-rose-50 border border-rose-200 rounded-lg p-3 text-xs text-rose-800 flex items-start gap-2">
              <ShieldAlert className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <span>{errorMsg}</span>
            </div>
          )}

          {successMsg && (
            <div className="mb-4 bg-emerald-50 border border-emerald-200 rounded-lg p-3 text-xs text-emerald-800 flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
              <span>{successMsg}</span>
            </div>
          )}

          <form onSubmit={handleSignup} className="space-y-4">
            {/* Full Name */}
            <div>
              <label
                htmlFor="fullName"
                className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1"
              >
                Full Name
              </label>

              <div className="relative">
                <User className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />

                <input
                  id="fullName"
                  type="text"
                  required
                  autoComplete="name"
                  placeholder="Dr. Jane Smith"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full text-xs pl-9 pr-3 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-900 outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label
                htmlFor="email"
                className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1"
              >
                Email Address
              </label>

              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />

                <input
                  id="email"
                  type="email"
                  required
                  autoComplete="email"
                  placeholder="name@school.org"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full text-xs pl-9 pr-3 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-900 outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>

            {/* Role */}
            <div>
              <label
                htmlFor="role"
                className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1"
              >
                Role
              </label>

              <select
                id="role"
                value={role}
                onChange={(e) => setRole(e.target.value as UserRole)}
                className="w-full text-xs px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-900 outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="coordinator">School Coordinator</option>
                <option value="special_educator">Special Educator</option>
              </select>
            </div>

            {/* Password */}
            <div>
              <label
                htmlFor="password"
                className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1"
              >
                Password
              </label>

              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />

                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  required
                  minLength={6}
                  autoComplete="new-password"
                  placeholder="Minimum 6 characters"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full text-xs pl-9 pr-10 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-900 outline-none focus:ring-2 focus:ring-indigo-500"
                />

                <button
                  type="button"
                  onClick={() => setShowPassword((prev) => !prev)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  aria-pressed={showPassword}
                >
                  {showPassword ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              </div>

              <p className="mt-1 text-[11px] text-slate-400">
                Minimum 6 characters
              </p>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading || !fullName || !email || !password}
              className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs rounded-lg transition flex items-center justify-center gap-1.5 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span>{loading ? "Creating account..." : "Create Account"}</span>

              {!loading && <ArrowRight className="w-3.5 h-3.5" />}
            </button>
          </form>

          <div className="text-center mt-4 pt-4 border-t border-slate-100">
            <span className="text-xs text-slate-500">
              Already have an account?{" "}
              <Link
                href="/login"
                className="text-indigo-600 font-semibold hover:underline"
              >
                Sign In
              </Link>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
