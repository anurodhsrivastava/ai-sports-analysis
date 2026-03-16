import { lazy, Suspense, useEffect, useState } from "react";
import { AnimatePresence } from "framer-motion";
import { useTranslation } from "react-i18next";
import type { AnalysisResult, AuthProvider, User } from "./types/analysis";
import type { SportId } from "./data/sportDefinitions";
import { getSportMeta } from "./data/sportDefinitions";
import {
  getCurrentUser,
  login,
  logout,
  monitorAnalysis,
  register,
  saveAnalysis,
  uploadVideo,
} from "./services/api";
import UploadZone from "./components/UploadZone";
import ProcessingState from "./components/ProcessingState";
import ResultsView from "./components/ResultsView";
import LoginModal from "./components/LoginModal";
import WishlistModal from "./components/WishlistModal";
import LanguageSelector from "./components/LanguageSelector";
import type { CompareItem } from "./pages/MyVideos";

// Lazy-loaded pages
const Pricing = lazy(() => import("./pages/Pricing"));
const Admin = lazy(() => import("./pages/Admin"));
const MyVideos = lazy(() => import("./pages/MyVideos"));
const ComparisonView = lazy(() => import("./components/ComparisonView"));

type AppPage = "main" | "pricing" | "admin" | "myVideos" | "compare";
type AppState = "upload" | "processing" | "results" | "error";

export default function App() {
  const { t } = useTranslation();
  const [page, setPage] = useState<AppPage>("main");
  const [state, setState] = useState<AppState>("upload");
  const [selectedSport, setSelectedSport] = useState<SportId>("snowboard");
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [fileSizeMB, setFileSizeMB] = useState<number | undefined>();

  // Auth
  const [user, setUser] = useState<User | null>(null);
  const [showLogin, setShowLogin] = useState(false);

  // Auth error
  const [loginError, setLoginError] = useState<string | null>(null);

  // Wishlist
  const [showWishlist, setShowWishlist] = useState(false);
  const [detectedUnsupportedSport, setDetectedUnsupportedSport] = useState("");

  // Compare
  const [compareData, setCompareData] = useState<[CompareItem, CompareItem] | null>(null);
  const [compareSport, setCompareSport] = useState<SportId>("snowboard");

  // Restore auth on mount
  useEffect(() => {
    const token = localStorage.getItem("jwt_token");
    if (token) {
      getCurrentUser()
        .then((data) => {
          if (data.authenticated && data.user_id) {
            setUser({
              user_id: data.user_id,
              display_name: data.display_name ?? "User",
              email: data.email ?? "",
              role: data.role as User["role"],
              tier: data.tier as User["tier"],
            });
          }
        })
        .catch(() => {
          localStorage.removeItem("jwt_token");
        });
    }
  }, []);

  // Check for upgrade success
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("upgraded") === "1") {
      getCurrentUser().then((data) => {
        if (data.authenticated && data.user_id) {
          setUser({
            user_id: data.user_id,
            display_name: data.display_name ?? "User",
            email: data.email ?? "",
            role: data.role as User["role"],
            tier: data.tier as User["tier"],
          });
        }
      });
      window.history.replaceState({}, "", "/");
    }
  }, []);

  const handleUpload = async (file: File) => {
    try {
      setFileSizeMB(file.size / (1024 * 1024));
      setUploadProgress(0);
      const { task_id } = await uploadVideo(file, selectedSport, setUploadProgress);

      setUploadProgress(null);
      setState("processing");

      monitorAnalysis(task_id, (analysisResult) => {
        if (analysisResult.status === "completed") {
          setResult(analysisResult);
          setState("results");
        } else if (
          analysisResult.error &&
          analysisResult.error.includes("sport mismatch")
        ) {
          const match = analysisResult.error.match(/detected: (.+)/);
          if (match) {
            setDetectedUnsupportedSport(match[1]);
            setShowWishlist(true);
          }
          setError(analysisResult.error);
          setState("error");
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
    setState("upload");
    setResult(null);
    setError(null);
    setUploadProgress(null);
    setFileSizeMB(undefined);
  };

  const handleLogin = async (provider: AuthProvider, email?: string, password?: string) => {
    setLoginError(null);
    try {
      if (provider === "email" && password) {
        const resp = await login(provider, password, email);
        if (resp.success && resp.user_id) {
          setUser({
            user_id: resp.user_id,
            display_name: resp.display_name ?? "User",
            email: resp.email ?? "",
            tier: resp.tier as User["tier"],
          });
        }
      } else {
        const resp = await login(provider, "mock-oauth-token");
        if (resp.success && resp.user_id) {
          setUser({
            user_id: resp.user_id,
            display_name: resp.display_name ?? "User",
            email: resp.email ?? "",
            tier: resp.tier as User["tier"],
          });
        }
      }
      setShowLogin(false);
    } catch (err: unknown) {
      const msg =
        err && typeof err === "object" && "response" in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : undefined;
      setLoginError(msg ?? "Login failed. Please try again.");
    }
  };

  const handleRegister = async (email: string, password: string, displayName?: string) => {
    setLoginError(null);
    try {
      const resp = await register(email, password, displayName);
      if (resp.success && resp.user_id) {
        setUser({
          user_id: resp.user_id,
          display_name: resp.display_name ?? "User",
          email: resp.email ?? "",
          tier: resp.tier as User["tier"],
        });
      }
      setShowLogin(false);
    } catch (err: unknown) {
      const msg =
        err && typeof err === "object" && "response" in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : undefined;
      setLoginError(msg ?? "Registration failed. Please try again.");
    }
  };

  const handleLogout = () => {
    logout();
    setUser(null);
    setPage("main");
  };

  const handleSaveResults = async () => {
    if (!user) {
      setShowLogin(true);
      return;
    }
    if (result) {
      try {
        await saveAnalysis(result.task_id);
      } catch {
        // quota error will be shown
      }
    }
  };

  const handleViewResult = (analysisResult: AnalysisResult, sport: SportId) => {
    setResult(analysisResult);
    setSelectedSport(sport);
    setState("results");
    setPage("main");
  };

  const handleCompare = (items: [CompareItem, CompareItem]) => {
    setCompareData(items);
    // Determine sport from the result
    const s = items[0].result.sport as SportId;
    setCompareSport(s);
    setPage("compare");
  };

  const sportMeta = getSportMeta(selectedSport);

  return (
    <div className="min-h-screen min-h-[100dvh] bg-slate-900 flex flex-col">
      {/* Nav */}
      <header className="border-b border-slate-800 px-4 sm:px-6 py-3 sm:py-4 shrink-0">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2 sm:gap-3">
            <span className="text-xl sm:text-2xl">{sportMeta.emoji}</span>
            <button
              onClick={() => { setPage("main"); handleReset(); }}
              className="font-bold text-white text-base sm:text-lg hover:text-cyan-400 transition-colors"
            >
              {t("app.title")}
            </button>
          </div>
          <div className="flex items-center gap-2 sm:gap-4">
            <LanguageSelector />
            {user && (
              <button
                onClick={() => setPage("myVideos")}
                className="text-xs sm:text-sm text-slate-400 hover:text-slate-300 transition-colors"
              >
                {t("nav.myVideos")}
              </button>
            )}
            {user && (
              <button
                onClick={() => setPage("pricing")}
                className="text-xs sm:text-sm text-slate-400 hover:text-slate-300 transition-colors"
              >
                {t("nav.pricing")}
              </button>
            )}
            {user?.role === "admin" && (
              <button
                onClick={() => setPage("admin")}
                className="text-xs sm:text-sm text-slate-400 hover:text-slate-300 transition-colors"
              >
                {t("nav.admin")}
              </button>
            )}
            {user ? (
              <div className="flex items-center gap-2">
                <span className="text-xs sm:text-sm text-slate-400">
                  {user.display_name}
                  {user.tier === "pro" && (
                    <span className="ml-1 text-[10px] bg-cyan-600 text-white px-1.5 py-0.5 rounded-full">
                      PRO
                    </span>
                  )}
                </span>
                <button
                  onClick={handleLogout}
                  className="text-xs text-slate-500 hover:text-slate-400 transition-colors"
                >
                  {t("app.signOut")}
                </button>
              </div>
            ) : (
              <button
                onClick={() => setShowLogin(true)}
                className="text-xs sm:text-sm text-cyan-400 hover:text-cyan-300 transition-colors font-medium"
              >
                {t("app.signIn")}
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 flex items-center justify-center p-3 sm:p-6 overflow-y-auto">
        <Suspense
          fallback={
            <div className="text-slate-400 text-center">Loading...</div>
          }
        >
          {page === "pricing" && (
            <Pricing
              user={user}
              onLoginPrompt={() => setShowLogin(true)}
              onBack={() => setPage("main")}
            />
          )}
          {page === "admin" && user?.role === "admin" && (
            <Admin onBack={() => setPage("main")} />
          )}
          {page === "myVideos" && user && (
            <MyVideos
              user={user}
              onBack={() => setPage("main")}
              onViewResult={handleViewResult}
              onCompare={handleCompare}
            />
          )}
          {page === "compare" && compareData && (
            <ComparisonView
              older={compareData[0]}
              newer={compareData[1]}
              sport={compareSport}
              onBack={() => setPage("myVideos")}
            />
          )}
          {page === "main" && (
            <AnimatePresence mode="wait">
              {state === "upload" && (
                <UploadZone
                  key="upload"
                  sport={selectedSport}
                  onUpload={handleUpload}
                  uploadProgress={uploadProgress}
                  onSportChange={setSelectedSport}
                />
              )}

              {state === "processing" && (
                <ProcessingState
                  key="processing"
                  sport={selectedSport}
                  fileSizeMB={fileSizeMB}
                />
              )}

              {state === "results" && result && (
                <ResultsView
                  key="results"
                  result={result}
                  sport={selectedSport}
                  onReset={handleReset}
                  user={user}
                  onLoginPrompt={() => setShowLogin(true)}
                  onSaveResults={handleSaveResults}
                />
              )}

              {state === "error" && (
                <div key="error" className="text-center px-4">
                  <div className="text-4xl sm:text-5xl mb-4">&#9888;</div>
                  <h2 className="text-xl sm:text-2xl font-semibold text-white mb-2">
                    {t("errors.somethingWrong")}
                  </h2>
                  <p className="text-slate-400 mb-6 text-sm sm:text-base max-w-md mx-auto">
                    {error}
                  </p>
                  <button
                    onClick={handleReset}
                    className="px-6 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors"
                  >
                    {t("errors.tryAgain")}
                  </button>
                </div>
              )}
            </AnimatePresence>
          )}
        </Suspense>
      </main>

      {/* Login Modal */}
      <LoginModal
        isOpen={showLogin}
        onClose={() => { setShowLogin(false); setLoginError(null); }}
        onLogin={handleLogin}
        onRegister={handleRegister}
        error={loginError}
      />

      {/* Wishlist Modal */}
      <WishlistModal
        isOpen={showWishlist}
        onClose={() => setShowWishlist(false)}
        detectedSport={detectedUnsupportedSport}
      />
    </div>
  );
}
