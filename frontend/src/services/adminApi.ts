import axios from "axios";

const api = axios.create({
  baseURL: "/api/admin",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("jwt_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function getAdminStats(): Promise<{
  total_users: number;
  pro_users: number;
  total_analyses: number;
  active_subscriptions: number;
  total_discount_codes: number;
}> {
  const { data } = await api.get("/stats");
  return data;
}

export interface AdminUser {
  id: string;
  email: string;
  display_name: string;
  role: string;
  tier: string;
  provider: string;
  created_at: string | null;
}

export async function getUsers(params: {
  page?: number;
  per_page?: number;
  search?: string;
  role?: string;
}): Promise<{ total: number; page: number; per_page: number; users: AdminUser[] }> {
  const { data } = await api.get("/users", { params });
  return data;
}

export async function updateUserRole(userId: string, role: string): Promise<void> {
  await api.patch(`/users/${userId}/role`, { role });
}

export async function updateUserTier(userId: string, tier: string): Promise<void> {
  await api.patch(`/users/${userId}/tier`, { tier });
}

export interface AdminDiscountCode {
  id: string;
  code: string;
  percent_off: number | null;
  amount_off: number | null;
  max_uses: number | null;
  times_used: number;
  valid_until: string | null;
  active: boolean;
  created_at: string | null;
}

export async function getDiscountCodes(): Promise<AdminDiscountCode[]> {
  const { data } = await api.get("/discount-codes");
  return data;
}

export async function createDiscountCode(params: {
  code: string;
  percent_off?: number;
  amount_off?: number;
  max_uses?: number;
  valid_until?: string;
}): Promise<{ success: boolean; id: string; code: string }> {
  const { data } = await api.post("/discount-codes", params);
  return data;
}

export async function deactivateDiscountCode(codeId: string): Promise<void> {
  await api.delete(`/discount-codes/${codeId}`);
}

export async function getAnalyses(params: {
  page?: number;
  per_page?: number;
  sport?: string;
}): Promise<{
  total: number;
  page: number;
  per_page: number;
  analyses: {
    id: string;
    task_id: string;
    user_id: string | null;
    sport: string;
    status: string;
    created_at: string | null;
  }[];
}> {
  const { data } = await api.get("/analyses", { params });
  return data;
}
