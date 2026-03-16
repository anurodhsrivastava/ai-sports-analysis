import { useCallback, useRef, useState } from "react";
import { motion } from "framer-motion";
import { useTranslation } from "react-i18next";
import type { SportId } from "../data/sportDefinitions";
import { SPORTS, getSportMeta } from "../data/sportDefinitions";

interface Props {
  sport: SportId;
  onUpload: (file: File) => void;
  uploadProgress: number | null;
  onSportChange: (sport: SportId) => void;
}

export default function UploadZone({ sport, onUpload, uploadProgress, onSportChange }: Props) {
  const { t } = useTranslation();
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const meta = getSportMeta(sport);

  const handleFile = useCallback(
    (file: File) => {
      const validTypes = [
        "video/mp4",
        "video/avi",
        "video/mov",
        "video/quicktime",
        "video/x-matroska",
        "video/webm",
      ];
      if (
        !validTypes.includes(file.type) &&
        !file.name.match(/\.(mp4|avi|mov|mkv|webm)$/i)
      ) {
        alert(t("upload.invalidFile"));
        return;
      }
      onUpload(file);
    },
    [onUpload, t],
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile],
  );

  const isUploading = uploadProgress !== null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="flex flex-col items-center gap-6 sm:gap-8 w-full max-w-lg px-4"
    >
      <div className="text-center">
        <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">
          {t("upload.heading")}
        </h1>
        <p className="text-slate-400 text-base sm:text-lg">
          {t("upload.subheading")}
        </p>
      </div>

      {/* Inline sport selector */}
      <div className="flex flex-wrap justify-center gap-2 sm:gap-3">
        {SPORTS.map((s) => {
          const isSelected = s.id === sport;
          return (
            <motion.button
              key={s.id}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onSportChange(s.id)}
              className={`
                flex items-center gap-2 px-3 py-2 sm:px-4 sm:py-2.5 rounded-xl text-sm font-medium
                transition-all border
                ${
                  isSelected
                    ? "bg-cyan-600 border-cyan-500 text-white shadow-lg shadow-cyan-600/20"
                    : "bg-slate-800/60 border-slate-700 text-slate-300 hover:border-slate-500 hover:bg-slate-700/60"
                }
              `}
            >
              <span className="text-lg">{s.emoji}</span>
              <span>{s.name}</span>
            </motion.button>
          );
        })}
      </div>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => !isUploading && inputRef.current?.click()}
        className={`
          w-full border-2 border-dashed rounded-2xl p-8 sm:p-12
          flex flex-col items-center gap-4 cursor-pointer transition-all
          ${
            isDragging
              ? "border-cyan-400 bg-cyan-400/10"
              : "border-slate-600 hover:border-slate-400 bg-slate-800/50"
          }
          ${isUploading ? "pointer-events-none opacity-70" : ""}
        `}
      >
        <div className="text-4xl sm:text-5xl">{meta.emoji}</div>

        {isUploading ? (
          <div className="w-full">
            <p className="text-sm text-slate-400 mb-2 text-center">
              {t("upload.uploading", { percent: uploadProgress })}
            </p>
            <div className="w-full bg-slate-700 rounded-full h-2">
              <div
                className="bg-cyan-400 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        ) : (
          <>
            <p className="text-slate-300 font-medium text-center text-sm sm:text-base">
              {t("upload.dropText")}
            </p>
            <p className="text-xs sm:text-sm text-slate-500">
              {t("upload.fileTypes")}
            </p>
          </>
        )}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="video/*"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleFile(file);
        }}
      />
    </motion.div>
  );
}
