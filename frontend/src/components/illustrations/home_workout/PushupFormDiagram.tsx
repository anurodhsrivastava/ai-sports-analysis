export default function PushupFormDiagram() {
  return (
    <svg viewBox="0 0 320 180" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full" role="img" aria-label="Push-up form: partial vs full range">
      <text x="80" y="18" textAnchor="middle" className="fill-red-400 text-[13px] font-semibold">Partial Range</text>
      <text x="240" y="18" textAnchor="middle" className="fill-cyan-400 text-[13px] font-semibold">Full Range</text>
      {/* Incorrect: arms barely bent */}
      <g stroke="#f87171" strokeWidth="3" strokeLinecap="round">
        {/* Body line */}
        <circle cx="30" cy="75" r="5" fill="none" />
        <line x1="35" y1="77" x2="90" y2="80" />
        <line x1="90" y1="80" x2="130" y2="83" />
        {/* Arms barely bent */}
        <line x1="55" y1="80" x2="52" y2="100" />
        <line x1="52" y1="100" x2="55" y2="115" />
        {/* Ground */}
        <line x1="20" y1="118" x2="140" y2="118" stroke="#475569" strokeWidth="1" />
      </g>
      <text x="42" y="100" className="fill-red-300 text-[10px]">140&deg;</text>
      <line x1="160" y1="24" x2="160" y2="175" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
      {/* Correct: chest near ground */}
      <g stroke="#22d3ee" strokeWidth="3" strokeLinecap="round">
        <circle cx="190" cy="105" r="5" fill="none" />
        <line x1="195" y1="107" x2="250" y2="108" />
        <line x1="250" y1="108" x2="290" y2="110" />
        {/* Arms at 90 degrees */}
        <line x1="215" y1="108" x2="218" y2="130" />
        <line x1="218" y1="130" x2="210" y2="148" />
        {/* Ground */}
        <line x1="180" y1="150" x2="300" y2="150" stroke="#475569" strokeWidth="1" />
      </g>
      <text x="226" y="132" className="fill-cyan-300 text-[10px]">90&deg;</text>
      <path d="M 214 120 Q 220 128 216 136" stroke="#22d3ee" strokeWidth="1.5" fill="none" strokeDasharray="3 2" />
      <text x="160" y="170" textAnchor="middle" className="fill-slate-500 text-[10px]">side view</text>
    </svg>
  );
}
