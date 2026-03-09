export default function PlankAlignmentDiagram() {
  return (
    <svg viewBox="0 0 320 180" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full" role="img" aria-label="Plank alignment: sagging hips vs straight body">
      <text x="80" y="18" textAnchor="middle" className="fill-red-400 text-[13px] font-semibold">Sagging</text>
      <text x="240" y="18" textAnchor="middle" className="fill-cyan-400 text-[13px] font-semibold">Correct</text>
      {/* Incorrect: sagging plank */}
      <g stroke="#f87171" strokeWidth="3" strokeLinecap="round">
        <circle cx="30" cy="68" r="5" fill="none" />
        {/* Upper body */}
        <line x1="35" y1="70" x2="60" y2="72" />
        {/* Sagging mid-section */}
        <line x1="60" y1="72" x2="85" y2="90" />
        {/* Lower body back up */}
        <line x1="85" y1="90" x2="130" y2="78" />
        {/* Arms */}
        <line x1="45" y1="72" x2="45" y2="105" />
        {/* Ground */}
        <line x1="20" y1="108" x2="140" y2="108" stroke="#475569" strokeWidth="1" />
        {/* Ideal line reference */}
        <line x1="30" y1="70" x2="130" y2="70" stroke="#f87171" strokeWidth="0.5" strokeDasharray="2 2" opacity="0.4" />
      </g>
      <text x="85" y="100" className="fill-red-300 text-[10px]">sag</text>
      <line x1="160" y1="24" x2="160" y2="175" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
      {/* Correct: straight plank */}
      <g stroke="#22d3ee" strokeWidth="3" strokeLinecap="round">
        <circle cx="190" cy="78" r="5" fill="none" />
        {/* Straight body line */}
        <line x1="195" y1="80" x2="240" y2="82" />
        <line x1="240" y1="82" x2="290" y2="84" />
        {/* Arms */}
        <line x1="205" y1="81" x2="205" y2="115" />
        {/* Ground */}
        <line x1="180" y1="118" x2="300" y2="118" stroke="#475569" strokeWidth="1" />
        {/* Straight reference line */}
        <line x1="190" y1="80" x2="290" y2="80" stroke="#22d3ee" strokeWidth="0.5" strokeDasharray="2 2" opacity="0.4" />
      </g>
      <text x="240" y="75" className="fill-cyan-300 text-[10px]">straight line</text>
      <text x="160" y="160" textAnchor="middle" className="fill-slate-500 text-[10px]">side view</text>
    </svg>
  );
}
