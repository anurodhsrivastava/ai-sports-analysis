import { lazy, createElement, type ComponentType } from "react";
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

// Yoga illustrations
const AlignmentDiagram = lazy(() => import("./yoga/AlignmentDiagram"));
const BalanceDiagram = lazy(() => import("./yoga/BalanceDiagram"));
const JointAnglesDiagram = lazy(() => import("./yoga/JointAnglesDiagram"));
const SymmetryDiagram = lazy(() => import("./yoga/SymmetryDiagram"));

// Golf illustrations
const SpineAngleDiagram = lazy(() => import("./golf/SpineAngleDiagram"));
const HipRotationDiagram = lazy(() => import("./golf/HipRotationDiagram"));
const ArmExtensionDiagram = lazy(() => import("./golf/ArmExtensionDiagram"));
const HeadMovementDiagram = lazy(() => import("./golf/HeadMovementDiagram"));

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
  yoga: {
    alignment: AlignmentDiagram,
    balance: BalanceDiagram,
    jointAngles: JointAnglesDiagram,
    symmetry: SymmetryDiagram,
  },
  golf: {
    spineAngle: SpineAngleDiagram,
    hipRotation: HipRotationDiagram,
    armExtension: ArmExtensionDiagram,
    headMovement: HeadMovementDiagram,
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

export function IllustrationRenderer({ sport, illustrationKey }: { sport: SportId; illustrationKey: string }) {
  const Component = illustrationsBySport[sport]?.[illustrationKey];
  if (!Component) return null;
  return createElement(Component);
}
