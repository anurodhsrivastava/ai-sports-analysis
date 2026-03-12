export interface StatTarget {
  min: number;
  max: number;
  unit: string;
  label: string;
  explanationKey: string;
}

// Map: sport -> stat_key -> StatTarget
const targets: Record<string, Record<string, StatTarget>> = {
  snowboard: {
    avg_knee_angle: {
      min: 35,
      max: 55,
      unit: "°",
      label: "Knee Flexion",
      explanationKey: "stats.snowboard.avg_knee_angle",
    },
    avg_shoulder_alignment: {
      min: 0,
      max: 15,
      unit: "°",
      label: "Shoulder Alignment",
      explanationKey: "stats.snowboard.avg_shoulder_alignment",
    },
  },
  skiing: {
    avg_knee_angle: {
      min: 90,
      max: 140,
      unit: "°",
      label: "Knee Flexion",
      explanationKey: "stats.skiing.avg_knee_angle",
    },
    avg_ski_parallelism: {
      min: 0,
      max: 10,
      unit: "°",
      label: "Ski Parallelism",
      explanationKey: "stats.skiing.avg_ski_parallelism",
    },
    avg_hip_alignment: {
      min: 0,
      max: 20,
      unit: "°",
      label: "Hip Alignment",
      explanationKey: "stats.skiing.avg_hip_alignment",
    },
  },
  running: {
    cadence_spm: {
      min: 170,
      max: 190,
      unit: "SPM",
      label: "Cadence",
      explanationKey: "stats.running.cadence_spm",
    },
    avg_forward_lean: {
      min: 5,
      max: 15,
      unit: "°",
      label: "Forward Lean",
      explanationKey: "stats.running.avg_forward_lean",
    },
    avg_arm_angle: {
      min: 85,
      max: 100,
      unit: "°",
      label: "Arm Swing",
      explanationKey: "stats.running.avg_arm_angle",
    },
  },
  golf: {
    avg_spine_angle: {
      min: 30,
      max: 45,
      unit: "°",
      label: "Spine Angle",
      explanationKey: "stats.golf.avg_spine_angle",
    },
    avg_hip_rotation: {
      min: 40,
      max: 50,
      unit: "°",
      label: "Hip Rotation",
      explanationKey: "stats.golf.avg_hip_rotation",
    },
    avg_arm_extension: {
      min: 165,
      max: 180,
      unit: "°",
      label: "Arm Extension",
      explanationKey: "stats.golf.avg_arm_extension",
    },
  },
  yoga: {
    balance_score: {
      min: 80,
      max: 100,
      unit: "",
      label: "Balance Score",
      explanationKey: "stats.yoga.balance_score",
    },
    symmetry_score: {
      min: 80,
      max: 100,
      unit: "",
      label: "Symmetry Score",
      explanationKey: "stats.yoga.symmetry_score",
    },
  },
  home_workout: {
    avg_knee_angle: {
      min: 80,
      max: 90,
      unit: "°",
      label: "Squat Depth",
      explanationKey: "stats.home_workout.avg_knee_angle",
    },
    rep_count: {
      min: 1,
      max: 999,
      unit: "reps",
      label: "Rep Count",
      explanationKey: "stats.home_workout.rep_count",
    },
  },
};

export function getStatTarget(
  sport: string,
  statKey: string,
): StatTarget | undefined {
  return targets[sport]?.[statKey];
}
