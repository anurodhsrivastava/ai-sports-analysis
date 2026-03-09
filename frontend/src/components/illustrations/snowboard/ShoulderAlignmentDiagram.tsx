export default function ShoulderAlignmentDiagram() {
  return (
    <svg viewBox="0 0 320 180" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full" role="img" aria-label="Shoulder alignment: incorrect rotated shoulders vs correct aligned shoulders">
      <text x="80" y="18" textAnchor="middle" className="fill-red-400 text-[13px] font-semibold">Incorrect</text>
      <text x="240" y="18" textAnchor="middle" className="fill-cyan-400 text-[13px] font-semibold">Correct</text>
      <g stroke="#f87171" strokeWidth="2" strokeLinecap="round">
        <rect x="40" y="130" width="80" height="16" rx="8" stroke="#f87171" strokeWidth="2" fill="none" />
        <text x="80" y="142" textAnchor="middle" className="fill-red-300 text-[9px]">board</text>
        <ellipse cx="80" cy="85" rx="12" ry="22" transform="rotate(-30 80 85)" fill="none" />
        <line x1="52" y1="72" x2="108" y2="98" strokeWidth="3" />
        <circle cx="52" cy="72" r="3" fill="#f87171" />
        <circle cx="108" cy="98" r="3" fill="#f87171" />
      </g>
      <path d="M 80 120 L 80 105" stroke="#475569" strokeWidth="1" strokeDasharray="3 2" />
      <text x="95" y="108" className="fill-red-300 text-[10px]">30&deg;</text>
      <line x1="160" y1="24" x2="160" y2="175" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
      <g stroke="#22d3ee" strokeWidth="2" strokeLinecap="round">
        <rect x="200" y="130" width="80" height="16" rx="8" stroke="#22d3ee" strokeWidth="2" fill="none" />
        <text x="240" y="142" textAnchor="middle" className="fill-cyan-300 text-[9px]">board</text>
        <ellipse cx="240" cy="85" rx="12" ry="22" fill="none" />
        <line x1="214" y1="85" x2="266" y2="85" strokeWidth="3" />
        <circle cx="214" cy="85" r="3" fill="#22d3ee" />
        <circle cx="266" cy="85" r="3" fill="#22d3ee" />
      </g>
      <path d="M 240 120 L 240 90" stroke="#475569" strokeWidth="1" strokeDasharray="3 2" />
      <text x="270" y="88" className="fill-cyan-300 text-[10px]">0&deg;</text>
      <text x="160" y="172" textAnchor="middle" className="fill-slate-500 text-[10px]">top-down view</text>
    </svg>
  );
}
