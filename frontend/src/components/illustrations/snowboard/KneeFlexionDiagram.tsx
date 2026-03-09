export default function KneeFlexionDiagram() {
  return (
    <svg viewBox="0 0 320 180" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full" role="img" aria-label="Knee flexion: incorrect straight legs vs correct bent knees">
      <text x="80" y="18" textAnchor="middle" className="fill-red-400 text-[13px] font-semibold">Incorrect</text>
      <text x="240" y="18" textAnchor="middle" className="fill-cyan-400 text-[13px] font-semibold">Correct</text>
      <g stroke="#f87171" strokeWidth="3" strokeLinecap="round">
        <circle cx="80" cy="40" r="8" fill="none" />
        <line x1="80" y1="48" x2="80" y2="90" />
        <line x1="80" y1="90" x2="80" y2="130" />
        <line x1="80" y1="130" x2="80" y2="165" />
        <line x1="55" y1="168" x2="105" y2="168" strokeWidth="4" />
        <line x1="80" y1="60" x2="60" y2="78" />
        <line x1="80" y1="60" x2="100" y2="78" />
      </g>
      <text x="92" y="134" className="fill-red-300 text-[10px]">175&deg;</text>
      <line x1="160" y1="24" x2="160" y2="175" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
      <g stroke="#22d3ee" strokeWidth="3" strokeLinecap="round">
        <circle cx="240" cy="46" r="8" fill="none" />
        <line x1="240" y1="54" x2="236" y2="92" />
        <line x1="236" y1="92" x2="248" y2="128" />
        <line x1="248" y1="128" x2="236" y2="165" />
        <line x1="211" y1="168" x2="261" y2="168" strokeWidth="4" />
        <line x1="238" y1="66" x2="218" y2="82" />
        <line x1="238" y1="66" x2="258" y2="82" />
      </g>
      <text x="256" y="132" className="fill-cyan-300 text-[10px]">45&deg;</text>
      <path d="M 242 118 Q 252 128 244 138" stroke="#22d3ee" strokeWidth="1.5" fill="none" strokeDasharray="3 2" />
    </svg>
  );
}
