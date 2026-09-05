import React from "react";
import {
  CheckCircle2,
  AlertTriangle,
  FileText,
  PhoneCall,
  UserX,
  Clock,
  Zap,
  ShieldCheck,
  RotateCcw,
  Sparkles,
} from "lucide-react";

export interface TimelineEvent {
  id: string;
  event_type: string;
  details?: string | null;
  timestamp?: string | null;
}

interface TimelineProps {
  events: TimelineEvent[];
}

export const Timeline: React.FC<TimelineProps> = ({ events }) => {
  if (!events || events.length === 0) {
    return (
      <div className="py-8 text-center text-sm text-gray-500 bg-gray-50 rounded-xl border border-dashed border-gray-200">
        No timeline events recorded yet.
      </div>
    );
  }

  const getEventBadge = (type: string) => {
    switch (type) {
      case "AGENT_OBSERVED_CASE":
        return {
          icon: <Sparkles className="w-4 h-4 text-purple-600" />,
          bg: "bg-purple-50 border-purple-200 text-purple-700",
        };
      case "BOTTLENECK_DETECTED":
        return {
          icon: <AlertTriangle className="w-4 h-4 text-amber-600" />,
          bg: "bg-amber-50 border-amber-200 text-amber-800",
        };
      case "RECOMMENDATION_CREATED":
        return {
          icon: <Zap className="w-4 h-4 text-indigo-600" />,
          bg: "bg-indigo-50 border-indigo-200 text-indigo-800",
        };
      case "RECOMMENDATION_APPROVED":
      case "OUTCOME_VERIFIED":
        return {
          icon: <CheckCircle2 className="w-4 h-4 text-emerald-600" />,
          bg: "bg-emerald-50 border-emerald-200 text-emerald-800",
        };
      case "RECOMMENDATION_REJECTED":
      case "OUTCOME_FAILED":
        return {
          icon: <AlertTriangle className="w-4 h-4 text-red-600" />,
          bg: "bg-red-50 border-red-200 text-red-800",
        };
      case "SPECIALIST_UNAVAILABLE":
        return {
          icon: <UserX className="w-4 h-4 text-red-600" />,
          bg: "bg-red-50 border-red-200 text-red-800",
        };
      case "DOCUMENT_REQUESTED":
      case "DOCUMENT_RECEIVED":
        return {
          icon: <FileText className="w-4 h-4 text-blue-600" />,
          bg: "bg-blue-50 border-blue-200 text-blue-800",
        };
      case "SPECIALIST_CONTACTED":
      case "PARENT_CONTACTED":
        return {
          icon: <PhoneCall className="w-4 h-4 text-teal-600" />,
          bg: "bg-teal-50 border-teal-200 text-teal-800",
        };
      case "FOLLOWUP_SCHEDULED":
      case "FOLLOWUP_SENT":
        return {
          icon: <Clock className="w-4 h-4 text-sky-600" />,
          bg: "bg-sky-50 border-sky-200 text-sky-800",
        };
      case "CASE_ESCALATED":
        return {
          icon: <ShieldCheck className="w-4 h-4 text-rose-600" />,
          bg: "bg-rose-50 border-rose-200 text-rose-800",
        };
      default:
        return {
          icon: <RotateCcw className="w-4 h-4 text-gray-500" />,
          bg: "bg-gray-50 border-gray-200 text-gray-700",
        };
    }
  };

  return (
    <div className="relative pl-6 space-y-6 before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-0.5 before:bg-gray-200">
      {events.map((evt) => {
        const badge = getEventBadge(evt.event_type);
        const formattedDate = evt.timestamp
          ? new Date(evt.timestamp).toLocaleString(undefined, {
              dateStyle: "medium",
              timeStyle: "short",
            })
          : "N/A";

        return (
          <div key={evt.id} className="relative group">
            <div className="absolute -left-[23px] top-1 w-6 h-6 rounded-full bg-white border border-gray-200 shadow-xs flex items-center justify-center">
              {badge.icon}
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-3 shadow-xs">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span
                  className={`inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded border ${badge.bg}`}
                >
                  {evt.event_type.replace(/_/g, " ")}
                </span>
                <span className="text-xs text-gray-400 font-mono">
                  {formattedDate}
                </span>
              </div>
              {evt.details && (
                <p className="mt-2 text-sm text-gray-700 leading-relaxed break-words bg-gray-50 p-2 rounded border border-gray-100 font-mono text-xs">
                  {evt.details}
                </p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};
