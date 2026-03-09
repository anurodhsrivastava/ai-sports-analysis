export type SportId = "snowboard" | "skiing" | "running" | "home_workout" | "yoga" | "golf";

export interface SportMeta {
  id: SportId;
  name: string;
  emoji: string;
  description: string;
  accentColor: string;
}

export const SPORTS: SportMeta[] = [
  {
    id: "snowboard",
    name: "Snowboarding",
    emoji: "\uD83C\uDFC2",
    description: "Analyze knee flexion, shoulder alignment, and stance width for better carving.",
    accentColor: "cyan",
  },
  {
    id: "skiing",
    name: "Skiing",
    emoji: "\u26F7\uFE0F",
    description: "Check ski parallelism, pole position, hip alignment, and knee bend.",
    accentColor: "blue",
  },
  {
    id: "running",
    name: "Running",
    emoji: "\uD83C\uDFC3",
    description: "Evaluate foot strike, forward lean, arm swing, and cadence.",
    accentColor: "green",
  },
  {
    id: "home_workout",
    name: "Home Workouts",
    emoji: "\uD83D\uDCAA",
    description: "Analyze squats, push-ups, planks, and lunges with rep counting.",
    accentColor: "orange",
  },
  {
    id: "yoga",
    name: "Yoga",
    emoji: "\uD83E\uDDD8",
    description: "Analyze your yoga poses for alignment, balance, joint safety, and left-right symmetry.",
    accentColor: "purple",
  },
  {
    id: "golf",
    name: "Golf",
    emoji: "\u26F3",
    description: "Analyze your golf swing mechanics including spine angle, hip rotation, and arm extension.",
    accentColor: "emerald",
  },
];

export function getSportMeta(id: SportId): SportMeta {
  return SPORTS.find((s) => s.id === id) ?? SPORTS[0];
}
