import React from "react";
import Link from "next/link";
import { AlertCircle, Clock, ArrowRight, UserCheck, ShieldAlert } from "lucide-react";

interface CaseCardProps {
  caseItem: {
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
  };
}

export const CaseCard: React.FC<CaseCardProps> = ({ caseItem }) => {
  const isStuck = caseItem.status === "STUCK" || Boolean(caseItem.current_bottleneck);
  const isEscalated = caseItem.status === "ESCALATED";

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-xs hover:shadow-md transition-all p-5 flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between gap-2 mb-3">
          <span className="font-mono text-xs font-semibold px-2.5 py-1 bg-gray-100 text-gray-700 rounded-md">
            {caseItem.id}
          </span>
          <div className="flex items-center gap-1.5">
            {isEscalated ? (
              <span className="inline-flex items-center gap-1 text-xs font-medium px-2.5 py-0.5 rounded-full bg-red-100 text-red-800">
                <ShieldAlert className="w-3.5 h-3.5" />
                ESCALATED
              </span>
            ) : isStuck ? (
              <span className="inline-flex items-center gap-1 text-xs font-medium px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800">
                <AlertCircle className="w-3.5 h-3.5" />
                STUCK
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 text-xs font-medium px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                <UserCheck className="w-3.5 h-3.5" />
                {caseItem.status}
              </span>
            )}
          </div>
        </div>

        <h3 className="text-base font-semibold text-gray-900 mb-1">
          Child: {caseItem.child_identifier}
        </h3>
        <p className="text-sm text-gray-500 mb-4">
          Type: <span className="font-medium text-gray-700">{caseItem.referral_type}</span>
        </p>

        {caseItem.current_bottleneck && (
          <div className="mb-4 p-3 bg-red-50 rounded-lg border border-red-100">
            <p className="text-xs font-semibold text-red-700 uppercase tracking-wide">
              Bottleneck
            </p>
            <p className="text-sm text-red-900 font-medium mt-0.5">
              {caseItem.current_bottleneck.replace(/_/g, " ")}
            </p>
          </div>
        )}

        {caseItem.recommendation && (
          <div className="mb-4 p-3 bg-indigo-50 rounded-lg border border-indigo-100">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-indigo-700 uppercase tracking-wide">
                Agent Recommended Action
              </span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 bg-indigo-200 text-indigo-800 rounded">
                {caseItem.recommendation.priority}
              </span>
            </div>
            <p className="text-sm text-indigo-950 font-medium mt-1">
              {caseItem.recommendation.recommended_action.replace(/_/g, " ")}
            </p>
          </div>
        )}
      </div>

      <div className="pt-4 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500 mt-2">
        <div className="flex items-center gap-3">
          <span className="inline-flex items-center gap-1">
            <Clock className="w-3.5 h-3.5" />
            {caseItem.days_open} days open
          </span>
          <span>{caseItem.followup_attempts} follow-ups</span>
        </div>
        <Link
          href={`/cases/${caseItem.id}`}
          className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 font-medium"
        >
          View Case
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
};
