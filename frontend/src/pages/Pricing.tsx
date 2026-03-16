import { useState } from "react";
import { useTranslation } from "react-i18next";
import { motion } from "framer-motion";
import type { User } from "../types/analysis";
import { createCheckoutSession, validateDiscount } from "../services/api";

interface Props {
  user: User | null;
  onLoginPrompt: () => void;
  onBack: () => void;
}

export default function Pricing({ user, onLoginPrompt, onBack }: Props) {
  const { t } = useTranslation();
  const [discountCode, setDiscountCode] = useState("");
  const [discountInfo, setDiscountInfo] = useState<{
    valid: boolean;
    percent_off?: number;
    amount_off?: number;
    message?: string;
  } | null>(null);
  const [loading, setLoading] = useState(false);

  const handleUpgrade = async () => {
    if (!user) {
      onLoginPrompt();
      return;
    }
    setLoading(true);
    try {
      const { checkout_url } = await createCheckoutSession(
        discountInfo?.valid ? discountCode : undefined,
      );
      window.location.href = checkout_url;
    } catch {
      alert(t("errors.paymentFailed"));
    } finally {
      setLoading(false);
    }
  };

  const handleValidateDiscount = async () => {
    if (!discountCode.trim()) return;
    const result = await validateDiscount(discountCode.trim());
    setDiscountInfo(result);
  };

  const isPro = user?.tier === "pro";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-4xl mx-auto px-4"
    >
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">{t("pricing.title")}</h1>
        <p className="text-slate-400">{t("pricing.subtitle")}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* Free Tier */}
        <div className="bg-slate-800 rounded-2xl border border-slate-700 p-6">
          <h3 className="text-xl font-bold text-white mb-1">{t("pricing.free")}</h3>
          <p className="text-slate-400 text-sm mb-4">{t("pricing.freePriceLabel")}</p>
          <ul className="space-y-3 text-sm text-slate-300">
            <li className="flex items-center gap-2">
              <span className="text-emerald-400">&#10003;</span>
              {t("pricing.freeFeature1")}
            </li>
            <li className="flex items-center gap-2">
              <span className="text-emerald-400">&#10003;</span>
              {t("pricing.freeFeature2")}
            </li>
            <li className="flex items-center gap-2">
              <span className="text-emerald-400">&#10003;</span>
              {t("pricing.freeFeature3")}
            </li>
          </ul>
          {!isPro && (
            <div className="mt-6">
              <span className="px-4 py-2 bg-slate-700 text-slate-400 rounded-xl text-sm font-medium">
                {t("pricing.currentPlan")}
              </span>
            </div>
          )}
        </div>

        {/* Pro Tier */}
        <div className="bg-gradient-to-b from-cyan-900/40 to-slate-800 rounded-2xl border border-cyan-600/40 p-6">
          <h3 className="text-xl font-bold text-white mb-1">{t("pricing.pro")}</h3>
          <p className="text-cyan-400 text-sm mb-4">{t("pricing.proPriceLabel")}</p>
          <ul className="space-y-3 text-sm text-slate-300">
            <li className="flex items-center gap-2">
              <span className="text-cyan-400">&#10003;</span>
              {t("pricing.proFeature1")}
            </li>
            <li className="flex items-center gap-2">
              <span className="text-cyan-400">&#10003;</span>
              {t("pricing.proFeature2")}
            </li>
            <li className="flex items-center gap-2">
              <span className="text-cyan-400">&#10003;</span>
              {t("pricing.proFeature3")}
            </li>
            <li className="flex items-center gap-2">
              <span className="text-cyan-400">&#10003;</span>
              {t("pricing.proFeature4")}
            </li>
          </ul>
          {isPro ? (
            <div className="mt-6">
              <span className="px-4 py-2 bg-cyan-700 text-white rounded-xl text-sm font-medium">
                {t("pricing.currentPlan")}
              </span>
            </div>
          ) : (
            <div className="mt-6 space-y-3">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={discountCode}
                  onChange={(e) => setDiscountCode(e.target.value)}
                  placeholder={t("pricing.discountCode")}
                  className="flex-1 px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm"
                />
                <button
                  onClick={handleValidateDiscount}
                  className="px-3 py-2 bg-slate-600 hover:bg-slate-500 text-white rounded-lg text-sm"
                >
                  {t("pricing.apply")}
                </button>
              </div>
              {discountInfo && (
                <p
                  className={`text-xs ${
                    discountInfo.valid ? "text-emerald-400" : "text-red-400"
                  }`}
                >
                  {discountInfo.valid
                    ? `${discountInfo.percent_off ?? discountInfo.amount_off}${
                        discountInfo.percent_off ? "%" : "$"
                      } off applied!`
                    : discountInfo.message}
                </p>
              )}
              <button
                onClick={handleUpgrade}
                disabled={loading}
                className="w-full px-4 py-3 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl text-sm font-semibold transition-colors disabled:opacity-50"
              >
                {loading ? "..." : t("pricing.upgrade")}
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="text-center">
        <button
          onClick={onBack}
          className="text-sm text-slate-400 hover:text-slate-300 transition-colors"
        >
          &larr; {t("admin.backToApp")}
        </button>
      </div>
    </motion.div>
  );
}
