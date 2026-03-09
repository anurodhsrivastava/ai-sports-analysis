export default function BalanceDiagram() {
  return (
    <svg viewBox="0 0 320 180" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full" role="img" aria-label="Weight distribution: uneven vs even">
      <text x="80" y="18" textAnchor="middle" className="fill-red-400 text-[13px] font-semibold">Uneven</text>
      <text x="240" y="18" textAnchor="middle" className="fill-cyan-400 text-[13px] font-semibold">Balanced</text>
      {/* Incorrect: uneven weight — tree pose leaning */}
      <g stroke="#f87171" strokeWidth="3" strokeLinecap="round">
        <circle cx="75" cy="35" r="7" fill="none" />
        <line x1="75" y1="42" x2="73" y2="65" />
        {/* Arms up */}
        <line x1="73" y1="55" x2="55" y2="40" />
        <line x1="73" y1="55" x2="90" y2="40" />
        {/* Torso */}
        <line x1="73" y1="65" x2="70" y2="100" />
        {/* Standing leg */}
        <line x1="70" y1="100" x2="65" y2="135" />
        <line x1="65" y1="135" x2="62" y2="155" />
        {/* Bent leg */}
        <line x1="70" y1="100" x2="90" y2="115" />
        <line x1="90" y1="115" x2="80" y2="105" />
        {/* Ground */}
        <line x1="30" y1="160" x2="130" y2="160" stroke="#475569" strokeWidth="1" />
      </g>
      {/* Uneven weight arrows */}
      <line x1="62" y1="160" x2="62" y2="170" stroke="#f87171" strokeWidth="2" />
      <polygon points="58,170 66,170 62,176" fill="#f87171" />
      <text x="62" y="175" textAnchor="middle" className="fill-red-300 text-[8px]" dy="7">heavy</text>
      <text x="90" y="163" className="fill-red-300 text-[8px]">light</text>
      <line x1="160" y1="24" x2="160" y2="175" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
      {/* Correct: balanced tree pose */}
      <g stroke="#22d3ee" strokeWidth="3" strokeLinecap="round">
        <circle cx="240" cy="35" r="7" fill="none" />
        <line x1="240" y1="42" x2="240" y2="65" />
        {/* Arms up */}
        <line x1="240" y1="55" x2="222" y2="40" />
        <line x1="240" y1="55" x2="258" y2="40" />
        {/* Torso */}
        <line x1="240" y1="65" x2="240" y2="100" />
        {/* Standing leg */}
        <line x1="240" y1="100" x2="240" y2="135" />
        <line x1="240" y1="135" x2="240" y2="155" />
        {/* Bent leg */}
        <line x1="240" y1="100" x2="258" y2="115" />
        <line x1="258" y1="115" x2="248" y2="105" />
        {/* Ground */}
        <line x1="190" y1="160" x2="290" y2="160" stroke="#475569" strokeWidth="1" />
      </g>
      {/* Even weight arrows */}
      <line x1="240" y1="160" x2="240" y2="170" stroke="#22d3ee" strokeWidth="2" />
      <polygon points="236,170 244,170 240,176" fill="#22d3ee" />
      <text x="240" y="175" textAnchor="middle" className="fill-cyan-300 text-[8px]" dy="7">centered</text>
    </svg>
  );
}
