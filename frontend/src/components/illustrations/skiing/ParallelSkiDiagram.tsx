export default function ParallelSkiDiagram() {
  return (
    <svg viewBox="0 0 320 180" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full" role="img" aria-label="Ski parallelism: diverging skis vs parallel skis">
      <text x="80" y="18" textAnchor="middle" className="fill-red-400 text-[13px] font-semibold">Incorrect</text>
      <text x="240" y="18" textAnchor="middle" className="fill-cyan-400 text-[13px] font-semibold">Correct</text>
      {/* Incorrect: diverging skis (top-down view) */}
      <g stroke="#f87171" strokeWidth="3" strokeLinecap="round">
        {/* Body outline */}
        <ellipse cx="80" cy="70" rx="10" ry="18" fill="none" strokeWidth="2" />
        {/* Left ski - angled out */}
        <line x1="55" y1="100" x2="40" y2="165" strokeWidth="4" />
        {/* Right ski - angled out */}
        <line x1="105" y1="100" x2="120" y2="165" strokeWidth="4" />
        {/* Legs */}
        <line x1="75" y1="88" x2="55" y2="100" />
        <line x1="85" y1="88" x2="105" y2="100" />
      </g>
      <text x="80" y="155" textAnchor="middle" className="fill-red-300 text-[10px]">20&deg; apart</text>
      <line x1="160" y1="24" x2="160" y2="175" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
      {/* Correct: parallel skis */}
      <g stroke="#22d3ee" strokeWidth="3" strokeLinecap="round">
        <ellipse cx="240" cy="70" rx="10" ry="18" fill="none" strokeWidth="2" />
        {/* Left ski - parallel */}
        <line x1="228" y1="100" x2="228" y2="165" strokeWidth="4" />
        {/* Right ski - parallel */}
        <line x1="252" y1="100" x2="252" y2="165" strokeWidth="4" />
        {/* Legs */}
        <line x1="235" y1="88" x2="228" y2="100" />
        <line x1="245" y1="88" x2="252" y2="100" />
      </g>
      <text x="240" y="155" textAnchor="middle" className="fill-cyan-300 text-[10px]">parallel</text>
      <text x="160" y="175" textAnchor="middle" className="fill-slate-500 text-[10px]">top-down view</text>
    </svg>
  );
}
