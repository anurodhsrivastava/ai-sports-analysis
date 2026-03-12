import { motion } from "framer-motion";

const gradeColor: Record<string, string> = {
  A: "text-emerald-500",
  B: "text-green-500",
  C: "text-yellow-500",
  D: "text-orange-500",
  E: "text-amber-500",
  F: "text-red-500",
};

const gradeStroke: Record<string, string> = {
  A: "stroke-emerald-500",
  B: "stroke-green-500",
  C: "stroke-yellow-500",
  D: "stroke-orange-500",
  E: "stroke-amber-500",
  F: "stroke-red-500",
};

interface Props {
  score: number;
  grade: string;
  size?: "lg" | "sm";
}

export default function ScoreBadge({ score, grade, size = "lg" }: Props) {
  const letter = grade.charAt(0).toUpperCase();
  const color = gradeColor[letter] ?? "text-slate-400";
  const stroke = gradeStroke[letter] ?? "stroke-slate-400";
  const pct = Math.max(0, Math.min(100, score)) / 100;

  const isLg = size === "lg";
  const svgSize = isLg ? 140 : 64;
  const r = isLg ? 58 : 26;
  const sw = isLg ? 6 : 4;
  const circumference = 2 * Math.PI * r;
  const dashOffset = circumference * (1 - pct);

  return (
    <motion.div
      initial={{ scale: 0.7, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: "spring", stiffness: 200, damping: 18 }}
      className="flex flex-col items-center"
    >
      <div className="relative" style={{ width: svgSize, height: svgSize }}>
        <svg
          width={svgSize}
          height={svgSize}
          viewBox={`0 0 ${svgSize} ${svgSize}`}
          className="-rotate-90"
        >
          <circle
            cx={svgSize / 2}
            cy={svgSize / 2}
            r={r}
            fill="none"
            className="stroke-slate-700"
            strokeWidth={sw}
          />
          <motion.circle
            cx={svgSize / 2}
            cy={svgSize / 2}
            r={r}
            fill="none"
            className={stroke}
            strokeWidth={sw}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: dashOffset }}
            transition={{ duration: 1, ease: "easeOut", delay: 0.3 }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`${isLg ? "text-5xl" : "text-lg"} font-bold ${color} leading-none`}>
            {letter}
          </span>
          {isLg && (
            <span className="text-xs text-slate-400 mt-1">
              {score} / 100
            </span>
          )}
        </div>
      </div>
      {!isLg && (
        <span className="text-[10px] text-slate-400 mt-0.5">{score}</span>
      )}
    </motion.div>
  );
}
