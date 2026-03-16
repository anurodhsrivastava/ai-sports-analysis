import { useState } from "react";
import { useTranslation } from "react-i18next";
import AdminDashboard from "./admin/Dashboard";
import UserManagement from "./admin/UserManagement";
import DiscountCodes from "./admin/DiscountCodes";

interface Props {
  onBack: () => void;
}

type Tab = "dashboard" | "users" | "discountCodes";

export default function Admin({ onBack }: Props) {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<Tab>("dashboard");

  const tabs: { id: Tab; label: string }[] = [
    { id: "dashboard", label: t("admin.dashboard") },
    { id: "users", label: t("admin.users") },
    { id: "discountCodes", label: t("admin.discountCodes") },
  ];

  return (
    <div className="w-full max-w-6xl mx-auto px-4">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white">{t("admin.title")}</h1>
        <button
          onClick={onBack}
          className="text-sm text-slate-400 hover:text-slate-300 transition-colors"
        >
          &larr; {t("admin.backToApp")}
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-slate-800 rounded-xl p-1">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? "bg-cyan-600 text-white"
                : "text-slate-400 hover:text-white"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      {activeTab === "dashboard" && <AdminDashboard />}
      {activeTab === "users" && <UserManagement />}
      {activeTab === "discountCodes" && <DiscountCodes />}
    </div>
  );
}
