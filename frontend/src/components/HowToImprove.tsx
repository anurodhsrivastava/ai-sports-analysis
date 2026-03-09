import { useMemo } from "react";
import type {
  CoachingTip,
  CoachingSummary,
  Severity,
} from "../types/analysis";
import type { SportId } from "../data/sportDefinitions";
import ImprovementCard from "./ImprovementCard";

const severityOrder: Record<Severity, number> = {
  critical: 0,
  warning: 1,
  ok: 2,
};

interface Props {
  sport: SportId;
  coachingSummary: CoachingSummary;
  coachingTips: CoachingTip[];
  onSeek: (frame: number) => void;
}

export default function HowToImprove({
  sport,
  coachingSummary,
  coachingTips,
  onSeek,
}: Props) {
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

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-white">How to Improve</h2>
        <p className="text-slate-400 text-sm mt-1">
          {coachingSummary.overall_assessment}
        </p>
      </div>

      {breakdowns.map((breakdown) => (
        <ImprovementCard
          key={breakdown.category}
          sport={sport}
          breakdown={breakdown}
          tips={tipsByCategory[breakdown.category] ?? []}
          onSeek={onSeek}
        />
      ))}
    </div>
  );
}
