import { useState } from "react";
import { useTranslation } from "react-i18next";
import { motion, AnimatePresence } from "framer-motion";
import { addToWishlist } from "../services/api";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  detectedSport: string;
}

export default function WishlistModal({ isOpen, onClose, detectedSport }: Props) {
  const { t } = useTranslation();
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      await addToWishlist(detectedSport, email || undefined);
      setSubmitted(true);
    } catch {
      setSubmitted(true);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setSubmitted(false);
    setEmail("");
    onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
          onClick={handleClose}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.2 }}
            className="bg-slate-800 rounded-2xl p-6 sm:p-8 w-full max-w-sm border border-slate-700 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            {!submitted ? (
              <>
                <div className="text-center mb-6">
                  <div className="text-4xl mb-3">&#128075;</div>
                  <h2 className="text-xl font-bold text-white">
                    {t("wishlist.comingSoon", { sport: detectedSport })}
                  </h2>
                  <p className="text-slate-400 text-sm mt-2">
                    {t("wishlist.description", { sport: detectedSport })}
                  </p>
                </div>

                <input
                  type="email"
                  placeholder={t("wishlist.emailPlaceholder")}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-600 text-white text-sm placeholder-slate-500 focus:outline-none focus:border-cyan-500 mb-4"
                />

                <button
                  onClick={handleSubmit}
                  disabled={loading}
                  className="w-full px-4 py-3 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl font-medium text-sm transition-colors disabled:opacity-50"
                >
                  {loading ? t("wishlist.submitting") : t("wishlist.notifyMe")}
                </button>

                <button
                  onClick={handleClose}
                  className="w-full mt-3 text-sm text-slate-500 hover:text-slate-300 transition-colors py-2"
                >
                  {t("wishlist.noThanks")}
                </button>
              </>
            ) : (
              <div className="text-center py-4">
                <div className="text-4xl mb-3">&#10024;</div>
                <h2 className="text-xl font-bold text-white mb-2">
                  {t("wishlist.onTheList")}
                </h2>
                <p className="text-slate-400 text-sm">
                  {t("wishlist.willNotify", { sport: detectedSport })}
                </p>
                <button
                  onClick={handleClose}
                  className="mt-6 px-6 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm transition-colors"
                >
                  {t("wishlist.gotIt")}
                </button>
              </div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
