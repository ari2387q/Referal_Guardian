"use client";

import React, { useEffect, useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  Clock,
  RefreshCw,
  Search,
  ShieldAlert,
  Sparkles,
  Users,
} from "lucide-react";
import { CaseCard } from "@/components/CaseCard";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface DashboardStats {
  active_cases: number;
  stuck_cases: number;
  pending_actions: number;
  escalations: number;
}

interface CaseItem {
  id: string;
  child_identifier: string;
  referral_type: string;
  status: string;
  current_bottleneck?: string | null;
  days_open: number;
  followup_attempts: number;
  recommendation?: {
    id: string;
    bottleneck: string;
    recommended_action: string;
    priority: string;
  } | null;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats>({
    active_cases: 0,
    stuck_cases: 0,
    pending_actions: 0,
    escalations: 0,
  });
  const [cases, setCases] = useState<CaseItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState<string>("ALL");

  const fetchData = async () => {
    setLoading(true);
    try {
      const [statsRes, casesRes] = await Promise.all([
        fetch(`${API_BASE}/api/dashboard`),
        fetch(`${API_BASE}/api/cases`),
      ]);

      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData);
      }

      if (casesRes.ok) {
        const casesData = await casesRes.json();
        setCases(casesData);
      }
    } catch (err) {
      console.error("Failed to fetch dashboard data", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const filteredCases = cases.filter((c) => {
    const matchesSearch =
      c.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.child_identifier.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.referral_type.toLowerCase().includes(searchTerm.toLowerCase());

    if (!matchesSearch) return false;

    if (filterStatus === "ALL") return true;
    if (filterStatus === "STUCK")
      return c.status === "STUCK" || Boolean(c.current_bottleneck);
    if (filterStatus === "ESCALATED") return c.status === "ESCALATED";
    if (filterStatus === "PENDING_ACTION") return Boolean(c.recommendation);
    return c.status === filterStatus;
  });

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-sm">
                <Sparkles className="w-5 h-5" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900 tracking-tight">
                Referral Guardian
              </h1>
            </div>
            <p className="text-sm text-gray-500 mt-1">
              AI-powered referral continuity & next-best-action guardian
            </p>
          </div>

          <button
            onClick={fetchData}
            disabled={loading}
            className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 shadow-xs transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-xs">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                Total Cases
              </span>
              <Users className="w-4 h-4 text-blue-500" />
            </div>
            <p className="text-2xl font-bold text-gray-900 mt-2">
              {stats.active_cases}
            </p>
            <p className="text-xs text-gray-400 mt-1">Active in system</p>
          </div>

          <div className="bg-white rounded-xl border border-amber-200 p-5 shadow-xs bg-amber-50/20">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-amber-700 uppercase tracking-wide">
                Stuck Cases
              </span>
              <AlertCircle className="w-4 h-4 text-amber-600" />
            </div>
            <p className="text-2xl font-bold text-amber-900 mt-2">
              {stats.stuck_cases}
            </p>
            <p className="text-xs text-amber-700/80 mt-1">
              Bottlenecks detected
            </p>
          </div>

          <div className="bg-white rounded-xl border border-indigo-200 p-5 shadow-xs bg-indigo-50/20">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-indigo-700 uppercase tracking-wide">
                Pending Actions
              </span>
              <Clock className="w-4 h-4 text-indigo-600" />
            </div>
            <p className="text-2xl font-bold text-indigo-900 mt-2">
              {stats.pending_actions}
            </p>
            <p className="text-xs text-indigo-700/80 mt-1">
              Awaiting human approval
            </p>
          </div>

          <div className="bg-white rounded-xl border border-red-200 p-5 shadow-xs bg-red-50/20">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-red-700 uppercase tracking-wide">
                Escalations
              </span>
              <ShieldAlert className="w-4 h-4 text-red-600" />
            </div>
            <p className="text-2xl font-bold text-red-900 mt-2">
              {stats.escalations}
            </p>
            <p className="text-xs text-red-700/80 mt-1">Urgent attention</p>
          </div>
        </div>

        {/* Controls: Search and Filters */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="relative w-full max-w-sm">
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search case, child ID, or type..."
              className="w-full pl-9 pr-4 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-900 focus:outline-hidden focus:ring-2 focus:ring-indigo-500 shadow-xs"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div className="flex flex-wrap gap-1.5 bg-white p-1 rounded-lg border border-gray-200 shadow-xs">
            {["ALL", "STUCK", "PENDING_ACTION", "ESCALATED"].map((filter) => (
              <button
                key={filter}
                onClick={() => setFilterStatus(filter)}
                className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-colors ${
                  filterStatus === filter
                    ? "bg-indigo-600 text-white"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                {filter.replace(/_/g, " ")}
              </button>
            ))}
          </div>
        </div>

        {/* Case List Grid */}
        {loading ? (
          <div className="py-16 text-center text-gray-500 flex items-center justify-center gap-2">
            <RefreshCw className="w-5 h-5 animate-spin text-indigo-600" />
            Loading referral cases...
          </div>
        ) : filteredCases.length === 0 ? (
          <div className="py-16 bg-white rounded-xl border border-dashed border-gray-200 text-center">
            <CheckCircle2 className="w-10 h-10 text-gray-300 mx-auto mb-2" />
            <p className="text-sm font-medium text-gray-600">
              No referral cases match the filter.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filteredCases.map((c) => (
              <CaseCard key={c.id} caseItem={c} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
