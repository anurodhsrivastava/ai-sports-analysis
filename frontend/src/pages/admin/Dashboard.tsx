import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { getAdminStats } from "../../services/adminApi";

export default function AdminDashboard() {
  const { t } = useTranslation();
  const [stats, setStats] = useState<{
    total_users: number;
    pro_users: number;
    total_analyses: number;
    active_subscriptions: number;
    total_discount_codes: number;
  } | null>(null);

  useEffect(() => {
    getAdminStats().then(setStats).catch(() => {});
  }, []);

  if (!stats) {
    return <div className="text-slate-400 text-center py-12">Loading...</div>;
  }

  const cards = [
    { label: t("admin.totalUsers"), value: stats.total_users },
    { label: t("admin.proUsers"), value: stats.pro_users },
    { label: t("admin.totalAnalyses"), value: stats.total_analyses },
    { label: t("admin.activeSubscriptions"), value: stats.active_subscriptions },
    { label: t("admin.discountCodes"), value: stats.total_discount_codes },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
      {cards.map((card) => (
        <div
          key={card.label}
          className="bg-slate-800 rounded-xl p-4 text-center border border-slate-700"
        >
          <div className="text-2xl font-bold text-white mb-1">{card.value}</div>
          <div className="text-xs text-slate-400">{card.label}</div>
        </div>
      ))}
    </div>
  );
}
