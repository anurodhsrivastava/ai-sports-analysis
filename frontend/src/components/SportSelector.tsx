import { motion } from "framer-motion";
import { SPORTS, type SportId } from "../data/sportDefinitions";

const accentClasses: Record<string, string> = {
  cyan: "hover:border-cyan-400 hover:bg-cyan-400/10",
  blue: "hover:border-blue-400 hover:bg-blue-400/10",
  green: "hover:border-green-400 hover:bg-green-400/10",
  orange: "hover:border-orange-400 hover:bg-orange-400/10",
};

interface Props {
  onSelect: (sport: SportId) => void;
}

export default function SportSelector({ onSelect }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="flex flex-col items-center gap-8 max-w-2xl w-full"
    >
      <div className="text-center">
        <h1 className="text-4xl font-bold text-white mb-2">
          Sports Coach AI
        </h1>
        <p className="text-slate-400 text-lg">
          Choose a sport to get AI-powered technique analysis
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full">
        {SPORTS.map((sport, i) => (
          <motion.button
            key={sport.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08 }}
            onClick={() => onSelect(sport.id)}
            className={`
              text-left p-6 rounded-xl border border-slate-700
              bg-slate-800/50 cursor-pointer transition-all
              ${accentClasses[sport.accentColor] ?? "hover:border-slate-400"}
            `}
          >
            <div className="text-4xl mb-3">{sport.emoji}</div>
            <h3 className="text-lg font-semibold text-white mb-1">{sport.name}</h3>
            <p className="text-sm text-slate-400">{sport.description}</p>
          </motion.button>
        ))}
      </div>
    </motion.div>
  );
}
