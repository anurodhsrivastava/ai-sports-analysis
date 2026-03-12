export type AnalysisStatus = "processing" | "completed" | "failed";
export type Severity = "ok" | "warning" | "critical";

export interface CoachingTip {
  category: string;
  body_part: string;
  angle_value: number;
  threshold: number;
  message: string;
  message_key?: string;
  message_params?: Record<string, string | number>;
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
  overall_assessment_key?: string;
  overall_score?: number;
  overall_grade?: string;
  category_breakdowns: CategoryBreakdown[];
  top_tips: CoachingTip[];
}

export interface UploadResponse {
  task_id: string;
  status: AnalysisStatus;
  sport: string;
}

export interface SportMismatchWarning {
  selected_sport: string;
  detected_environment: string;
  suggested_sport: string;
  message: string;
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
  sport_mismatch: SportMismatchWarning | null;
}

// Sport selection
export interface SportInfo {
  id: string;
  label: string;
  emoji: string;
  available: boolean;
}

// Auth
export type AuthProvider = "google" | "facebook" | "email";
export type UserRole = "user" | "admin" | "support" | "tester";
export type UserTier = "free" | "pro";

export interface User {
  user_id: string;
  display_name: string;
  email: string;
  role?: UserRole;
  tier?: UserTier;
  jwt_token?: string;
}

// Saved videos
export interface SavedVideo {
  id: string;
  task_id: string;
  sport: string;
  status: string;
  created_at: string;
  video_url: string | null;
}

// Progress tracking
export interface ProgressEntry {
  task_id: string;
  sport: string;
  score: number | null;
  grade: string | null;
  created_at: string | null;
}

// Wishlist
export interface WishlistRequest {
  sport: string;
  email?: string;
}
