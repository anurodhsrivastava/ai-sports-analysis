import { motion } from "framer-motion";
import type { SportId } from "../data/sportDefinitions";
import { getSportMeta } from "../data/sportDefinitions";

interface Props {
  sport: SportId;
}

export default function ProcessingState({ sport }: Props) {
  const meta = getSportMeta(sport);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex flex-col items-center gap-6"
    >
      {/* Spinning sport emoji */}
      <motion.div
        animate={{ rotateY: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        className="text-7xl"
        style={{ perspective: 200 }}
      >
        {meta.emoji}
      </motion.div>

      <div className="text-center">
        <h2 className="text-2xl font-semibold text-white mb-2">
          Analyzing your technique...
        </h2>
        <p className="text-slate-400">
          Running pose estimation and biomechanical analysis
        </p>
      </div>

      {/* Animated dots */}
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
            className="w-3 h-3 rounded-full bg-cyan-400"
          />
        ))}
      </div>

      {/* Pipeline steps */}
      <div className="mt-4 space-y-2 text-sm text-slate-500">
        <Step label="Extracting frames" />
        <Step label="Detecting pose keypoints" />
        <Step label="Computing joint angles" />
        <Step label="Generating coaching tips" />
      </div>
    </motion.div>
  );
}

function Step({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-2">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        className="w-4 h-4 border-2 border-slate-600 border-t-cyan-400 rounded-full"
      />
      <span>{label}</span>
    </div>
  );
}
