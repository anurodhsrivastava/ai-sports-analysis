import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useTranslation } from "react-i18next";
import type { AuthProvider } from "../types/analysis";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onLogin: (provider: AuthProvider, email?: string, password?: string) => void;
  onRegister?: (email: string, password: string, displayName?: string) => void;
  title?: string;
  subtitle?: string;
  error?: string | null;
}

const providers: { id: AuthProvider; labelKey: string; icon: string; bg: string; hover: string }[] = [
  {
    id: "google",
    labelKey: "login.continueGoogle",
    icon: "G",
    bg: "bg-white text-gray-800",
    hover: "hover:bg-gray-100",
  },
  {
    id: "facebook",
    labelKey: "login.continueFacebook",
    icon: "f",
    bg: "bg-[#1877F2] text-white",
    hover: "hover:bg-[#166FE5]",
  },
];

export default function LoginModal({
  isOpen,
  onClose,
  onLogin,
  onRegister,
  title,
  subtitle,
  error,
}: Props) {
  const { t } = useTranslation();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");

  const handleEmailLogin = () => {
    if (email && password) {
      onLogin("email", email, password);
    }
  };

  const handleRegister = () => {
    if (email && password && onRegister) {
      onRegister(email, password, displayName || undefined);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.2 }}
            className="bg-slate-800 rounded-2xl p-6 sm:p-8 w-full max-w-sm border border-slate-700 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="text-center mb-6">
              <h2 className="text-xl font-bold text-white">
                {title ?? (mode === "register" ? t("login.registerTitle") : t("login.saveTitle"))}
              </h2>
              <p className="text-slate-400 text-sm mt-2">
                {subtitle ?? t("login.saveSubtitle")}
              </p>
            </div>

            {/* OAuth providers */}
            <div className="space-y-3 mb-4">
              {providers.map((p) => (
                <button
                  key={p.id}
                  onClick={() => onLogin(p.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-colors ${p.bg} ${p.hover}`}
                >
                  <span className="w-6 h-6 flex items-center justify-center text-lg font-bold">
                    {p.icon}
                  </span>
                  <span>{t(p.labelKey)}</span>
                </button>
              ))}
            </div>

            {/* Divider */}
            <div className="flex items-center gap-3 my-4">
              <div className="flex-1 h-px bg-slate-700" />
              <span className="text-xs text-slate-500">{t("login.continueEmail")}</span>
              <div className="flex-1 h-px bg-slate-700" />
            </div>

            {/* Error message */}
            {error && (
              <div className="mb-3 px-3 py-2 bg-red-900/40 border border-red-700 rounded-lg text-red-300 text-sm text-center">
                {error}
              </div>
            )}

            {/* Email/Password form */}
            <div className="space-y-3">
              {mode === "register" && (
                <input
                  type="text"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  placeholder={t("login.displayName")}
                  className="w-full px-3 py-2.5 bg-slate-700 border border-slate-600 rounded-xl text-white text-sm"
                />
              )}
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={t("login.email")}
                className="w-full px-3 py-2.5 bg-slate-700 border border-slate-600 rounded-xl text-white text-sm"
              />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={t("login.password")}
                className="w-full px-3 py-2.5 bg-slate-700 border border-slate-600 rounded-xl text-white text-sm"
              />
              <button
                onClick={mode === "register" ? handleRegister : handleEmailLogin}
                className="w-full px-4 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl text-sm font-medium transition-colors"
              >
                {mode === "register" ? t("login.register") : t("login.login")}
              </button>
            </div>

            {/* Toggle mode */}
            <div className="text-center mt-3">
              <button
                onClick={() => setMode(mode === "login" ? "register" : "login")}
                className="text-xs text-slate-400 hover:text-slate-300 transition-colors"
              >
                {mode === "login" ? t("login.noAccount") : t("login.haveAccount")}
              </button>
            </div>

            <button
              onClick={onClose}
              className="w-full mt-4 text-sm text-slate-500 hover:text-slate-300 transition-colors py-2"
            >
              {t("login.maybeLater")}
            </button>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
