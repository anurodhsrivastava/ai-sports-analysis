export default function HipAlignmentDiagram() {
  return (
    <svg viewBox="0 0 320 180" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full" role="img" aria-label="Hip alignment: rotated hips vs square hips">
      <text x="80" y="18" textAnchor="middle" className="fill-red-400 text-[13px] font-semibold">Incorrect</text>
      <text x="240" y="18" textAnchor="middle" className="fill-cyan-400 text-[13px] font-semibold">Correct</text>
      {/* Incorrect: rotated body (top-down) */}
      <g stroke="#f87171" strokeWidth="2" strokeLinecap="round">
        {/* Skis going straight */}
        <line x1="65" y1="140" x2="65" y2="165" strokeWidth="3" />
        <line x1="95" y1="140" x2="95" y2="165" strokeWidth="3" />
        {/* Body rotated */}
        <ellipse cx="80" cy="80" rx="12" ry="20" transform="rotate(-35 80 80)" fill="none" />
        {/* Shoulder line rotated */}
        <line x1="55" y1="68" x2="105" y2="92" strokeWidth="3" />
        <circle cx="55" cy="68" r="3" fill="#f87171" />
        <circle cx="105" cy="92" r="3" fill="#f87171" />
        {/* Direction arrow */}
        <line x1="80" y1="110" x2="80" y2="135" stroke="#475569" strokeWidth="1" strokeDasharray="3 2" />
        <polygon points="77,135 83,135 80,140" fill="#475569" />
      </g>
      <text x="80" y="172" textAnchor="middle" className="fill-red-300 text-[10px]">35&deg; rotated</text>
      <line x1="160" y1="24" x2="160" y2="175" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
      {/* Correct: square to fall line */}
      <g stroke="#22d3ee" strokeWidth="2" strokeLinecap="round">
        {/* Skis */}
        <line x1="225" y1="140" x2="225" y2="165" strokeWidth="3" />
        <line x1="255" y1="140" x2="255" y2="165" strokeWidth="3" />
        {/* Body aligned */}
        <ellipse cx="240" cy="80" rx="12" ry="20" fill="none" />
        {/* Shoulder line square */}
        <line x1="218" y1="80" x2="262" y2="80" strokeWidth="3" />
        <circle cx="218" cy="80" r="3" fill="#22d3ee" />
        <circle cx="262" cy="80" r="3" fill="#22d3ee" />
        <line x1="240" y1="110" x2="240" y2="135" stroke="#475569" strokeWidth="1" strokeDasharray="3 2" />
        <polygon points="237,135 243,135 240,140" fill="#475569" />
      </g>
      <text x="240" y="172" textAnchor="middle" className="fill-cyan-300 text-[10px]">square to fall line</text>
    </svg>
  );
}
