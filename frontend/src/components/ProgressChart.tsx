import { useMemo } from "react";
import { useTranslation } from "react-i18next";
import type { ProgressEntry } from "../types/analysis";
import type { SportId } from "../data/sportDefinitions";

const gradeColor: Record<string, string> = {
  A: "#10b981",
  B: "#22c55e",
  C: "#eab308",
  D: "#f97316",
  E: "#f59e0b",
  F: "#ef4444",
};

interface Props {
  entries: ProgressEntry[];
  sport: SportId;
  isPro: boolean;
}

export default function ProgressChart({ entries, sport, isPro }: Props) {
  const { t } = useTranslation();

  const scored = useMemo(
    () => entries.filter((e) => e.score != null && e.sport === sport),
    [entries, sport],
  );

  if (scored.length < 2) return null;

  const padding = { top: 20, right: 20, bottom: 30, left: 40 };
  const width = 400;
  const height = 180;
  const innerW = width - padding.left - padding.right;
  const innerH = height - padding.top - padding.bottom;

  const points = scored.map((e, i) => {
    const x = padding.left + (i / (scored.length - 1)) * innerW;
    const y = padding.top + innerH - ((e.score ?? 0) / 100) * innerH;
    return { x, y, entry: e };
  });

  const linePath = points.map((p, i) => `${i === 0 ? "M" : "L"}${p.x},${p.y}`).join(" ");

  // Y-axis ticks
  const yTicks = [0, 25, 50, 75, 100];

  // X-axis labels (first and last date)
  const formatDate = (iso: string | null) => {
    if (!iso) return "";
    const d = new Date(iso);
    return `${d.getMonth() + 1}/${d.getDate()}`;
  };

  return (
    <div className="relative">
      {!isPro && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-slate-900/70 backdrop-blur-sm rounded-xl">
          <div className="text-center">
            <p className="text-white font-semibold mb-1">
              {t("myVideos.upgradeForProgress", "Upgrade to Pro")}
            </p>
            <p className="text-slate-400 text-sm">
              {t("myVideos.scoreOverTime", "Track your score over time")}
            </p>
          </div>
        </div>
      )}
      <div className={!isPro ? "blur-sm" : ""}>
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-auto"
          preserveAspectRatio="xMidYMid meet"
        >
          {/* Grid lines */}
          {yTicks.map((tick) => {
            const y = padding.top + innerH - (tick / 100) * innerH;
            return (
              <g key={tick}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={padding.left + innerW}
                  y2={y}
                  stroke="#334155"
                  strokeWidth={0.5}
                />
                <text
                  x={padding.left - 6}
                  y={y + 3}
                  textAnchor="end"
                  className="fill-slate-500"
                  fontSize={9}
                >
                  {tick}
                </text>
              </g>
            );
          })}

          {/* X-axis labels */}
          <text
            x={points[0].x}
            y={height - 5}
            textAnchor="start"
            className="fill-slate-500"
            fontSize={9}
          >
            {formatDate(scored[0].created_at)}
          </text>
          <text
            x={points[points.length - 1].x}
            y={height - 5}
            textAnchor="end"
            className="fill-slate-500"
            fontSize={9}
          >
            {formatDate(scored[scored.length - 1].created_at)}
          </text>

          {/* Line */}
          <path d={linePath} fill="none" stroke="#06b6d4" strokeWidth={2} />

          {/* Points */}
          {points.map((p, i) => (
            <circle
              key={i}
              cx={p.x}
              cy={p.y}
              r={4}
              fill={gradeColor[p.entry.grade?.charAt(0) ?? ""] ?? "#94a3b8"}
              stroke="#0f172a"
              strokeWidth={1.5}
            />
          ))}
        </svg>
      </div>
    </div>
  );
}
