import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useTranslation } from "react-i18next";
import type { AnalysisResult, ProgressEntry, SavedVideo, User } from "../types/analysis";
import type { SportId } from "../data/sportDefinitions";
import { SPORTS, getSportMeta } from "../data/sportDefinitions";
import { deleteMyVideo, getMyVideoDetail, getMyVideos, getProgress } from "../services/api";
import ScoreBadge from "../components/ScoreBadge";
import ProgressChart from "../components/ProgressChart";

interface Props {
  user: User;
  onBack: () => void;
  onViewResult: (result: AnalysisResult, sport: SportId) => void;
  onCompare?: (items: [CompareItem, CompareItem]) => void;
}

export interface CompareItem {
  result: AnalysisResult;
  date: string;
}

export default function MyVideos({ user, onBack, onViewResult, onCompare }: Props) {
  const { t } = useTranslation();
  const [videos, setVideos] = useState<SavedVideo[]>([]);
  const [progress, setProgress] = useState<ProgressEntry[]>([]);
  const [activeSport, setActiveSport] = useState<SportId | "all">("all");
  const [loading, setLoading] = useState(true);
  const [compareMode, setCompareMode] = useState(false);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [comparingLoader, setComparingLoader] = useState(false);

  useEffect(() => {
    setLoading(true);
    Promise.all([getMyVideos(), getProgress()])
      .then(([v, p]) => {
        setVideos(v);
        setProgress(p);
      })
      .finally(() => setLoading(false));
  }, []);

  const sportTabs = useMemo(() => {
    const sportsInUse = new Set(videos.map((v) => v.sport));
    return SPORTS.filter((s) => sportsInUse.has(s.id));
  }, [videos]);

  const filtered = useMemo(
    () => activeSport === "all" ? videos : videos.filter((v) => v.sport === activeSport),
    [videos, activeSport],
  );

  // Build score/grade map from progress entries
  const scoreMap = useMemo(() => {
    const m: Record<string, { score: number | null; grade: string | null }> = {};
    for (const p of progress) {
      m[p.task_id] = { score: p.score, grade: p.grade };
    }
    return m;
  }, [progress]);

  const handleDelete = async (id: string) => {
    if (!confirm(t("myVideos.deleteConfirm", "Delete this analysis?"))) return;
    await deleteMyVideo(id);
    setVideos((prev) => prev.filter((v) => v.id !== id));
  };

  const handleView = async (video: SavedVideo) => {
    const detail = await getMyVideoDetail(video.id);
    if (detail.result) {
      onViewResult(detail.result, video.sport as SportId);
    }
  };

  const toggleSelect = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else if (next.size < 2) next.add(id);
      return next;
    });
  };

  const handleCompare = async () => {
    if (selected.size !== 2 || !onCompare) return;
    setComparingLoader(true);
    try {
      const ids = [...selected];
      const [a, b] = await Promise.all(ids.map((id) => getMyVideoDetail(id)));
      if (a.result && b.result) {
        const itemA: CompareItem = { result: a.result, date: a.created_at ?? "" };
        const itemB: CompareItem = { result: b.result, date: b.created_at ?? "" };
        // Ensure older first
        const ordered: [CompareItem, CompareItem] = itemA.date <= itemB.date
          ? [itemA, itemB]
          : [itemB, itemA];
        onCompare(ordered);
      }
    } finally {
      setComparingLoader(false);
    }
  };

  // Check if all selected are same sport
  const selectedSameSport = useMemo(() => {
    if (selected.size < 2) return true;
    const sports = [...selected].map((id) => videos.find((v) => v.id === id)?.sport);
    return sports[0] === sports[1];
  }, [selected, videos]);

  const isPro = user.tier === "pro";

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="w-full max-w-4xl mx-auto px-2 sm:px-0"
    >
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl sm:text-3xl font-bold text-white">
          {t("myVideos.title", "My Videos")}
        </h1>
        <div className="flex items-center gap-2">
          {onCompare && (
            <button
              onClick={() => {
                setCompareMode((v) => !v);
                setSelected(new Set());
              }}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                compareMode
                  ? "bg-cyan-600 text-white"
                  : "bg-slate-700 text-slate-300 hover:bg-slate-600"
              }`}
            >
              {compareMode ? t("compare.cancel", "Cancel") : t("compare.toggle", "Compare")}
            </button>
          )}
          <button
            onClick={onBack}
            className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-xs transition-colors"
          >
            {t("admin.backToApp", "Back")}
          </button>
        </div>
      </div>

      {/* Progress Chart */}
      {activeSport !== "all" && progress.length >= 2 && (
        <div className="mb-6 bg-slate-800/60 rounded-xl border border-slate-700 p-4">
          <h3 className="text-sm font-semibold text-white mb-2">
            {t("myVideos.scoreOverTime", "Score Over Time")}
          </h3>
          <ProgressChart entries={progress} sport={activeSport} isPro={isPro} />
        </div>
      )}

      {/* Sport tabs */}
      {sportTabs.length > 1 && (
        <div className="flex gap-2 mb-4 overflow-x-auto pb-1">
          <button
            onClick={() => setActiveSport("all")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors shrink-0 ${
              activeSport === "all"
                ? "bg-cyan-600 text-white"
                : "bg-slate-700 text-slate-300 hover:bg-slate-600"
            }`}
          >
            All
          </button>
          {sportTabs.map((s) => (
            <button
              key={s.id}
              onClick={() => setActiveSport(s.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors shrink-0 ${
                activeSport === s.id
                  ? "bg-cyan-600 text-white"
                  : "bg-slate-700 text-slate-300 hover:bg-slate-600"
              }`}
            >
              {s.emoji} {s.name}
            </button>
          ))}
        </div>
      )}

      {/* Compare action bar */}
      {compareMode && selected.size === 2 && (
        <div className="mb-4 flex items-center gap-3">
          <button
            onClick={handleCompare}
            disabled={!selectedSameSport || comparingLoader}
            className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-600 disabled:text-slate-400 text-white rounded-lg text-sm font-medium transition-colors"
          >
            {comparingLoader ? "Loading..." : t("compare.title", "Compare")}
          </button>
          {!selectedSameSport && (
            <span className="text-xs text-amber-400">
              {t("compare.sameSportOnly", "Select two analyses of the same sport")}
            </span>
          )}
        </div>
      )}

      {loading ? (
        <div className="text-slate-400 text-center py-12">Loading...</div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-12 text-slate-400">
          <div className="text-4xl mb-3">&#128249;</div>
          <p>{t("myVideos.noVideos", "No saved videos yet")}</p>
        </div>
      ) : (
        <div className="space-y-2">
          {filtered.map((video) => {
            const meta = getSportMeta(video.sport as SportId);
            const scoreInfo = scoreMap[video.task_id];
            const isSelected = selected.has(video.id);
            return (
              <div
                key={video.id}
                className={`flex items-center gap-3 bg-slate-800/60 rounded-xl border p-3 sm:p-4 transition-colors ${
                  isSelected ? "border-cyan-500" : "border-slate-700"
                }`}
              >
                {compareMode && (
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => toggleSelect(video.id)}
                    disabled={!isSelected && selected.size >= 2}
                    className="shrink-0"
                  />
                )}
                <span className="text-2xl shrink-0">{meta.emoji}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-white text-sm font-medium">{meta.name}</p>
                  <p className="text-slate-400 text-xs">
                    {video.created_at
                      ? new Date(video.created_at).toLocaleDateString(undefined, {
                          year: "numeric",
                          month: "short",
                          day: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })
                      : ""}
                  </p>
                </div>
                {scoreInfo?.score != null && scoreInfo.grade && (
                  <div className="shrink-0">
                    <ScoreBadge score={scoreInfo.score} grade={scoreInfo.grade} size="sm" />
                  </div>
                )}
                <div className="flex items-center gap-2 shrink-0">
                  <button
                    onClick={() => handleView(video)}
                    className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-xs transition-colors"
                  >
                    View
                  </button>
                  <button
                    onClick={() => handleDelete(video.id)}
                    className="px-2 py-1.5 text-red-400 hover:text-red-300 text-xs transition-colors"
                  >
                    &#10005;
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </motion.div>
  );
}
