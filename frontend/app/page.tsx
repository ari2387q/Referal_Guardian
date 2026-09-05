"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AlertCircle, Clock, CheckCircle2, AlertTriangle, Layers, ArrowUpRight } from "lucide-react";

interface DashboardStats {
  total_cases: number;
  active_cases: number;
  resolved_cases: number;
  bottleneck_cases: number;
  avg_days_open: number;
}

interface CaseItem {
  id: string;
  child_identifier: string;
  referral_type: string;
  status: string;
  current_bottleneck: string | null;
  days_open: number;
  followup_attempts: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function CoordinatorDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [cases, setCases] = useState<CaseItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const [statsRes, casesRes] = await Promise.all([
          fetch(`${API_BASE}/api/dashboard`),
          fetch(`${API_BASE}/api/cases`),
        ]);

        if (!statsRes.ok || !casesRes.ok) {
          throw new Error("Failed to load dashboard data from API");
        }

        const statsData: DashboardStats = await statsRes.json();
        const casesData: CaseItem[] = await casesRes.json();

        setStats(statsData);
        setCases(casesData);
        setError(null);
      } catch (err: any) {
        setError(err.message || "An unexpected error occurred");
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Placeholder Banner */}
      <div className="rounded-lg border border-indigo-200 bg-indigo-50/80 px-4 py-3 text-indigo-900 shadow-sm flex items-center gap-3">
        <AlertCircle className="w-5 h-5 text-indigo-600 shrink-0" />
        <p className="text-sm font-medium">
          AI Agent Coming Soon — Manual tracking mode active
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          <strong>Error connecting to backend:</strong> {error}
        </div>
      )}

      {/* 4 Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Cases */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Total</span>
            <Layers className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-3xl font-bold text-slate-900">
            {loading ? "—" : stats?.total_cases ?? 0}
          </div>
          <p className="text-xs text-slate-500 mt-1">All tracked referrals</p>
        </div>

        {/* Active Cases */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Active</span>
            <Clock className="w-4 h-4 text-indigo-500" />
          </div>
          <div className="text-3xl font-bold text-indigo-600">
            {loading ? "—" : stats?.active_cases ?? 0}
          </div>
          <p className="text-xs text-slate-500 mt-1">Under review / evaluation</p>
        </div>

        {/* Resolved Cases */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Resolved</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-3xl font-bold text-emerald-600">
            {loading ? "—" : stats?.resolved_cases ?? 0}
          </div>
          <p className="text-xs text-slate-500 mt-1">Completed referrals</p>
        </div>

        {/* Bottlenecked Cases */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Bottlenecked</span>
            <AlertTriangle className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-3xl font-bold text-amber-600">
            {loading ? "—" : stats?.bottleneck_cases ?? 0}
          </div>
          <p className="text-xs text-slate-500 mt-1">Action blocked or stalled</p>
        </div>
      </div>

      {/* Cases Table Section */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h2 className="text-base font-semibold text-slate-900">Referral Cases</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Read-only list of special education referral tracking items
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50 text-xs uppercase font-semibold text-slate-500 border-b border-slate-200">
              <tr>
                <th scope="col" className="px-6 py-3.5">Case ID</th>
                <th scope="col" className="px-6 py-3.5">Child</th>
                <th scope="col" className="px-6 py-3.5">Type</th>
                <th scope="col" className="px-6 py-3.5">Status</th>
                <th scope="col" className="px-6 py-3.5">Bottleneck</th>
                <th scope="col" className="px-6 py-3.5">Days Open</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-slate-400">
                    Loading cases...
                  </td>
                </tr>
              ) : cases.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-slate-400">
                    No cases found.
                  </td>
                </tr>
              ) : (
                cases.map((c) => (
                  <tr
                    key={c.id}
                    className="hover:bg-slate-50/80 transition-colors group cursor-pointer"
                  >
                    <td className="px-6 py-4 font-mono font-medium text-indigo-600">
                      <Link
                        href={`/cases/${c.id}`}
                        className="inline-flex items-center gap-1 hover:underline focus:outline-none"
                      >
                        {c.id}
                        <ArrowUpRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </Link>
                    </td>
                    <td className="px-6 py-4 font-medium text-slate-800">
                      {c.child_identifier}
                    </td>
                    <td className="px-6 py-4 text-slate-700">
                      {c.referral_type}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          c.status === "ACTIVE"
                            ? "bg-indigo-100 text-indigo-800"
                            : c.status === "NEW"
                            ? "bg-slate-100 text-slate-800"
                            : "bg-emerald-100 text-emerald-800"
                        }`}
                      >
                        {c.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {c.current_bottleneck ? (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-50 text-amber-800 border border-amber-200">
                          {c.current_bottleneck}
                        </span>
                      ) : (
                        <span className="text-slate-400">—</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-slate-600 font-mono text-xs">
                      {c.days_open} {c.days_open === 1 ? "day" : "days"}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
