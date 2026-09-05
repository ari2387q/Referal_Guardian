"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Clock, Calendar, AlertTriangle, CheckCircle, Tag } from "lucide-react";

interface CaseEvent {
  id: string;
  case_id: string;
  event_type: string;
  details: string;
  timestamp: string;
}

interface CaseDetail {
  id: string;
  child_identifier: string;
  referral_type: string;
  status: string;
  coordinator_id: string | null;
  current_bottleneck: string | null;
  created_date: string;
  last_activity: string;
  days_open: number;
  followup_attempts: number;
  events: CaseEvent[];
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function CaseDetailPage() {
  const params = useParams();
  const id = params?.id as string;

  const [caseData, setCaseData] = useState<CaseDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    async function fetchCase() {
      try {
        setLoading(true);
        const res = await fetch(`${API_BASE}/api/cases/${id}`);
        if (!res.ok) {
          if (res.status === 404) {
            throw new Error(`Case ${id} not found.`);
          }
          throw new Error("Failed to fetch case details.");
        }
        const data: CaseDetail = await res.json();
        setCaseData(data);
        setError(null);
      } catch (err: any) {
        setError(err.message || "An unexpected error occurred.");
      } finally {
        setLoading(false);
      }
    }

    fetchCase();
  }, [id]);

  const formatDate = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Back navigation */}
      <div>
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 text-sm font-medium text-indigo-600 hover:text-indigo-800 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Cases
        </Link>
      </div>

      {loading && (
        <div className="bg-white p-8 rounded-xl border border-slate-200 text-center text-slate-500 shadow-sm">
          Loading case information...
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-sm">
          <strong>Error:</strong> {error}
        </div>
      )}

      {caseData && !loading && (
        <>
          {/* Header Card */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-5">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                    {caseData.id}
                  </span>
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      caseData.status === "ACTIVE"
                        ? "bg-indigo-100 text-indigo-800"
                        : caseData.status === "NEW"
                        ? "bg-slate-100 text-slate-800"
                        : "bg-emerald-100 text-emerald-800"
                    }`}
                  >
                    {caseData.status}
                  </span>
                </div>
                <h2 className="text-2xl font-bold text-slate-900 mt-2">
                  Child ID: {caseData.child_identifier}
                </h2>
                <p className="text-sm font-medium text-slate-600 mt-1 flex items-center gap-1.5">
                  <Tag className="w-4 h-4 text-slate-400" />
                  {caseData.referral_type}
                </p>
              </div>

              {/* Quick stats on case */}
              <div className="flex sm:flex-col items-end gap-1.5 bg-slate-50 sm:bg-transparent p-3 sm:p-0 rounded-lg">
                <div className="flex items-center gap-1 text-sm font-medium text-slate-700">
                  <Clock className="w-4 h-4 text-slate-400" />
                  <span>Days Open:</span>
                  <span className="font-bold text-slate-900">{caseData.days_open}</span>
                </div>
                <div className="text-xs text-slate-500">
                  Follow-up Attempts: {caseData.followup_attempts}
                </div>
              </div>
            </div>

            {/* Bottleneck alert if present */}
            {caseData.current_bottleneck && (
              <div className="mt-4 flex items-center gap-2.5 bg-amber-50 border border-amber-200 text-amber-800 text-xs sm:text-sm px-3.5 py-2.5 rounded-lg">
                <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                <div>
                  <span className="font-semibold">Current Bottleneck:</span>{" "}
                  <span className="font-mono">{caseData.current_bottleneck}</span>
                </div>
              </div>
            )}
          </div>

          {/* Vertical Timeline */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
            <h3 className="text-base font-semibold text-slate-900 mb-6">
              Activity & Event Timeline
            </h3>

            {caseData.events.length === 0 ? (
              <p className="text-sm text-slate-400 italic">No recorded events yet for this case.</p>
            ) : (
              <div className="relative pl-6 border-l-2 border-slate-200 space-y-8 ml-2">
                {caseData.events.map((event, index) => (
                  <div key={event.id} className="relative group">
                    {/* Timeline Node Point */}
                    <div className="absolute -left-[31px] top-1 w-4 h-4 rounded-full bg-white border-2 border-indigo-600 group-hover:scale-110 transition-transform" />

                    <div className="space-y-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-mono text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-800">
                          {event.event_type}
                        </span>
                        <span className="text-xs text-slate-400 flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {formatDate(event.timestamp)}
                        </span>
                      </div>
                      <p className="text-sm text-slate-700 font-medium pt-0.5">
                        {event.details}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
