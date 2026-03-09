import { Suspense, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { CoachingTip, CategoryBreakdown, Severity } from "../types/analysis";
import type { SportId } from "../data/sportDefinitions";
import { getGuidance } from "../data/coachingGuidance";
import { getIllustration } from "./illustrations";

const severityStyle: Record<Severity, { border: string; badge: string; badgeBg: string }> = {
  ok: { border: "border-emerald-700", badge: "text-emerald-400", badgeBg: "bg-emerald-600" },
  warning: { border: "border-amber-700", badge: "text-amber-400", badgeBg: "bg-amber-600" },
  critical: { border: "border-red-700", badge: "text-red-400", badgeBg: "bg-red-600" },
};

const severityLabel: Record<Severity, string> = {
  ok: "OK",
  warning: "Warning",
  critical: "Critical",
};

interface Props {
  sport: SportId;
  breakdown: CategoryBreakdown;
  tips: CoachingTip[];
  onSeek: (frame: number) => void;
}

export default function ImprovementCard({ sport, breakdown, tips, onSeek }: Props) {
  const [expanded, setExpanded] = useState(false);
  const guidance = getGuidance(sport, breakdown.category);
  const style = severityStyle[breakdown.worst_severity];
  const Illustration = getIllustration(sport, guidance.illustrationKey);

  const worstTip = tips.reduce<CoachingTip | null>((worst, tip) => {
    if (!worst) return tip;
    const order: Record<Severity, number> = { ok: 0, warning: 1, critical: 2 };
    return order[tip.severity] > order[worst.severity] ? tip : worst;
  }, null);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className={`rounded-xl border ${style.border} bg-slate-800/60 overflow-hidden`}
    >
      {/* Header */}
      <div className="p-5 pb-0">
        <div className="flex items-start justify-between mb-1">
          <h3 className="text-lg font-semibold text-white">{guidance.title}</h3>
          <div className="flex items-center gap-2 shrink-0 ml-3">
            <span className="text-xs text-slate-400">{breakdown.count} occurrences</span>
            <span
              className={`text-xs font-bold px-2 py-0.5 rounded-full text-white ${style.badgeBg}`}
            >
              {severityLabel[breakdown.worst_severity]}
            </span>
          </div>
        </div>

        <p className="text-slate-300 text-sm leading-relaxed mt-2">
          {guidance.whatIsWrong}
        </p>
      </div>

      {/* Illustration */}
      {Illustration && (
        <div className="px-5 pt-4">
          <div className="bg-slate-900/60 rounded-lg p-3">
            <Suspense fallback={<div className="h-32 flex items-center justify-center text-slate-500 text-sm">Loading...</div>}>
              <Illustration />
            </Suspense>
          </div>
        </div>
      )}

      {/* How to fix */}
      <div className="px-5 pt-4">
        <div className="bg-slate-900/50 rounded-lg p-4 space-y-3">
          <h4 className="text-sm font-semibold text-white uppercase tracking-wider">
            How to Fix It
          </h4>
          <p className="text-slate-300 text-sm leading-relaxed">
            {guidance.howToFix}
          </p>
          <div className="border-t border-slate-700 pt-3">
            <p className="text-xs text-slate-400">
              <span className="font-semibold text-slate-300">Drill: </span>
              {guidance.drillTip}
            </p>
          </div>
        </div>
      </div>

      {/* Stats + action row */}
      <div className="px-5 pt-4 pb-5 flex flex-wrap items-center gap-4">
        <div className="text-xs text-slate-400">
          Your avg:{" "}
          <span className={`font-semibold ${style.badge}`}>
            {breakdown.avg_angle_value}&deg;
          </span>
        </div>
        <div className="text-xs text-slate-400">
          Ideal range:{" "}
          <span className="font-semibold text-slate-300">{guidance.idealRange}</span>
        </div>

        {worstTip && (
          <button
            type="button"
            onClick={() => onSeek(worstTip.frame_range[0])}
            className="ml-auto text-sm text-blue-400 hover:text-blue-300 transition-colors"
          >
            See it in your video &rarr;
          </button>
        )}
      </div>

      {/* Expandable per-frame details */}
      {tips.length > 0 && (
        <div className="border-t border-slate-700">
          <button
            type="button"
            onClick={() => setExpanded((v) => !v)}
            className="w-full px-5 py-3 text-left text-sm text-slate-400 hover:text-slate-300 transition-colors"
          >
            {expanded
              ? `Hide ${tips.length} detailed occurrences`
              : `Show ${tips.length} detailed occurrences`}
          </button>

          <AnimatePresence>
            {expanded && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <div className="px-5 pb-4 space-y-2">
                  {tips.map((tip, i) => (
                    <div
                      key={`${tip.frame_range[0]}-${i}`}
                      className="flex items-center justify-between bg-slate-900/40 rounded-lg px-3 py-2 text-xs"
                    >
                      <div className="text-slate-300">{tip.message}</div>
                      <div className="flex items-center gap-3 shrink-0 ml-3">
                        <span className="text-slate-500">
                          {tip.angle_value}&deg;
                        </span>
                        <button
                          type="button"
                          onClick={() => onSeek(tip.frame_range[0])}
                          className="text-blue-400 hover:text-blue-300"
                        >
                          Frame {tip.frame_range[0]}&ndash;{tip.frame_range[1]}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}
    </motion.div>
  );
}
