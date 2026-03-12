import axios from "axios";
import type {
  AnalysisResult,
  AuthProvider,
  ProgressEntry,
  SavedVideo,
  SportInfo,
  UploadResponse,
} from "../types/analysis";

const api = axios.create({
  baseURL: "/api",
});

// Attach JWT token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("jwt_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function uploadVideo(
  file: File,
  sport: string,
  onProgress?: (percent: number) => void,
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("sport", sport);

  const { data } = await api.post<UploadResponse>("/analyze", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (e) => {
      if (e.total && onProgress) {
        onProgress(Math.round((e.loaded * 100) / e.total));
      }
    },
  });

  return data;
}

export async function getAnalysisResult(
  taskId: string,
): Promise<AnalysisResult> {
  const { data } = await api.get<AnalysisResult>(`/analyze/${taskId}`);
  return data;
}

// ---------------------------------------------------------------------------
// Sports
// ---------------------------------------------------------------------------

export async function getSports(): Promise<SportInfo[]> {
  const { data } = await api.get<SportInfo[]>("/sports");
  return data;
}

export async function addToWishlist(
  sport: string,
  email?: string,
): Promise<{ success: boolean; message: string }> {
  const { data } = await api.post("/sports/wishlist", { sport, email });
  return data;
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export async function login(
  provider: AuthProvider,
  token: string,
  email?: string,
): Promise<{
  success: boolean;
  user_id?: string;
  display_name?: string;
  email?: string;
  jwt_token?: string;
  tier?: string;
  message?: string;
}> {
  const { data } = await api.post("/auth/login", { provider, token, email });
  if (data.jwt_token) {
    localStorage.setItem("jwt_token", data.jwt_token);
  }
  return data;
}

export async function register(
  email: string,
  password: string,
  displayName?: string,
): Promise<{
  success: boolean;
  user_id?: string;
  display_name?: string;
  email?: string;
  jwt_token?: string;
  tier?: string;
}> {
  const { data } = await api.post("/auth/register", {
    email,
    password,
    display_name: displayName,
  });
  if (data.jwt_token) {
    localStorage.setItem("jwt_token", data.jwt_token);
  }
  return data;
}

export async function getCurrentUser(): Promise<{
  authenticated: boolean;
  user_id?: string;
  display_name?: string;
  email?: string;
  role?: string;
  tier?: string;
}> {
  const { data } = await api.get("/auth/me");
  return data;
}

export async function guestSave(
  taskId: string,
): Promise<{ success: boolean; message: string }> {
  const { data } = await api.post("/auth/guest-save", {
    task_id: taskId,
  });
  return data;
}

export function logout() {
  localStorage.removeItem("jwt_token");
}

// ---------------------------------------------------------------------------
// Saved Videos
// ---------------------------------------------------------------------------

export async function getMyVideos(sport?: string): Promise<SavedVideo[]> {
  const params = sport ? { sport } : {};
  const { data } = await api.get("/my-videos/", { params });
  return data;
}

export async function saveAnalysis(taskId: string): Promise<{ success: boolean; id: string }> {
  const { data } = await api.post("/my-videos/save", { task_id: taskId });
  return data;
}

export async function deleteMyVideo(recordId: string): Promise<{ success: boolean }> {
  const { data } = await api.delete(`/my-videos/${recordId}`);
  return data;
}

export async function getMyVideoDetail(recordId: string): Promise<{
  id: string;
  task_id: string;
  sport: string;
  status: string;
  result: AnalysisResult | null;
  created_at: string | null;
}> {
  const { data } = await api.get(`/my-videos/${recordId}`);
  return data;
}

// ---------------------------------------------------------------------------
// Progress
// ---------------------------------------------------------------------------

export async function getProgress(sport?: string): Promise<ProgressEntry[]> {
  const params = sport ? { sport } : {};
  const { data } = await api.get<ProgressEntry[]>("/progress/", { params });
  return data;
}

// ---------------------------------------------------------------------------
// Payments
// ---------------------------------------------------------------------------

export async function createCheckoutSession(
  discountCode?: string,
): Promise<{ checkout_url: string; session_id: string }> {
  const { data } = await api.post("/payments/create-checkout", {
    discount_code: discountCode,
    success_url: `${window.location.origin}/?upgraded=1`,
    cancel_url: window.location.origin,
  });
  return data;
}

export async function getSubscription(): Promise<{
  tier: string;
  subscription: { id: string; plan: string; status: string; current_period_end: string | null } | null;
}> {
  const { data } = await api.get("/payments/subscription");
  return data;
}

export async function cancelSubscription(): Promise<{ success: boolean; message: string }> {
  const { data } = await api.post("/payments/cancel");
  return data;
}

export async function validateDiscount(code: string): Promise<{
  valid: boolean;
  percent_off?: number;
  amount_off?: number;
  message?: string;
}> {
  const { data } = await api.post("/payments/validate-discount", { code });
  return data;
}

// ---------------------------------------------------------------------------
// WebSocket-based monitoring with polling fallback
// ---------------------------------------------------------------------------

export function monitorAnalysis(
  taskId: string,
  onResult: (result: AnalysisResult) => void,
): () => void {
  const ws = connectWebSocket(taskId, onResult);
  if (ws) {
    return () => ws.close();
  }
  return pollAnalysis(taskId, onResult);
}

function connectWebSocket(
  taskId: string,
  onResult: (result: AnalysisResult) => void,
): WebSocket | null {
  try {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(
      `${protocol}//${window.location.host}/api/ws/${taskId}`,
    );

    let settled = false;
    let fallbackStarted = false;

    const startPollingFallback = () => {
      if (!settled && !fallbackStarted) {
        fallbackStarted = true;
        pollAnalysis(taskId, onResult);
      }
    };

    ws.onmessage = (event) => {
      try {
        const result: AnalysisResult = JSON.parse(event.data);
        if (result.status !== "processing") {
          settled = true;
          onResult(result);
        }
      } catch {
        settled = true;
        onResult({
          task_id: taskId,
          status: "failed",
          sport: "unknown",
          coaching_tips: [],
          video_url: null,
          keypoints_summary: null,
          coaching_summary: null,
          video_fps: null,
          error: "Failed to parse analysis result.",
          sport_mismatch: null,
        });
      }
    };

    ws.onerror = () => {
      startPollingFallback();
    };

    ws.onclose = () => {
      startPollingFallback();
    };

    return ws;
  } catch {
    return null;
  }
}

function pollAnalysis(
  taskId: string,
  onResult: (result: AnalysisResult) => void,
  intervalMs = 2000,
): () => void {
  const timer = setInterval(async () => {
    try {
      const result = await getAnalysisResult(taskId);
      if (result.status !== "processing") {
        clearInterval(timer);
        onResult(result);
      }
    } catch {
      clearInterval(timer);
      onResult({
        task_id: taskId,
        status: "failed",
        sport: "unknown",
        coaching_tips: [],
        video_url: null,
        keypoints_summary: null,
        coaching_summary: null,
        video_fps: null,
        error: "Failed to fetch analysis results.",
        sport_mismatch: null,
      });
    }
  }, intervalMs);

  return () => clearInterval(timer);
}
