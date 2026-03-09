export interface CategoryGuidance {
  title: string;
  whatIsWrong: string;
  howToFix: string;
  drillTip: string;
  idealRange: string;
  illustrationKey: string;
}

const guidanceByCategory: Record<string, Record<string, CategoryGuidance>> = {
  snowboard: {
    "Knee Flexion": {
      title: "Bend Your Knees More",
      whatIsWrong:
        "Your legs are too straight. Riding with locked-out knees makes it hard to absorb bumps, steer, and stay balanced.",
      howToFix:
        "Keep a soft, athletic bend in both knees throughout the run. Imagine sitting into an invisible chair \u2014 your shins should press lightly against the front of your boots.",
      drillTip:
        'Practice "1000 turns" at low speed: on each turn, exaggerate the knee bend until your thighs burn slightly. This builds muscle memory for the correct position.',
      idealRange: "35\u00b0\u201355\u00b0",
      illustrationKey: "kneeFlexion",
    },
    "Shoulder Alignment": {
      title: "Align Your Shoulders with the Board",
      whatIsWrong:
        "Your shoulders are rotated too far open (facing downhill). This forces your hips out of alignment and makes edge-to-edge transitions sluggish.",
      howToFix:
        'Keep your shoulders roughly parallel to the board. Your lead hand should point toward the nose; your rear hand stays over the tail. Think "quiet upper body."',
      drillTip:
        "Grab both ends of a pole or stick while riding and keep it parallel to the board. If the stick rotates, your shoulders are opening up.",
      idealRange: "0\u00b0\u201315\u00b0",
      illustrationKey: "shoulderAlignment",
    },
    "Stance Width": {
      title: "Widen Your Stance",
      whatIsWrong:
        "Your feet are too close together. A narrow stance reduces stability and makes it harder to engage your edges effectively.",
      howToFix:
        "Set your bindings at shoulder width or slightly wider. Your weight should be evenly distributed between both feet with your knees tracking over your toes.",
      drillTip:
        "On flat ground, stand in your board and have a friend push you gently from different directions. Widen your stance until you feel stable against every push.",
      idealRange: "Shoulder width apart",
      illustrationKey: "stanceWidth",
    },
  },
  skiing: {
    "Knee Flexion": {
      title: "Keep Your Knees Flexed",
      whatIsWrong:
        "Your knees are too straight, reducing your ability to absorb terrain and maintain edge control through turns.",
      howToFix:
        "Maintain an athletic stance with knees flexed. Feel the pressure on the front of your boots \u2014 your shins should always be in contact.",
      drillTip:
        "Practice garland turns on a gentle slope, focusing on knee flex at each turn initiation.",
      idealRange: "90\u00b0\u2013140\u00b0",
      illustrationKey: "kneeAngle",
    },
    "Ski Parallelism": {
      title: "Keep Your Skis Parallel",
      whatIsWrong:
        "Your skis are diverging or converging too much, causing wedge-like turns that waste energy and reduce speed control.",
      howToFix:
        "Focus on equal edge angles on both skis. Your feet should feel like they're on railway tracks, moving together.",
      drillTip:
        "Practice straight runs on gentle terrain, consciously keeping both ski tips the same distance apart throughout.",
      idealRange: "0\u00b0\u201310\u00b0 divergence",
      illustrationKey: "parallelSki",
    },
    "Hip Alignment": {
      title: "Square Your Hips to the Fall Line",
      whatIsWrong:
        "Your upper body is rotating too far away from your ski direction, leading to inefficient turns and loss of edge grip.",
      howToFix:
        "Keep your belly button pointing downhill. Your upper and lower body should separate \u2014 let your legs turn underneath a stable torso.",
      drillTip:
        "Hold your poles horizontally in front of you across your stomach while skiing. Keep them pointing downhill as you turn.",
      idealRange: "0\u00b0\u201320\u00b0 from fall line",
      illustrationKey: "hipAlignment",
    },
    "Pole Position": {
      title: "Keep Your Hands Forward",
      whatIsWrong:
        "Your poles are trailing behind you, pulling your weight back and reducing your ability to initiate turns.",
      howToFix:
        "Keep your hands forward and slightly apart at waist height. Your pole tips should point slightly down and back, ready for the next plant.",
      drillTip:
        "Ski with your hands resting on an imaginary shelf in front of you. If your hands drop, you'll feel the balance shift.",
      idealRange: "15\u00b0\u201345\u00b0 from vertical",
      illustrationKey: "polePosition",
    },
  },
  running: {
    "Foot Strike": {
      title: "Reduce Overstriding",
      whatIsWrong:
        "You're landing with your foot too far in front of your body, creating a braking force with each step that wastes energy and increases injury risk.",
      howToFix:
        "Aim to land with your foot beneath your hips, not in front. Think about \"pulling\" the ground beneath you rather than reaching forward.",
      drillTip:
        "Practice running with a slight forward lean from the ankles. Count your steps for 30 seconds \u2014 aim for 85-95 per foot.",
      idealRange: "Ratio < 0.4",
      illustrationKey: "footStrike",
    },
    "Forward Lean": {
      title: "Adjust Your Torso Lean",
      whatIsWrong:
        "Your torso position is either too upright or leaning too far forward, affecting your running economy and increasing fatigue.",
      howToFix:
        "Lean slightly forward from your ankles (not your waist) \u2014 about 5-15 degrees. Imagine a straight line from your ankle through your head.",
      drillTip:
        "Stand tall, then lean forward from your ankles until you feel like you need to step forward. That's your ideal running lean.",
      idealRange: "5\u00b0\u201315\u00b0",
      illustrationKey: "forwardLean",
    },
    "Arm Swing": {
      title: "Optimize Your Arm Drive",
      whatIsWrong:
        "Your arms are either too straight or too tightly bent, reducing your running efficiency and balance.",
      howToFix:
        "Keep your elbows at roughly 85-100 degrees. Swing from your shoulders, not your elbows. Hands should be relaxed, not clenched.",
      drillTip:
        "Practice arm swing drills while standing: pump your arms forward and back (not across your body) with a 90-degree bend.",
      idealRange: "85\u00b0\u2013100\u00b0 elbow angle",
      illustrationKey: "armSwing",
    },
    "Cadence": {
      title: "Increase Your Step Rate",
      whatIsWrong:
        "Your cadence (steps per minute) is below optimal, which typically means you're overstriding and spending too long on the ground per step.",
      howToFix:
        "Gradually increase your cadence by 5-10% at a time. Use a metronome app or music with the right BPM to pace yourself.",
      drillTip:
        "Run to music at 170-180 BPM for short intervals. Over time your natural cadence will increase.",
      idealRange: "170\u2013190 spm",
      illustrationKey: "cadence",
    },
  },
  home_workout: {
    "Squat Depth": {
      title: "Squat Deeper",
      whatIsWrong:
        "You're not reaching proper squat depth. Partial squats limit muscle activation in your glutes and hamstrings.",
      howToFix:
        "Lower until your thighs are at least parallel to the floor (knee angle around 80-90\u00b0). Keep your weight on your heels and chest up.",
      drillTip:
        "Practice box squats: sit back onto a bench/box at parallel depth, then stand. This teaches proper depth and control.",
      idealRange: "80\u00b0\u201390\u00b0 knee angle",
      illustrationKey: "squatDepth",
    },
    "Knee Tracking": {
      title: "Push Your Knees Out",
      whatIsWrong:
        "Your knees are caving inward during the movement. This places stress on your knee ligaments and reduces power.",
      howToFix:
        "Push your knees out over your toes throughout the movement. Think about \"spreading the floor\" with your feet.",
      drillTip:
        "Place a light resistance band around your knees during squats. The band cue will train you to push your knees outward.",
      idealRange: "Knees over toes",
      illustrationKey: "squatDepth",
    },
    "Back Position": {
      title: "Keep Your Chest Up",
      whatIsWrong:
        "Your torso is leaning too far forward, rounding your back and shifting load away from your legs to your lower back.",
      howToFix:
        "Keep your chest proud and back straight. Brace your core as if you're about to get punched in the stomach.",
      drillTip:
        "Practice goblet squats holding a weight at your chest \u2014 the counterweight naturally helps keep your torso upright.",
      idealRange: "< 45\u00b0 forward lean",
      illustrationKey: "squatDepth",
    },
    "Elbow Range": {
      title: "Full Range of Motion",
      whatIsWrong:
        "You're not lowering far enough in your push-ups. Partial range means less muscle engagement and slower progress.",
      howToFix:
        "Lower your chest until your elbows reach at least 90 degrees. Keep your elbows at about 45 degrees from your body.",
      drillTip:
        "Place a tennis ball under your chest. Touch it on every rep to ensure consistent depth.",
      idealRange: "90\u00b0 elbow angle at bottom",
      illustrationKey: "pushupForm",
    },
    "Body Line": {
      title: "Maintain a Straight Body",
      whatIsWrong:
        "Your body is sagging at the hips or piking upward, reducing core engagement and placing strain on your lower back.",
      howToFix:
        "Squeeze your glutes and brace your abs to create a rigid straight line from shoulders to ankles. Don't let your hips drop or rise.",
      drillTip:
        "Practice holding a plank for 30 seconds with a broomstick along your back. It should touch your head, upper back, and tailbone.",
      idealRange: "< 10\u00b0 deviation",
      illustrationKey: "plankAlignment",
    },
    "Front Knee Angle": {
      title: "Perfect Your Lunge Depth",
      whatIsWrong:
        "Your front knee angle isn't optimal \u2014 either too shallow (not enough activation) or too deep (knee past toes).",
      howToFix:
        "Step far enough forward that your front shin is vertical at the bottom. Both knees should be at about 90 degrees.",
      drillTip:
        "Practice static lunges first: find the right foot position, then add movement once you have the pattern down.",
      idealRange: "80\u00b0\u2013100\u00b0",
      illustrationKey: "lungeForm",
    },
    "Torso Position": {
      title: "Stay Upright in Lunges",
      whatIsWrong:
        "You're leaning too far forward during lunges, which shifts load to your lower back and reduces quad activation.",
      howToFix:
        "Keep your torso vertical throughout the lunge. Engage your core and look straight ahead, not down.",
      drillTip:
        "Hold a light weight overhead during lunges \u2014 this forces you to maintain an upright posture.",
      idealRange: "< 20\u00b0 from vertical",
      illustrationKey: "lungeForm",
    },
  },
};

const fallbackGuidance: CategoryGuidance = {
  title: "Technique Issue Detected",
  whatIsWrong:
    "A recurring form issue was detected across multiple frames of your video.",
  howToFix:
    "Review the detailed occurrences below and pay attention to the frames where the issue is most severe.",
  drillTip:
    "Film yourself on your next session and compare side-by-side to spot the improvement.",
  idealRange: "See details",
  illustrationKey: "unknown",
};

export function getGuidance(sport: string, category: string): CategoryGuidance {
  return guidanceByCategory[sport]?.[category] ?? fallbackGuidance;
}
