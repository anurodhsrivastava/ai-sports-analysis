import { useCallback, useRef } from "react";
import { motion } from "framer-motion";
import type { AnalysisResult } from "../types/analysis";
import type { SportId } from "../data/sportDefinitions";
import VideoPlayer, { type VideoPlayerHandle } from "./VideoPlayer";
import HowToImprove from "./HowToImprove";

interface Props {
  result: AnalysisResult;
  sport: SportId;
  onReset: () => void;
}

export default function ResultsView({ result, sport, onReset }: Props) {
  const {
    coaching_tips,
    video_url,
    keypoints_summary,
    coaching_summary,
    video_fps,
  } = result;

  const videoRef = useRef<VideoPlayerHandle>(null);

  const fps = video_fps ?? 30;

  const handleSeekToFrame = useCallback(
    (frameIndex: number) => {
      videoRef.current?.seekTo(frameIndex / fps);
    },
    [fps]
  );

  const categoryCount = coaching_summary?.category_breakdowns.length ?? 0;

  // Build stat cards from the sport-specific stats dictionary
  const stats = keypoints_summary?.stats ?? {};
  const statEntries = Object.entries(stats).filter(
    ([, v]) => v !== null && v !== undefined
  );

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="w-full max-w-6xl mx-auto"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-white">Analysis Results</h1>
          <p className="text-slate-400 mt-1">
            {categoryCount > 0
              ? `${categoryCount} area${categoryCount !== 1 ? "s" : ""} to improve`
              : "Looking good!"}
          </p>
        </div>
        <button
          onClick={onReset}
          className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors text-sm"
        >
          Analyze Another Video
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Video */}
        <div className="space-y-4">
          {video_url && <VideoPlayer ref={videoRef} videoUrl={video_url} />}

          {/* Summary stats - dynamically rendered */}
          {statEntries.length > 0 && (
            <div className={`grid gap-3 ${statEntries.length <= 3 ? `grid-cols-${statEntries.length}` : "grid-cols-3"}`}>
              {statEntries.map(([key, value]) => (
                <StatCard
                  key={key}
                  label={formatStatLabel(key)}
                  value={formatStatValue(value, key)}
                />
              ))}
            </div>
          )}
        </div>

        {/* Right: Coaching section */}
        <div className="space-y-4">
          {coaching_summary && coaching_summary.category_breakdowns.length > 0 ? (
            <HowToImprove
              sport={sport}
              coachingSummary={coaching_summary}
              coachingTips={coaching_tips}
              onSeek={handleSeekToFrame}
            />
          ) : coaching_tips.length === 0 ? (
            <div className="text-center py-12 text-slate-400">
              <div className="text-4xl mb-3">&#10003;</div>
              <p className="text-lg font-medium text-white">Looking good!</p>
              <p>No major technique issues detected.</p>
            </div>
          ) : null}
        </div>
      </div>
    </motion.div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-slate-800 rounded-lg p-3 text-center">
      <div className="text-lg font-bold text-white">{value}</div>
      <div className="text-xs text-slate-400">{label}</div>
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
