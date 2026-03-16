import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  createDiscountCode,
  deactivateDiscountCode,
  getDiscountCodes,
  type AdminDiscountCode,
} from "../../services/adminApi";

export default function DiscountCodes() {
  const { t } = useTranslation();
  const [codes, setCodes] = useState<AdminDiscountCode[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    code: "",
    percent_off: "",
    amount_off: "",
    max_uses: "",
    valid_until: "",
  });

  const loadCodes = async () => {
    try {
      const data = await getDiscountCodes();
      setCodes(data);
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    getDiscountCodes().then(setCodes).catch(() => {});
  }, []);

  const handleCreate = async () => {
    if (!form.code.trim()) return;
    try {
      await createDiscountCode({
        code: form.code.trim(),
        percent_off: form.percent_off ? Number(form.percent_off) : undefined,
        amount_off: form.amount_off ? Number(form.amount_off) * 100 : undefined,
        max_uses: form.max_uses ? Number(form.max_uses) : undefined,
        valid_until: form.valid_until || undefined,
      });
      setForm({ code: "", percent_off: "", amount_off: "", max_uses: "", valid_until: "" });
      setShowForm(false);
      loadCodes();
    } catch {
      alert("Failed to create code");
    }
  };

  const handleDeactivate = async (id: string) => {
    await deactivateDiscountCode(id);
    loadCodes();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">{t("admin.discountCodes")}</h3>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-3 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-sm"
        >
          {t("admin.createCode")}
        </button>
      </div>

      {/* Create form */}
      {showForm && (
        <div className="bg-slate-800 rounded-xl p-4 mb-4 border border-slate-700 grid grid-cols-2 sm:grid-cols-3 gap-3">
          <input
            type="text"
            value={form.code}
            onChange={(e) => setForm({ ...form, code: e.target.value })}
            placeholder={t("admin.code")}
            className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm"
          />
          <input
            type="number"
            value={form.percent_off}
            onChange={(e) => setForm({ ...form, percent_off: e.target.value })}
            placeholder={t("admin.percentOff")}
            className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm"
          />
          <input
            type="number"
            value={form.amount_off}
            onChange={(e) => setForm({ ...form, amount_off: e.target.value })}
            placeholder={t("admin.amountOff")}
            className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm"
          />
          <input
            type="number"
            value={form.max_uses}
            onChange={(e) => setForm({ ...form, max_uses: e.target.value })}
            placeholder={t("admin.maxUses")}
            className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm"
          />
          <input
            type="date"
            value={form.valid_until}
            onChange={(e) => setForm({ ...form, valid_until: e.target.value })}
            className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm"
          />
          <button
            onClick={handleCreate}
            className="px-3 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-medium"
          >
            {t("admin.create")}
          </button>
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead>
            <tr className="text-slate-400 border-b border-slate-700">
              <th className="pb-2 pr-4">{t("admin.code")}</th>
              <th className="pb-2 pr-4">{t("admin.percentOff")}</th>
              <th className="pb-2 pr-4">{t("admin.amountOff")}</th>
              <th className="pb-2 pr-4">{t("admin.maxUses")}</th>
              <th className="pb-2 pr-4">{t("admin.timesUsed")}</th>
              <th className="pb-2 pr-4">{t("admin.validUntil")}</th>
              <th className="pb-2 pr-4">{t("admin.active")}</th>
              <th className="pb-2">{t("admin.actions")}</th>
            </tr>
          </thead>
          <tbody>
            {codes.map((code) => (
              <tr
                key={code.id}
                className="border-b border-slate-800 text-slate-300"
              >
                <td className="py-2 pr-4 font-mono">{code.code}</td>
                <td className="py-2 pr-4">
                  {code.percent_off ? `${code.percent_off}%` : "-"}
                </td>
                <td className="py-2 pr-4">
                  {code.amount_off ? `$${(code.amount_off / 100).toFixed(2)}` : "-"}
                </td>
                <td className="py-2 pr-4">{code.max_uses ?? "Unlimited"}</td>
                <td className="py-2 pr-4">{code.times_used}</td>
                <td className="py-2 pr-4">
                  {code.valid_until
                    ? new Date(code.valid_until).toLocaleDateString()
                    : "No expiry"}
                </td>
                <td className="py-2 pr-4">
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full ${
                      code.active
                        ? "bg-emerald-900 text-emerald-400"
                        : "bg-red-900 text-red-400"
                    }`}
                  >
                    {code.active ? "Active" : "Inactive"}
                  </span>
                </td>
                <td className="py-2">
                  {code.active && (
                    <button
                      onClick={() => handleDeactivate(code.id)}
                      className="text-xs text-red-400 hover:text-red-300"
                    >
                      {t("admin.deactivate")}
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
