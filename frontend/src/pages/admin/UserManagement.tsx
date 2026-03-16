import { useCallback, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  getUsers,
  updateUserRole,
  updateUserTier,
  type AdminUser,
} from "../../services/adminApi";

export default function UserManagement() {
  const { t } = useTranslation();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("");

  const loadUsers = useCallback(async () => {
    try {
      const result = await getUsers({ page, search, role: roleFilter });
      setUsers(result.users);
      setTotal(result.total);
    } catch {
      // ignore
    }
  }, [page, search, roleFilter]);

  useEffect(() => {
    getUsers({ page, search, role: roleFilter }).then((result) => {
      setUsers(result.users);
      setTotal(result.total);
    }).catch(() => {});
  }, [page, search, roleFilter]);

  const handleRoleChange = async (userId: string, role: string) => {
    await updateUserRole(userId, role);
    loadUsers();
  };

  const handleTierChange = async (userId: string, tier: string) => {
    await updateUserTier(userId, tier);
    loadUsers();
  };

  return (
    <div>
      {/* Filters */}
      <div className="flex gap-3 mb-4">
        <input
          type="text"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          placeholder={t("admin.search")}
          className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm flex-1"
        />
        <select
          value={roleFilter}
          onChange={(e) => {
            setRoleFilter(e.target.value);
            setPage(1);
          }}
          className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm"
        >
          <option value="">All Roles</option>
          <option value="user">User</option>
          <option value="admin">Admin</option>
          <option value="support">Support</option>
          <option value="tester">Tester</option>
        </select>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead>
            <tr className="text-slate-400 border-b border-slate-700">
              <th className="pb-2 pr-4">Email</th>
              <th className="pb-2 pr-4">Name</th>
              <th className="pb-2 pr-4">{t("admin.role")}</th>
              <th className="pb-2 pr-4">{t("admin.tier")}</th>
              <th className="pb-2">Provider</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr
                key={user.id}
                className="border-b border-slate-800 text-slate-300"
              >
                <td className="py-2 pr-4">{user.email}</td>
                <td className="py-2 pr-4">{user.display_name}</td>
                <td className="py-2 pr-4">
                  <select
                    value={user.role}
                    onChange={(e) => handleRoleChange(user.id, e.target.value)}
                    className="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-white"
                  >
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                    <option value="support">Support</option>
                    <option value="tester">Tester</option>
                  </select>
                </td>
                <td className="py-2 pr-4">
                  <select
                    value={user.tier}
                    onChange={(e) => handleTierChange(user.id, e.target.value)}
                    className="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-white"
                  >
                    <option value="free">Free</option>
                    <option value="pro">Pro</option>
                  </select>
                </td>
                <td className="py-2">{user.provider}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between mt-4 text-sm text-slate-400">
        <span>
          {total} total users
        </span>
        <div className="flex gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3 py-1 bg-slate-800 rounded disabled:opacity-50"
          >
            Prev
          </button>
          <span className="px-3 py-1">Page {page}</span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={users.length < 20}
            className="px-3 py-1 bg-slate-800 rounded disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
