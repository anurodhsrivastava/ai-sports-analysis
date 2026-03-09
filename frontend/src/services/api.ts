import axios from "axios";
import type { AnalysisResult, UploadResponse } from "../types/analysis";

const api = axios.create({
  baseURL: "/api",
});

export async function uploadVideo(
  file: File,
  sport: string,
  onProgress?: (percent: number) => void
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
  taskId: string
): Promise<AnalysisResult> {
  const { data } = await api.get<AnalysisResult>(`/analyze/${taskId}`);
  return data;
}

// ---------------------------------------------------------------------------
// WebSocket-based monitoring with polling fallback
// ---------------------------------------------------------------------------

export function monitorAnalysis(
  taskId: string,
  onResult: (result: AnalysisResult) => void
): () => void {
  const ws = connectWebSocket(taskId, onResult);
  if (ws) {
    return () => ws.close();
  }
  return pollAnalysis(taskId, onResult);
}

function connectWebSocket(
  taskId: string,
  onResult: (result: AnalysisResult) => void
): WebSocket | null {
  try {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(`${protocol}//${window.location.host}/api/ws/${taskId}`);

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
  intervalMs = 2000
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
      });
    }
  }, intervalMs);

  return () => clearInterval(timer);
}
