export type AnalysisStatus = "processing" | "completed" | "failed";
export type Severity = "ok" | "warning" | "critical";

export interface CoachingTip {
  category: string;
  body_part: string;
  angle_value: number;
  threshold: number;
  message: string;
  severity: Severity;
  frame_range: [number, number];
}

export interface SportSpecificStats {
  stats: Record<string, number | string | null>;
}

export interface CategoryBreakdown {
  category: string;
  count: number;
  avg_angle_value: number;
  worst_severity: Severity;
}

export interface CoachingSummary {
  overall_assessment: string;
  category_breakdowns: CategoryBreakdown[];
  top_tips: CoachingTip[];
}

export interface UploadResponse {
  task_id: string;
  status: AnalysisStatus;
  sport: string;
}

export interface AnalysisResult {
  task_id: string;
  status: AnalysisStatus;
  sport: string;
  coaching_tips: CoachingTip[];
  video_url: string | null;
  keypoints_summary: SportSpecificStats | null;
  coaching_summary: CoachingSummary | null;
  video_fps: number | null;
  error: string | null;
}
