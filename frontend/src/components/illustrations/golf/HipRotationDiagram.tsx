export default function HipRotationDiagram() {
  return (
    <svg viewBox="0 0 320 180" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full" role="img" aria-label="Hip rotation: shoulder line vs hip line separation">
      <text x="80" y="18" textAnchor="middle" className="fill-red-400 text-[13px] font-semibold">No Separation</text>
      <text x="240" y="18" textAnchor="middle" className="fill-cyan-400 text-[13px] font-semibold">Good Separation</text>
      {/* Incorrect: shoulders and hips aligned (no separation) — top-down view */}
      <g strokeWidth="3" strokeLinecap="round">
        {/* Shoulder line */}
        <line x1="50" y1="60" x2="110" y2="60" stroke="#f87171" />
        <text x="80" y="55" textAnchor="middle" className="fill-red-300 text-[8px]">shoulders</text>
        {/* Hip line — same angle */}
        <line x1="55" y1="100" x2="105" y2="100" stroke="#f87171" strokeDasharray="4 2" />
        <text x="80" y="95" textAnchor="middle" className="fill-red-300 text-[8px]">hips</text>
        {/* Spine connecting them */}
        <line x1="80" y1="60" x2="80" y2="100" stroke="#f87171" strokeWidth="2" />
        {/* Angle indicator */}
        <text x="80" y="125" textAnchor="middle" className="fill-red-300 text-[10px]">0° separation</text>
      </g>
      <line x1="160" y1="24" x2="160" y2="175" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
      {/* Correct: shoulders rotated more than hips — top-down view */}
      <g strokeWidth="3" strokeLinecap="round">
        {/* Shoulder line — rotated */}
        <line x1="205" y1="50" x2="275" y2="70" stroke="#22d3ee" />
        <text x="240" y="45" textAnchor="middle" className="fill-cyan-300 text-[8px]">shoulders</text>
        {/* Hip line — less rotated */}
        <line x1="220" y1="100" x2="270" y2="100" stroke="#22d3ee" strokeDasharray="4 2" />
        <text x="245" y="95" textAnchor="middle" className="fill-cyan-300 text-[8px]">hips</text>
        {/* Spine connecting them */}
        <line x1="240" y1="60" x2="245" y2="100" stroke="#22d3ee" strokeWidth="2" />
        {/* Angle arc */}
        <path d="M 260 100 A 20 20 0 0 0 265 80" stroke="#22d3ee" strokeWidth="1" fill="none" />
        <text x="240" y="125" textAnchor="middle" className="fill-cyan-300 text-[10px]">45° separation</text>
      </g>
      <text x="80" y="145" textAnchor="middle" className="fill-red-300 text-[9px]">all-arms swing</text>
      <text x="240" y="145" textAnchor="middle" className="fill-cyan-300 text-[9px]">power from hips</text>
    </svg>
  );
}
