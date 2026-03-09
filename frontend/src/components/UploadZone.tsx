import { useCallback, useRef, useState } from "react";
import { motion } from "framer-motion";
import type { SportId } from "../data/sportDefinitions";
import { getSportMeta } from "../data/sportDefinitions";

interface Props {
  sport: SportId;
  onUpload: (file: File) => void;
  uploadProgress: number | null;
}

export default function UploadZone({ sport, onUpload, uploadProgress }: Props) {
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
      if (!validTypes.includes(file.type) && !file.name.match(/\.(mp4|avi|mov|mkv|webm)$/i)) {
        alert("Please upload a video file (MP4, AVI, MOV, MKV, or WebM).");
        return;
      }
      onUpload(file);
    },
    [onUpload]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const isUploading = uploadProgress !== null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="flex flex-col items-center gap-8"
    >
      <div className="text-center">
        <h1 className="text-4xl font-bold text-white mb-2">
          AI {meta.name} Coach
        </h1>
        <p className="text-slate-400 text-lg">
          Upload a {meta.name.toLowerCase()} video for technique analysis
        </p>
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
          w-full max-w-lg border-2 border-dashed rounded-2xl p-12
          flex flex-col items-center gap-4 cursor-pointer transition-all
          ${isDragging
            ? "border-cyan-400 bg-cyan-400/10"
            : "border-slate-600 hover:border-slate-400 bg-slate-800/50"
          }
          ${isUploading ? "pointer-events-none opacity-70" : ""}
        `}
      >
        <div className="text-5xl">{meta.emoji}</div>

        {isUploading ? (
          <div className="w-full">
            <p className="text-sm text-slate-400 mb-2 text-center">
              Uploading... {uploadProgress}%
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
            <p className="text-slate-300 font-medium">
              Drop your video here or click to browse
            </p>
            <p className="text-sm text-slate-500">
              MP4, AVI, MOV, MKV, or WebM up to 500MB
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
