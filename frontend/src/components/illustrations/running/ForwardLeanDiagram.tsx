export default function ForwardLeanDiagram() {
  return (
    <svg viewBox="0 0 320 180" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full" role="img" aria-label="Forward lean: too upright vs slight forward lean">
      <text x="80" y="18" textAnchor="middle" className="fill-red-400 text-[13px] font-semibold">Too Upright</text>
      <text x="240" y="18" textAnchor="middle" className="fill-cyan-400 text-[13px] font-semibold">Correct Lean</text>
      {/* Incorrect: perfectly vertical */}
      <g stroke="#f87171" strokeWidth="3" strokeLinecap="round">
        <circle cx="80" cy="35" r="7" fill="none" />
        <line x1="80" y1="42" x2="80" y2="85" />
        <line x1="80" y1="85" x2="80" y2="115" />
        <line x1="80" y1="115" x2="72" y2="150" />
        <line x1="72" y1="150" x2="68" y2="158" strokeWidth="2" />
        {/* Ground */}
        <line x1="40" y1="160" x2="120" y2="160" stroke="#475569" strokeWidth="1" />
        {/* Vertical reference */}
        <line x1="80" y1="25" x2="80" y2="160" stroke="#475569" strokeWidth="1" strokeDasharray="3 2" />
      </g>
      <text x="92" y="55" className="fill-red-300 text-[10px]">0&deg;</text>
      <line x1="160" y1="24" x2="160" y2="175" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
      {/* Correct: slight forward lean */}
      <g stroke="#22d3ee" strokeWidth="3" strokeLinecap="round">
        <circle cx="246" cy="33" r="7" fill="none" />
        <line x1="245" y1="40" x2="241" y2="78" />
        <line x1="241" y1="78" x2="238" y2="112" />
        <line x1="238" y1="112" x2="234" y2="148" />
        <line x1="234" y1="148" x2="228" y2="158" strokeWidth="2" />
        <line x1="200" y1="160" x2="280" y2="160" stroke="#475569" strokeWidth="1" />
        {/* Vertical reference */}
        <line x1="238" y1="25" x2="238" y2="160" stroke="#475569" strokeWidth="1" strokeDasharray="3 2" />
      </g>
      <text x="258" y="55" className="fill-cyan-300 text-[10px]">10&deg;</text>
      <path d="M 238 40 Q 244 42 246 33" stroke="#22d3ee" strokeWidth="1.5" fill="none" strokeDasharray="3 2" />
      <text x="160" y="175" textAnchor="middle" className="fill-slate-500 text-[10px]">side view</text>
    </svg>
  );
}
