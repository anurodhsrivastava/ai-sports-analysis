export default function KneeAngleDiagram() {
  return (
    <svg viewBox="0 0 320 180" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full" role="img" aria-label="Skiing knee angle: straight knees vs flexed knees">
      <text x="80" y="18" textAnchor="middle" className="fill-red-400 text-[13px] font-semibold">Incorrect</text>
      <text x="240" y="18" textAnchor="middle" className="fill-cyan-400 text-[13px] font-semibold">Correct</text>
      {/* Incorrect: straight legs */}
      <g stroke="#f87171" strokeWidth="3" strokeLinecap="round">
        <circle cx="80" cy="35" r="7" fill="none" />
        <line x1="80" y1="42" x2="80" y2="80" />
        <line x1="80" y1="80" x2="80" y2="120" />
        <line x1="80" y1="120" x2="80" y2="150" />
        <line x1="60" y1="153" x2="100" y2="153" strokeWidth="4" />
      </g>
      <text x="95" y="125" className="fill-red-300 text-[10px]">170&deg;</text>
      <line x1="160" y1="24" x2="160" y2="175" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
      {/* Correct: bent knees */}
      <g stroke="#22d3ee" strokeWidth="3" strokeLinecap="round">
        <circle cx="240" cy="40" r="7" fill="none" />
        <line x1="240" y1="47" x2="238" y2="82" />
        <line x1="238" y1="82" x2="250" y2="118" />
        <line x1="250" y1="118" x2="238" y2="150" />
        <line x1="218" y1="153" x2="258" y2="153" strokeWidth="4" />
      </g>
      <text x="260" y="122" className="fill-cyan-300 text-[10px]">120&deg;</text>
      <path d="M 244 108 Q 254 118 248 128" stroke="#22d3ee" strokeWidth="1.5" fill="none" strokeDasharray="3 2" />
      <text x="160" y="172" textAnchor="middle" className="fill-slate-500 text-[10px]">side view</text>
    </svg>
  );
}
