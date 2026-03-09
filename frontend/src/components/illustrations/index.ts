import { lazy, type ComponentType } from "react";
import type { SportId } from "../../data/sportDefinitions";

// Snowboard illustrations
const KneeFlexionDiagram = lazy(() => import("./snowboard/KneeFlexionDiagram"));
const ShoulderAlignmentDiagram = lazy(() => import("./snowboard/ShoulderAlignmentDiagram"));
const StanceWidthDiagram = lazy(() => import("./snowboard/StanceWidthDiagram"));

// Skiing illustrations
const ParallelSkiDiagram = lazy(() => import("./skiing/ParallelSkiDiagram"));
const PolePositionDiagram = lazy(() => import("./skiing/PolePositionDiagram"));
const KneeAngleDiagram = lazy(() => import("./skiing/KneeAngleDiagram"));
const HipAlignmentDiagram = lazy(() => import("./skiing/HipAlignmentDiagram"));

// Running illustrations
const FootStrikeDiagram = lazy(() => import("./running/FootStrikeDiagram"));
const ForwardLeanDiagram = lazy(() => import("./running/ForwardLeanDiagram"));
const ArmSwingDiagram = lazy(() => import("./running/ArmSwingDiagram"));
const CadenceDiagram = lazy(() => import("./running/CadenceDiagram"));

// Home workout illustrations
const SquatDepthDiagram = lazy(() => import("./home_workout/SquatDepthDiagram"));
const PushupFormDiagram = lazy(() => import("./home_workout/PushupFormDiagram"));
const PlankAlignmentDiagram = lazy(() => import("./home_workout/PlankAlignmentDiagram"));
const LungeFormDiagram = lazy(() => import("./home_workout/LungeFormDiagram"));

const illustrationsBySport: Record<string, Record<string, ComponentType>> = {
  snowboard: {
    kneeFlexion: KneeFlexionDiagram,
    shoulderAlignment: ShoulderAlignmentDiagram,
    stanceWidth: StanceWidthDiagram,
  },
  skiing: {
    parallelSki: ParallelSkiDiagram,
    polePosition: PolePositionDiagram,
    kneeAngle: KneeAngleDiagram,
    hipAlignment: HipAlignmentDiagram,
  },
  running: {
    footStrike: FootStrikeDiagram,
    forwardLean: ForwardLeanDiagram,
    armSwing: ArmSwingDiagram,
    cadence: CadenceDiagram,
  },
  home_workout: {
    squatDepth: SquatDepthDiagram,
    pushupForm: PushupFormDiagram,
    plankAlignment: PlankAlignmentDiagram,
    lungeForm: LungeFormDiagram,
  },
};

export function getIllustration(sport: SportId, key: string): ComponentType | null {
  return illustrationsBySport[sport]?.[key] ?? null;
}
