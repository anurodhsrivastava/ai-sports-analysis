import { useState } from "react";
import { AnimatePresence } from "framer-motion";
import type { AnalysisResult } from "./types/analysis";
import type { SportId } from "./data/sportDefinitions";
import { getSportMeta } from "./data/sportDefinitions";
import { monitorAnalysis, uploadVideo } from "./services/api";
import SportSelector from "./components/SportSelector";
import UploadZone from "./components/UploadZone";
import ProcessingState from "./components/ProcessingState";
import ResultsView from "./components/ResultsView";

type AppState = "sport-select" | "upload" | "processing" | "results" | "error";

export default function App() {
  const [state, setState] = useState<AppState>("sport-select");
  const [selectedSport, setSelectedSport] = useState<SportId | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSportSelect = (sport: SportId) => {
    setSelectedSport(sport);
    setState("upload");
  };

  const handleUpload = async (file: File) => {
    if (!selectedSport) return;

    try {
      setUploadProgress(0);
      const { task_id } = await uploadVideo(file, selectedSport, setUploadProgress);

      setUploadProgress(null);
      setState("processing");

      monitorAnalysis(task_id, (analysisResult) => {
        if (analysisResult.status === "completed") {
          setResult(analysisResult);
          setState("results");
        } else {
          setError(analysisResult.error || "Analysis failed.");
          setState("error");
        }
      });
    } catch (err) {
      setUploadProgress(null);
      setError(err instanceof Error ? err.message : "Upload failed.");
      setState("error");
    }
  };

  const handleReset = () => {
    setState("sport-select");
    setSelectedSport(null);
    setResult(null);
    setError(null);
    setUploadProgress(null);
  };

  const sportMeta = selectedSport ? getSportMeta(selectedSport) : null;

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col">
      {/* Nav */}
      <header className="border-b border-slate-800 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center gap-3">
          <span className="text-2xl">{sportMeta?.emoji ?? "\uD83C\uDFC6"}</span>
          <span className="font-bold text-white text-lg">
            {sportMeta ? `${sportMeta.name} Coach AI` : "Sports Coach AI"}
          </span>
          {state !== "sport-select" && (
            <button
              onClick={handleReset}
              className="ml-auto text-sm text-slate-400 hover:text-slate-200 transition-colors"
            >
              Change Sport
            </button>
          )}
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 flex items-center justify-center p-6">
        <AnimatePresence mode="wait">
          {state === "sport-select" && (
            <SportSelector key="sport-select" onSelect={handleSportSelect} />
          )}

          {state === "upload" && selectedSport && (
            <UploadZone
              key="upload"
              sport={selectedSport}
              onUpload={handleUpload}
              uploadProgress={uploadProgress}
            />
          )}

          {state === "processing" && selectedSport && (
            <ProcessingState key="processing" sport={selectedSport} />
          )}

          {state === "results" && result && selectedSport && (
            <ResultsView
              key="results"
              result={result}
              sport={selectedSport}
              onReset={handleReset}
            />
          )}

          {state === "error" && (
            <div key="error" className="text-center">
              <div className="text-5xl mb-4">&#9888;</div>
              <h2 className="text-2xl font-semibold text-white mb-2">
                Something went wrong
              </h2>
              <p className="text-slate-400 mb-6">{error}</p>
              <button
                onClick={handleReset}
                className="px-6 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors"
              >
                Try Again
              </button>
            </div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
