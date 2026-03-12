import { useMemo } from "react";
import { useTranslation } from "react-i18next";
import type {
  CoachingTip,
  CoachingSummary,
  Severity,
} from "../types/analysis";
import type { SportId } from "../data/sportDefinitions";
import ImprovementCard from "./ImprovementCard";
import ScoreBadge from "./ScoreBadge";

const severityOrder: Record<Severity, number> = {
  critical: 0,
  warning: 1,
  ok: 2,
};

const severityBadgeStyle: Record<Severity, string> = {
  critical: "bg-red-600",
  warning: "bg-amber-600",
  ok: "bg-emerald-600",
};

interface Props {
  sport: SportId;
  coachingSummary: CoachingSummary;
  coachingTips: CoachingTip[];
  onSeek: (frame: number) => void;
  fps: number;
  totalFrames: number;
}

function formatTimestamp(frame: number, fps: number): string {
  if (fps <= 0) return `${frame}`;
  const totalSeconds = frame / fps;
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return minutes > 0
    ? `${minutes}:${seconds.toFixed(1).padStart(4, "0")}`
    : `0:${seconds.toFixed(1).padStart(4, "0")}`;
}

export default function HowToImprove({
  sport,
  coachingSummary,
  coachingTips,
  onSeek,
  fps,
  totalFrames,
}: Props) {
  const { t } = useTranslation();

  const breakdowns = useMemo(
    () =>
      [...coachingSummary.category_breakdowns].sort(
        (a, b) => severityOrder[a.worst_severity] - severityOrder[b.worst_severity]
      ),
    [coachingSummary.category_breakdowns]
  );

  const tipsByCategory = useMemo(() => {
    const grouped: Record<string, CoachingTip[]> = {};
    for (const tip of coachingTips) {
      (grouped[tip.category] ??= []).push(tip);
    }
    return grouped;
  }, [coachingTips]);

  const topTips = coachingSummary.top_tips?.slice(0, 5) ?? [];

  // Compute coverage per category
  const coverageByCategory = useMemo(() => {
    if (totalFrames <= 0) return {};
    const result: Record<string, number> = {};
    for (const [cat, tips] of Object.entries(tipsByCategory)) {
      const totalSpan = tips.reduce(
        (sum, tip) => sum + Math.max(0, tip.frame_range[1] - tip.frame_range[0]),
        0
      );
      result[cat] = Math.round((totalSpan / totalFrames) * 100);
    }
    return result;
  }, [tipsByCategory, totalFrames]);

  return (
    <div className="space-y-4">
      {/* Score Badge */}
      {coachingSummary.overall_score != null && coachingSummary.overall_grade && (
        <div className="flex justify-center py-2">
          <ScoreBadge
            score={coachingSummary.overall_score}
            grade={coachingSummary.overall_grade}
          />
        </div>
      )}

      <div>
        <h2 className="text-lg font-semibold text-white">{t("improve.title")}</h2>
        <p className="text-slate-400 text-sm mt-1">
          {coachingSummary.overall_assessment}
        </p>
      </div>

      {/* Top Tips - Focus on These First */}
      {topTips.length > 0 && (
        <div className="bg-slate-800/60 rounded-xl border border-slate-700 p-4 space-y-2">
          <h3 className="text-sm font-semibold text-white uppercase tracking-wider">
            {t("improve.focusFirst", "Focus on These First")}
          </h3>
          {topTips.map((tip, i) => (
            <div
              key={`top-${tip.frame_range[0]}-${i}`}
              className="flex items-start gap-3 bg-slate-900/40 rounded-lg px-3 py-2"
            >
              <span
                className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full text-white shrink-0 mt-0.5 ${severityBadgeStyle[tip.severity]}`}
              >
                {t(`severity.${tip.severity}`)}
              </span>
              <p className="text-slate-300 text-sm flex-1">{tip.message}</p>
              <button
                type="button"
                onClick={() => onSeek(tip.frame_range[0])}
                className="text-xs text-blue-400 hover:text-blue-300 shrink-0"
              >
                {formatTimestamp(tip.frame_range[0], fps)}
              </button>
            </div>
          ))}
        </div>
      )}

      {breakdowns.map((breakdown) => (
        <ImprovementCard
          key={breakdown.category}
          sport={sport}
          breakdown={breakdown}
          tips={tipsByCategory[breakdown.category] ?? []}
          onSeek={onSeek}
          fps={fps}
          coveragePercent={coverageByCategory[breakdown.category]}
        />
      ))}
    </div>
  );
}
