import { useCallback, useRef } from "react";
import { motion } from "framer-motion";
import { useTranslation } from "react-i18next";
import type { AnalysisResult, User } from "../types/analysis";
import type { SportId } from "../data/sportDefinitions";
import { getStatTarget } from "../data/statTargets";
import VideoPlayer, { type VideoPlayerHandle } from "./VideoPlayer";
import HowToImprove from "./HowToImprove";

interface Props {
  result: AnalysisResult;
  sport: SportId;
  onReset: () => void;
  user: User | null;
  onLoginPrompt: () => void;
  onSaveResults?: () => void;
}

export default function ResultsView({ result, sport, onReset, user, onLoginPrompt, onSaveResults }: Props) {
  const { t } = useTranslation();
  const {
    coaching_tips,
    video_url,
    keypoints_summary,
    coaching_summary,
    video_fps,
    sport_mismatch,
  } = result;

  const videoRef = useRef<VideoPlayerHandle>(null);
  const fps = video_fps ?? 30;

  const handleSeekToFrame = useCallback(
    (frameIndex: number) => {
      videoRef.current?.seekTo(frameIndex / fps);
    },
    [fps],
  );

  const categoryCount = coaching_summary?.category_breakdowns.length ?? 0;

  // Build stat cards from the sport-specific stats dictionary
  const stats = keypoints_summary?.stats ?? {};
  const statEntries = Object.entries(stats).filter(
    ([, v]) => v !== null && v !== undefined
  );

  const totalFrames = Number(stats.total_frames_analyzed) || 0;

  // Mismatch-only screen
  if (sport_mismatch && !video_url && coaching_tips.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="w-full max-w-2xl mx-auto px-2 sm:px-0"
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="rounded-2xl border border-amber-500/40 bg-gradient-to-b from-amber-900/40 to-slate-900/80 p-6 sm:p-10 text-center"
        >
          <div className="text-amber-400 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
            </svg>
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-white mb-3">
            {t("results.wrongVideo")}
          </h2>
          <p className="text-amber-200/80 text-base sm:text-lg mb-2">
            {sport_mismatch.message}
          </p>
          <p className="text-slate-400 text-sm mb-8">
            {t("results.wrongVideoDesc")}
          </p>
          <button
            onClick={onReset}
            className="px-6 py-3 bg-amber-600 hover:bg-amber-500 text-white rounded-xl transition-colors text-base font-semibold shadow-lg shadow-amber-900/30"
          >
            {t("results.uploadCorrect")}
          </button>
        </motion.div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="w-full max-w-6xl mx-auto px-2 sm:px-0"
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 sm:mb-6 gap-3">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white">
            {t("results.title")}
          </h1>
          <p className="text-slate-400 mt-1 text-sm sm:text-base">
            {categoryCount > 0
              ? t("results.areasToImprove", { count: categoryCount })
              : t("results.lookingGood")}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {!user ? (
            <button
              onClick={onLoginPrompt}
              className="px-3 py-2 sm:px-4 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors text-xs sm:text-sm font-medium"
            >
              {t("results.saveResults")}
            </button>
          ) : onSaveResults ? (
            <button
              onClick={onSaveResults}
              className="px-3 py-2 sm:px-4 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors text-xs sm:text-sm font-medium"
            >
              {t("results.saveResults")}
            </button>
          ) : null}
          <button
            onClick={onReset}
            className="px-3 py-2 sm:px-4 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors text-xs sm:text-sm"
          >
            {t("results.analyzeAnother")}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        {/* Left: Video */}
        <div className="space-y-3 sm:space-y-4">
          {video_url && <VideoPlayer ref={videoRef} videoUrl={video_url} />}

          {/* Summary stats - dynamically rendered */}
          {statEntries.length > 0 && (
            <div className={`grid gap-2 sm:gap-3 ${statEntries.length <= 3 ? `grid-cols-${statEntries.length}` : "grid-cols-3"}`}>
              {statEntries.map(([key, value]) => {
                const target = getStatTarget(sport, key);
                return (
                  <StatCard
                    key={key}
                    label={formatStatLabel(key)}
                    value={formatStatValue(value, key)}
                    target={target ? `${target.min}–${target.max}${target.unit ? " " + target.unit : ""}` : undefined}
                    inRange={target && typeof value === "number" ? getStatStatus(value, target.min, target.max) : undefined}
                  />
                );
              })}
            </div>
          )}
        </div>

        {/* Right: Coaching section */}
        <div className="space-y-3 sm:space-y-4">
          {coaching_summary && coaching_summary.category_breakdowns.length > 0 ? (
            <HowToImprove
              sport={sport}
              coachingSummary={coaching_summary}
              coachingTips={coaching_tips}
              onSeek={handleSeekToFrame}
              fps={fps}
              totalFrames={totalFrames}
            />
          ) : coaching_tips.length === 0 ? (
            <div className="text-center py-8 sm:py-12 text-slate-400">
              <div className="text-4xl mb-3">&#10003;</div>
              <p className="text-lg font-medium text-white">{t("results.lookingGood")}</p>
              <p>{t("results.noIssues")}</p>
            </div>
          ) : null}
        </div>
      </div>
    </motion.div>
  );
}

type StatStatus = "in" | "near" | "out";

function getStatStatus(value: number, min: number, max: number): StatStatus {
  if (value >= min && value <= max) return "in";
  const range = max - min;
  const tolerance = range * 0.15;
  if (value >= min - tolerance && value <= max + tolerance) return "near";
  return "out";
}

const statStatusColor: Record<StatStatus, string> = {
  in: "text-emerald-400",
  near: "text-amber-400",
  out: "text-white",
};

function StatCard({
  label,
  value,
  target,
  inRange,
}: {
  label: string;
  value: string;
  target?: string;
  inRange?: StatStatus;
}) {
  const valueColor = inRange ? statStatusColor[inRange] : "text-white";
  return (
    <div className="bg-slate-800 rounded-lg p-2.5 sm:p-3 text-center">
      <div className={`text-base sm:text-lg font-bold ${valueColor}`}>{value}</div>
      <div className="text-[10px] sm:text-xs text-slate-400">{label}</div>
      {target && (
        <div className="text-[9px] sm:text-[10px] text-slate-500 mt-0.5">
          target: {target}
        </div>
      )}
    </div>
  );
}

function formatStatLabel(key: string): string {
  return key
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase())
    .replace("Avg ", "Avg. ")
    .replace("Spm", "SPM");
}

// Keys whose values are percentages or scores, not angles
const NON_ANGLE_KEYS = new Set([
  "total_frames_analyzed",
  "balance_score",
  "symmetry_score",
  "head_stability",
  "detected_exercise",
  "rep_count",
]);

function formatStatValue(value: number | string | null, key?: string): string {
  if (value === null || value === undefined) return "N/A";
  if (typeof value === "string") return value;
  if (Number.isInteger(value)) return value.toString();
  if (key && NON_ANGLE_KEYS.has(key)) return value.toFixed(1);
  return `${value}\u00b0`;
}
