import { useEffect, useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useTranslation } from "react-i18next";
import type { SportId } from "../data/sportDefinitions";
import { getSportMeta } from "../data/sportDefinitions";

interface Props {
  sport: SportId;
  fileSizeMB?: number;
}

export default function ProcessingState({ sport, fileSizeMB }: Props) {
  const { t } = useTranslation("coaching");
  const { t: tc } = useTranslation("common");
  const [factIndex, setFactIndex] = useState(0);
  const [elapsed, setElapsed] = useState(0);
  const meta = getSportMeta(sport);

  const facts = useMemo(() => {
    const sportFacts: string[] = t(`sportFacts.${sport}`, { returnObjects: true, defaultValue: [] }) as string[];
    const generalFacts: string[] = t("sportFacts.general", { returnObjects: true, defaultValue: [] }) as string[];
    const all = [...(Array.isArray(sportFacts) ? sportFacts : []), ...(Array.isArray(generalFacts) ? generalFacts : [])];
    // Shuffle using a seeded approach to avoid lint warning about Math.random in render
    const shuffled = [...all];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = (i * 7 + 13) % (i + 1);
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  }, [sport, t]);

  // Rotate facts every 6 seconds
  useEffect(() => {
    if (facts.length <= 1) return;
    const timer = setInterval(() => {
      setFactIndex((i) => (i + 1) % facts.length);
    }, 6000);
    return () => clearInterval(timer);
  }, [facts.length]);

  // Track elapsed time
  useEffect(() => {
    const timer = setInterval(() => setElapsed((e) => e + 1), 1000);
    return () => clearInterval(timer);
  }, []);

  // Rough ETA
  const estimatedSeconds = fileSizeMB ? Math.round(fileSizeMB * 2 + 10) : 30;
  const remaining = Math.max(0, estimatedSeconds - elapsed);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex flex-col items-center gap-6 px-4 max-w-md w-full"
    >
      <motion.div
        animate={{ rotateY: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        className="text-6xl sm:text-7xl"
        style={{ perspective: 200 }}
      >
        {meta.emoji}
      </motion.div>

      <div className="text-center">
        <h2 className="text-xl sm:text-2xl font-semibold text-white mb-2">
          {tc("processing.analyzing")}
        </h2>
        <p className="text-slate-400 text-sm sm:text-base">
          {tc("processing.subtitle")}
        </p>
      </div>

      <div className="bg-slate-800/60 rounded-xl px-4 py-3 text-center w-full">
        <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">
          {tc("processing.timeRemaining")}
        </p>
        <p className="text-lg font-semibold text-cyan-400">
          {remaining > 0 ? (
            remaining > 60
              ? tc("processing.minutes", { count: Math.ceil(remaining / 60) })
              : tc("processing.seconds", { count: remaining })
          ) : (
            tc("processing.almostDone")
          )}
        </p>
        <div className="w-full bg-slate-700 rounded-full h-1.5 mt-2">
          <motion.div
            className="bg-cyan-400 h-1.5 rounded-full"
            initial={{ width: "0%" }}
            animate={{
              width: `${Math.min(95, (elapsed / estimatedSeconds) * 100)}%`,
            }}
            transition={{ duration: 0.5 }}
          />
        </div>
      </div>

      <div className="flex gap-2">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            animate={{ scale: [1, 1.4, 1], opacity: [0.5, 1, 0.5] }}
            transition={{
              duration: 1,
              repeat: Infinity,
              delay: i * 0.2,
            }}
            className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full bg-cyan-400"
          />
        ))}
      </div>

      <div className="space-y-2 text-xs sm:text-sm text-slate-500">
        <Step label={tc("processing.steps.extracting")} />
        <Step label={tc("processing.steps.detecting")} />
        <Step label={tc("processing.steps.computing")} />
        <Step label={tc("processing.steps.generating")} />
      </div>

      {facts.length > 0 && (
        <div className="w-full bg-slate-800/40 rounded-xl px-4 py-3 min-h-[60px] flex items-center">
          <AnimatePresence mode="wait">
            <motion.p
              key={factIndex}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className="text-xs sm:text-sm text-slate-400 text-center leading-relaxed"
            >
              <span className="text-cyan-400 font-medium">{tc("processing.didYouKnow")}</span>{" "}
              {facts[factIndex]}
            </motion.p>
          </AnimatePresence>
        </div>
      )}
    </motion.div>
  );
}

function Step({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-2">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        className="w-3.5 h-3.5 sm:w-4 sm:h-4 border-2 border-slate-600 border-t-cyan-400 rounded-full"
      />
      <span>{label}</span>
    </div>
  );
}
