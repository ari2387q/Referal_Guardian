"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { supabase } from "@/lib/supabase";
import { useAuth, UserRole } from "@/lib/AuthContext";
import { Lock, Mail, ShieldAlert, ArrowRight, Sparkles, User, UserCheck, Eye, EyeOff } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { setDemoUser } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [role, setRole] = useState<UserRole>("coordinator");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;

    setLoading(true);
    setErrorMsg(null);

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) {
        // If Supabase authentication throws error, display friendly message
        setErrorMsg(error.message);
      } else if (data?.user) {
        const userRole = (data.user.user_metadata?.role as UserRole) || role;
        if (userRole === "special_educator") {
          router.push("/educator");
        } else {
          router.push("/");
        }
      }
    } catch (err: any) {
      setErrorMsg(err.message || "An unexpected error occurred during login.");
    } finally {
      setLoading(false);
    }
  };

  // Quick 1-click Demo Logins for evaluating both sides instantly
  const handleQuickDemo = (demoRole: UserRole) => {
    if (demoRole === "coordinator") {
      setDemoUser("coordinator", "dr.smith@school.org", "Dr. Jane Smith (Coordinator)");
      router.push("/");
    } else {
      setDemoUser("special_educator", "dr.vance@clinic.org", "Dr. Marcus Vance (Special Educator)");
      router.push("/educator");
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
            Sign In to Referral Guardian
          </h1>
          <p className="text-xs text-slate-500">
            Secure authentication powered by <strong>Supabase Auth</strong>
          </p>
        </div>

        {/* Quick Demo Selector */}
        <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-4 rounded-xl border border-indigo-100 space-y-2.5">
          <div className="flex items-center space-x-1.5 text-xs font-bold text-indigo-900">
            <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
            <span>Instant Demo Access (No password required)</span>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => handleQuickDemo("coordinator")}
              className="px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold shadow-xs transition flex items-center justify-center space-x-1"
            >
              <User className="w-3.5 h-3.5" />
              <span>Coordinator</span>
            </button>
            <button
              type="button"
              onClick={() => handleQuickDemo("special_educator")}
              className="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-xs font-semibold shadow-xs transition flex items-center justify-center space-x-1"
            >
              <UserCheck className="w-3.5 h-3.5" />
              <span>Special Educator</span>
            </button>
          </div>
        </div>

        {/* Form Card */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          {errorMsg && (
            <div className="bg-rose-50 border border-rose-200 rounded-lg p-3 text-xs text-rose-800 flex items-start space-x-2">
              <ShieldAlert className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <span>{errorMsg}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Role Persona
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setRole("coordinator")}
                  className={`py-2 px-3 text-xs font-semibold rounded-lg border transition ${
                    role === "coordinator"
                      ? "bg-indigo-50 text-indigo-700 border-indigo-300 shadow-xs"
                      : "bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100"
                  }`}
                >
                  📋 School Coordinator
                </button>
                <button
                  type="button"
                  onClick={() => setRole("special_educator")}
                  className={`py-2 px-3 text-xs font-semibold rounded-lg border transition ${
                    role === "special_educator"
                      ? "bg-purple-50 text-purple-700 border-purple-300 shadow-xs"
                      : "bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100"
                  }`}
                >
                  🎓 Special Educator
                </button>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type="email"
                  required
                  placeholder="name@school.org"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full text-xs pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-900 focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full text-xs pl-9 pr-9 py-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-900 focus:ring-2 focus:ring-indigo-500"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-600 focus:outline-none"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? (
                    <EyeOff className="w-4 h-4 text-slate-500" />
                  ) : (
                    <Eye className="w-4 h-4 text-slate-400" />
                  )}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs rounded-lg transition shadow-xs flex items-center justify-center space-x-1.5 disabled:opacity-50"
            >
              <span>{loading ? "Authenticating..." : "Sign In with Supabase"}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </form>

          <div className="text-center pt-2 border-t border-slate-100">
            <span className="text-xs text-slate-500">
              Don't have an account yet?{" "}
              <Link href="/signup" className="text-indigo-600 font-semibold hover:underline">
                Create Account
              </Link>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
