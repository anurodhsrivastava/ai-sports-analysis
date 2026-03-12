import { Suspense, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useTranslation } from "react-i18next";
import type { CoachingTip, CategoryBreakdown, Severity } from "../types/analysis";
import type { SportId } from "../data/sportDefinitions";
import { getGuidance, type DrillInfo } from "../data/coachingGuidance";
import { IllustrationRenderer } from "./illustrations";

const severityStyle: Record<Severity, { border: string; badge: string; badgeBg: string }> = {
  ok: { border: "border-emerald-700", badge: "text-emerald-400", badgeBg: "bg-emerald-600" },
  warning: { border: "border-amber-700", badge: "text-amber-400", badgeBg: "bg-amber-600" },
  critical: { border: "border-red-700", badge: "text-red-400", badgeBg: "bg-red-600" },
};

const difficultyStyle: Record<string, string> = {
  beginner: "bg-green-600",
  intermediate: "bg-amber-600",
  advanced: "bg-red-600",
};

function formatTimestamp(frame: number, fps: number): string {
  if (fps <= 0) return `${frame}`;
  const totalSeconds = frame / fps;
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return minutes > 0
    ? `${minutes}:${seconds.toFixed(1).padStart(4, "0")}`
    : `0:${seconds.toFixed(1).padStart(4, "0")}`;
}

// Map severity to recommended drill difficulty
const severityToDifficulty: Record<Severity, DrillInfo["difficulty"]> = {
  critical: "beginner",
  warning: "intermediate",
  ok: "advanced",
};

interface Props {
  sport: SportId;
  breakdown: CategoryBreakdown;
  tips: CoachingTip[];
  onSeek: (frame: number) => void;
  fps: number;
  coveragePercent?: number;
}

export default function ImprovementCard({ sport, breakdown, tips, onSeek, fps, coveragePercent }: Props) {
  const { t } = useTranslation();
  const [expanded, setExpanded] = useState(false);
  const [drillTab, setDrillTab] = useState<DrillInfo["difficulty"] | null>(null);
  const guidance = getGuidance(sport, breakdown.category);
  const style = severityStyle[breakdown.worst_severity];
  const worstTip = tips.reduce<CoachingTip | null>((worst, tip) => {
    if (!worst) return tip;
    const order: Record<Severity, number> = { ok: 0, warning: 1, critical: 2 };
    return order[tip.severity] > order[worst.severity] ? tip : worst;
  }, null);

  const recommendedDifficulty = severityToDifficulty[breakdown.worst_severity];
  const activeDifficulty = drillTab ?? recommendedDifficulty;
  const drills = guidance.drills;
  const activeDrill = drills?.find((d) => d.difficulty === activeDifficulty);

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
            <span className="text-xs text-slate-400">
              {t("improve.occurrences", { count: breakdown.count })}
              {coveragePercent != null && coveragePercent > 0 && (
                <span className="ml-1">({coveragePercent}% of video)</span>
              )}
            </span>
            <span
              className={`text-xs font-bold px-2 py-0.5 rounded-full text-white ${style.badgeBg}`}
            >
              {t(`severity.${breakdown.worst_severity}`)}
            </span>
          </div>
        </div>

        <p className="text-slate-300 text-sm leading-relaxed mt-2">
          {guidance.whatIsWrong}
        </p>
      </div>

      {/* Illustration */}
      <div className="px-5 pt-4">
        <div className="bg-slate-900/60 rounded-lg p-3">
          <Suspense fallback={<div className="h-32 flex items-center justify-center text-slate-500 text-sm">Loading...</div>}>
            <IllustrationRenderer sport={sport} illustrationKey={guidance.illustrationKey} />
          </Suspense>
        </div>
      </div>

      {/* How to fix */}
      <div className="px-5 pt-4">
        <div className="bg-slate-900/50 rounded-lg p-4 space-y-3">
          <h4 className="text-sm font-semibold text-white uppercase tracking-wider">
            {t("improve.howToFix")}
          </h4>
          <p className="text-slate-300 text-sm leading-relaxed">
            {guidance.howToFix}
          </p>

          {/* Drills section */}
          <div className="border-t border-slate-700 pt-3">
            {drills && drills.length > 0 ? (
              <div className="space-y-2">
                <div className="flex items-center gap-1.5">
                  {(["beginner", "intermediate", "advanced"] as const).map((diff) => {
                    const isActive = activeDifficulty === diff;
                    const isRecommended = recommendedDifficulty === diff;
                    return (
                      <button
                        key={diff}
                        type="button"
                        onClick={() => setDrillTab(diff)}
                        className={`text-[10px] px-2 py-0.5 rounded-full font-medium transition-colors ${
                          isActive
                            ? `${difficultyStyle[diff]} text-white`
                            : "bg-slate-700 text-slate-400 hover:text-slate-300"
                        }`}
                      >
                        {t(`improve.${diff}`, diff.charAt(0).toUpperCase() + diff.slice(1))}
                        {isRecommended && !isActive && " *"}
                      </button>
                    );
                  })}
                </div>
                {activeDrill && (
                  <div className="text-xs space-y-1">
                    <p className="text-slate-300 font-semibold">{activeDrill.name}</p>
                    <p className="text-slate-400">{activeDrill.description}</p>
                    <p className="text-slate-500">{t("improve.drillDuration", { duration: activeDrill.duration })}</p>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-xs text-slate-400">
                <span className="font-semibold text-slate-300">{t("improve.drill")} </span>
                {guidance.drillTip}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Stats + action row */}
      <div className="px-5 pt-4 pb-5 flex flex-wrap items-center gap-4">
        <div className="text-xs text-slate-400">
          {t("improve.yourAvg")}{" "}
          <span className={`font-semibold ${style.badge}`}>
            {breakdown.avg_angle_value}&deg;
          </span>
        </div>
        <div className="text-xs text-slate-400">
          {t("improve.idealRange")}{" "}
          <span className="font-semibold text-slate-300">{guidance.idealRange}</span>
        </div>

        {worstTip && (
          <button
            type="button"
            onClick={() => onSeek(worstTip.frame_range[0])}
            className="ml-auto text-sm text-blue-400 hover:text-blue-300 transition-colors"
          >
            {t("improve.seeInVideo")} &rarr;
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
              ? t("improve.hideDetails", { count: tips.length })
              : t("improve.showDetails", { count: tips.length })}
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
                      <div className="text-slate-300">
                        {tip.message_key
                          ? t(tip.message_key, { ...tip.message_params, defaultValue: tip.message })
                          : tip.message}
                      </div>
                      <div className="flex items-center gap-3 shrink-0 ml-3">
                        <span className="text-slate-500">
                          {tip.angle_value}&deg;
                        </span>
                        <button
                          type="button"
                          onClick={() => onSeek(tip.frame_range[0])}
                          className="text-blue-400 hover:text-blue-300"
                        >
                          {formatTimestamp(tip.frame_range[0], fps)}&ndash;{formatTimestamp(tip.frame_range[1], fps)}
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
