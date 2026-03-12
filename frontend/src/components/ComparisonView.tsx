import { useMemo } from "react";
import { motion } from "framer-motion";
import { useTranslation } from "react-i18next";
import type { AnalysisResult, Severity } from "../types/analysis";
import type { SportId } from "../data/sportDefinitions";
import { getSportMeta } from "../data/sportDefinitions";
import ScoreBadge from "./ScoreBadge";

interface CompareEntry {
  result: AnalysisResult;
  date: string;
}

interface Props {
  older: CompareEntry;
  newer: CompareEntry;
  sport: SportId;
  onBack: () => void;
}

export default function ComparisonView({ older, newer, sport, onBack }: Props) {
  const { t } = useTranslation();

  const olderSummary = older.result.coaching_summary;
  const newerSummary = newer.result.coaching_summary;
  const olderScore = olderSummary?.overall_score ?? 0;
  const newerScore = newerSummary?.overall_score ?? 0;
  const scoreDelta = newerScore - olderScore;

  // Build category comparison
  const categories = useMemo(() => {
    const olderCats = new Map(
      (olderSummary?.category_breakdowns ?? []).map((c) => [c.category, c]),
    );
    const newerCats = new Map(
      (newerSummary?.category_breakdowns ?? []).map((c) => [c.category, c]),
    );
    const allKeys = new Set([...olderCats.keys(), ...newerCats.keys()]);
    return [...allKeys].map((key) => ({
      category: key,
      older: olderCats.get(key),
      newer: newerCats.get(key),
    }));
  }, [olderSummary, newerSummary]);

  // Build stat comparison
  const statComparison = useMemo(() => {
    const olderStats = older.result.keypoints_summary?.stats ?? {};
    const newerStats = newer.result.keypoints_summary?.stats ?? {};
    const allKeys = new Set([...Object.keys(olderStats), ...Object.keys(newerStats)]);
    return [...allKeys]
      .filter((k) => k !== "total_frames_analyzed" && k !== "detected_exercise")
      .map((key) => ({
        key,
        older: olderStats[key],
        newer: newerStats[key],
      }));
  }, [older.result, newer.result]);

  const formatDate = (d: string) =>
    d ? new Date(d).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" }) : "";

  const severityRank: Record<Severity, number> = { ok: 0, warning: 1, critical: 2 };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="w-full max-w-4xl mx-auto px-2 sm:px-0"
    >
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl sm:text-3xl font-bold text-white">
          {getSportMeta(sport).emoji} {t("compare.title", "Comparison")}
        </h1>
        <button
          onClick={onBack}
          className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-xs transition-colors"
        >
          {t("admin.backToApp", "Back")}
        </button>
      </div>

      {/* Score comparison */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="text-center">
          <p className="text-slate-400 text-xs mb-2">{formatDate(older.date)}</p>
          {olderSummary?.overall_grade && (
            <ScoreBadge score={olderScore} grade={olderSummary.overall_grade} size="sm" />
          )}
        </div>
        <div className="flex items-center justify-center">
          <div
            className={`text-2xl font-bold ${
              scoreDelta > 0
                ? "text-emerald-400"
                : scoreDelta < 0
                  ? "text-red-400"
                  : "text-slate-400"
            }`}
          >
            {scoreDelta > 0 && "+"}
            {scoreDelta}
          </div>
        </div>
        <div className="text-center">
          <p className="text-slate-400 text-xs mb-2">{formatDate(newer.date)}</p>
          {newerSummary?.overall_grade && (
            <ScoreBadge score={newerScore} grade={newerSummary.overall_grade} size="sm" />
          )}
        </div>
      </div>

      {/* Category comparison */}
      {categories.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-3">
            {t("compare.categories", "Category Breakdown")}
          </h3>
          <div className="space-y-2">
            {categories.map(({ category, older: o, newer: n }) => {
              const olderSev = o?.worst_severity ?? "ok";
              const newerSev = n?.worst_severity ?? "ok";
              const sevChange = severityRank[olderSev] - severityRank[newerSev];
              const angleDelta = (n?.avg_angle_value ?? 0) - (o?.avg_angle_value ?? 0);

              return (
                <div
                  key={category}
                  className="flex items-center justify-between bg-slate-800/60 rounded-lg px-4 py-3 border border-slate-700"
                >
                  <span className="text-white text-sm font-medium">{category}</span>
                  <div className="flex items-center gap-4">
                    {/* Severity change indicator */}
                    <span className="text-xs">
                      {sevChange > 0 ? (
                        <span className="text-emerald-400">{t("compare.improved", "Improved")}</span>
                      ) : sevChange < 0 ? (
                        <span className="text-red-400">{t("compare.regressed", "Regressed")}</span>
                      ) : (
                        <span className="text-slate-500">{t("compare.unchanged", "Unchanged")}</span>
                      )}
                    </span>
                    {/* Angle delta */}
                    {o && n && (
                      <span className="text-xs text-slate-400">
                        {angleDelta > 0 ? "+" : ""}
                        {angleDelta.toFixed(1)}&deg;
                      </span>
                    )}
                    {/* Count change */}
                    <span className="text-xs text-slate-500">
                      {o?.count ?? 0} &rarr; {n?.count ?? 0}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Stat comparison */}
      {statComparison.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-3">
            {t("compare.stats", "Stats Comparison")}
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {statComparison.map(({ key, older: ov, newer: nv }) => {
              const label = key
                .replace(/_/g, " ")
                .replace(/\b\w/g, (c) => c.toUpperCase());
              const oldNum = typeof ov === "number" ? ov : null;
              const newNum = typeof nv === "number" ? nv : null;
              const delta = oldNum != null && newNum != null ? newNum - oldNum : null;

              return (
                <div
                  key={key}
                  className="flex items-center justify-between bg-slate-800/60 rounded-lg px-3 py-2 border border-slate-700"
                >
                  <span className="text-slate-300 text-xs">{label}</span>
                  <div className="flex items-center gap-3 text-xs">
                    <span className="text-slate-500">{ov ?? "–"}</span>
                    <span className="text-slate-600">&rarr;</span>
                    <span className="text-white">{nv ?? "–"}</span>
                    {delta != null && (
                      <span
                        className={
                          delta > 0 ? "text-emerald-400" : delta < 0 ? "text-red-400" : "text-slate-500"
                        }
                      >
                        {delta > 0 && "+"}
                        {delta.toFixed(1)}
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </motion.div>
  );
}
