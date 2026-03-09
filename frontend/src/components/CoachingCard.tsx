import { motion } from "framer-motion";
import type { CoachingTip, Severity } from "../types/analysis";

const severityConfig: Record<
  Severity,
  { bg: string; border: string; badge: string; label: string }
> = {
  ok: {
    bg: "bg-emerald-900/30",
    border: "border-emerald-700",
    badge: "bg-emerald-600",
    label: "Good",
  },
  warning: {
    bg: "bg-amber-900/30",
    border: "border-amber-700",
    badge: "bg-amber-600",
    label: "Needs Work",
  },
  critical: {
    bg: "bg-red-900/30",
    border: "border-red-700",
    badge: "bg-red-600",
    label: "Fix This",
  },
};

interface Props {
  tip: CoachingTip;
  index: number;
  onSeek?: (frameStart: number) => void;
}

export default function CoachingCard({ tip, index, onSeek }: Props) {
  const config = severityConfig[tip.severity];

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1 }}
      className={`rounded-xl border p-4 ${config.bg} ${config.border}`}
    >
      <div className="flex items-start justify-between mb-2">
        <div>
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
            {tip.category}
          </span>
          <h3 className="text-white font-semibold">{tip.body_part}</h3>
        </div>
        <span
          className={`text-xs font-bold px-2 py-1 rounded-full text-white ${config.badge}`}
        >
          {config.label}
        </span>
      </div>

      <p className="text-slate-300 text-sm leading-relaxed mb-3">
        {tip.message}
      </p>

      <div className="flex gap-4 text-xs text-slate-500">
        <span>
          Angle: <span className="text-slate-300">{tip.angle_value}&deg;</span>
        </span>
        <span>
          Threshold:{" "}
          <span className="text-slate-300">{tip.threshold}&deg;</span>
        </span>
        <span>
          Frames:{" "}
          {onSeek ? (
            <button
              type="button"
              onClick={() => onSeek(tip.frame_range[0])}
              className="text-blue-400 hover:text-blue-300 underline cursor-pointer"
            >
              {tip.frame_range[0]}&ndash;{tip.frame_range[1]}
            </button>
          ) : (
            <span className="text-slate-300">
              {tip.frame_range[0]}&ndash;{tip.frame_range[1]}
            </span>
          )}
        </span>
      </div>
    </motion.div>
  );
}
