export default function SquatDepthDiagram() {
  return (
    <svg viewBox="0 0 320 180" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full" role="img" aria-label="Squat depth: quarter squat vs parallel squat">
      <text x="80" y="18" textAnchor="middle" className="fill-red-400 text-[13px] font-semibold">Too Shallow</text>
      <text x="240" y="18" textAnchor="middle" className="fill-cyan-400 text-[13px] font-semibold">Correct Depth</text>
      {/* Incorrect: quarter squat */}
      <g stroke="#f87171" strokeWidth="3" strokeLinecap="round">
        <circle cx="80" cy="35" r="7" fill="none" />
        <line x1="80" y1="42" x2="80" y2="78" />
        {/* Hips barely bent */}
        <line x1="80" y1="78" x2="80" y2="100" />
        {/* Upper leg slightly angled */}
        <line x1="80" y1="100" x2="75" y2="125" />
        {/* Lower leg */}
        <line x1="75" y1="125" x2="75" y2="155" />
        <line x1="70" y1="158" x2="82" y2="158" strokeWidth="2" />
      </g>
      <text x="92" y="120" className="fill-red-300 text-[10px]">120&deg;</text>
      <line x1="160" y1="24" x2="160" y2="175" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
      {/* Correct: parallel squat */}
      <g stroke="#22d3ee" strokeWidth="3" strokeLinecap="round">
        <circle cx="240" cy="45" r="7" fill="none" />
        {/* Torso more upright but lower */}
        <line x1="240" y1="52" x2="238" y2="82" />
        {/* Hip crease */}
        <line x1="238" y1="82" x2="238" y2="95" />
        {/* Thigh nearly parallel (deep bend) */}
        <line x1="238" y1="95" x2="255" y2="120" />
        {/* Shin */}
        <line x1="255" y1="120" x2="245" y2="155" />
        <line x1="240" y1="158" x2="252" y2="158" strokeWidth="2" />
      </g>
      <text x="266" y="118" className="fill-cyan-300 text-[10px]">85&deg;</text>
      <path d="M 248 110 Q 258 118 252 128" stroke="#22d3ee" strokeWidth="1.5" fill="none" strokeDasharray="3 2" />
      {/* Parallel line reference */}
      <line x1="220" y1="120" x2="275" y2="120" stroke="#22d3ee" strokeWidth="0.5" strokeDasharray="2 2" opacity="0.5" />
      <text x="160" y="175" textAnchor="middle" className="fill-slate-500 text-[10px]">side view</text>
    </svg>
  );
}
