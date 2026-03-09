export default function SymmetryDiagram() {
  return (
    <svg viewBox="0 0 320 180" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full" role="img" aria-label="Symmetry: asymmetric vs symmetric warrior II pose">
      <text x="80" y="18" textAnchor="middle" className="fill-red-400 text-[13px] font-semibold">Asymmetric</text>
      <text x="240" y="18" textAnchor="middle" className="fill-cyan-400 text-[13px] font-semibold">Symmetric</text>
      {/* Incorrect: asymmetric warrior II */}
      <g stroke="#f87171" strokeWidth="3" strokeLinecap="round">
        <circle cx="80" cy="40" r="7" fill="none" />
        {/* Neck */}
        <line x1="80" y1="47" x2="80" y2="60" />
        {/* Left arm — drooping */}
        <line x1="80" y1="60" x2="50" y2="72" />
        <line x1="50" y1="72" x2="25" y2="80" />
        {/* Right arm — raised too high */}
        <line x1="80" y1="60" x2="108" y2="48" />
        <line x1="108" y1="48" x2="135" y2="42" />
        {/* Torso */}
        <line x1="80" y1="60" x2="80" y2="100" />
        {/* Left leg — bent */}
        <line x1="80" y1="100" x2="55" y2="130" />
        <line x1="55" y1="130" x2="45" y2="155" />
        {/* Right leg — too straight */}
        <line x1="80" y1="100" x2="105" y2="130" />
        <line x1="105" y1="130" x2="115" y2="155" />
        {/* Ground */}
        <line x1="15" y1="158" x2="145" y2="158" stroke="#475569" strokeWidth="1" />
      </g>
      {/* Angle indicators showing mismatch */}
      <text x="30" y="95" className="fill-red-300 text-[8px]">low</text>
      <text x="120" y="38" className="fill-red-300 text-[8px]">high</text>
      <line x1="160" y1="24" x2="160" y2="175" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
      {/* Correct: symmetric warrior II */}
      <g stroke="#22d3ee" strokeWidth="3" strokeLinecap="round">
        <circle cx="240" cy="40" r="7" fill="none" />
        {/* Neck */}
        <line x1="240" y1="47" x2="240" y2="60" />
        {/* Left arm — level */}
        <line x1="240" y1="60" x2="210" y2="60" />
        <line x1="210" y1="60" x2="185" y2="60" />
        {/* Right arm — level */}
        <line x1="240" y1="60" x2="270" y2="60" />
        <line x1="270" y1="60" x2="295" y2="60" />
        {/* Torso */}
        <line x1="240" y1="60" x2="240" y2="100" />
        {/* Left leg — bent ~90deg */}
        <line x1="240" y1="100" x2="215" y2="130" />
        <line x1="215" y1="130" x2="210" y2="155" />
        {/* Right leg — bent matching */}
        <line x1="240" y1="100" x2="265" y2="130" />
        <line x1="265" y1="130" x2="270" y2="155" />
        {/* Ground */}
        <line x1="175" y1="158" x2="305" y2="158" stroke="#475569" strokeWidth="1" />
      </g>
      {/* Symmetry line */}
      <line x1="240" y1="30" x2="240" y2="158" stroke="#475569" strokeWidth="1" strokeDasharray="3 2" />
      <text x="240" y="172" textAnchor="middle" className="fill-cyan-300 text-[8px]">mirror match</text>
    </svg>
  );
}
