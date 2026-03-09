export default function AlignmentDiagram() {
  return (
    <svg viewBox="0 0 320 180" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full" role="img" aria-label="Spine alignment: curved vs straight">
      <text x="80" y="18" textAnchor="middle" className="fill-red-400 text-[13px] font-semibold">Misaligned</text>
      <text x="240" y="18" textAnchor="middle" className="fill-cyan-400 text-[13px] font-semibold">Aligned</text>
      {/* Incorrect: curved spine */}
      <g stroke="#f87171" strokeWidth="3" strokeLinecap="round">
        <circle cx="75" cy="35" r="7" fill="none" />
        <line x1="75" y1="42" x2="78" y2="60" />
        <line x1="78" y1="60" x2="85" y2="85" />
        <line x1="85" y1="85" x2="82" y2="110" />
        <line x1="82" y1="110" x2="78" y2="130" />
        <line x1="78" y1="130" x2="75" y2="155" />
        {/* Arms */}
        <line x1="78" y1="60" x2="55" y2="80" />
        <line x1="78" y1="60" x2="100" y2="80" />
        {/* Legs */}
        <line x1="78" y1="130" x2="65" y2="155" />
        <line x1="78" y1="130" x2="90" y2="155" />
        {/* Ground */}
        <line x1="30" y1="160" x2="130" y2="160" stroke="#475569" strokeWidth="1" />
      </g>
      {/* Curved spine indicator */}
      <path d="M 100 35 Q 108 90 100 130" stroke="#f87171" strokeWidth="1" strokeDasharray="3 2" fill="none" />
      <text x="115" y="85" className="fill-red-300 text-[9px]">curved</text>
      <line x1="160" y1="24" x2="160" y2="175" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
      {/* Correct: straight spine */}
      <g stroke="#22d3ee" strokeWidth="3" strokeLinecap="round">
        <circle cx="240" cy="35" r="7" fill="none" />
        <line x1="240" y1="42" x2="240" y2="60" />
        <line x1="240" y1="60" x2="240" y2="85" />
        <line x1="240" y1="85" x2="240" y2="110" />
        <line x1="240" y1="110" x2="240" y2="130" />
        <line x1="240" y1="130" x2="240" y2="155" />
        {/* Arms */}
        <line x1="240" y1="60" x2="218" y2="80" />
        <line x1="240" y1="60" x2="262" y2="80" />
        {/* Legs */}
        <line x1="240" y1="130" x2="228" y2="155" />
        <line x1="240" y1="130" x2="252" y2="155" />
        {/* Ground */}
        <line x1="190" y1="160" x2="290" y2="160" stroke="#475569" strokeWidth="1" />
      </g>
      {/* Vertical reference line */}
      <line x1="240" y1="30" x2="240" y2="160" stroke="#475569" strokeWidth="1" strokeDasharray="3 2" />
      <text x="255" y="85" className="fill-cyan-300 text-[9px]">stacked</text>
    </svg>
  );
}
