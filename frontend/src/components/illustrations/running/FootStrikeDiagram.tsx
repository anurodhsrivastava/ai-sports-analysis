export default function FootStrikeDiagram() {
  return (
    <svg viewBox="0 0 320 180" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full" role="img" aria-label="Foot strike: heel strike vs midfoot strike">
      <text x="80" y="18" textAnchor="middle" className="fill-red-400 text-[13px] font-semibold">Overstriding</text>
      <text x="240" y="18" textAnchor="middle" className="fill-cyan-400 text-[13px] font-semibold">Correct</text>
      {/* Incorrect: heel strike, foot far ahead */}
      <g stroke="#f87171" strokeWidth="3" strokeLinecap="round">
        <circle cx="80" cy="35" r="7" fill="none" />
        <line x1="80" y1="42" x2="78" y2="75" />
        <line x1="78" y1="75" x2="80" y2="110" />
        <line x1="80" y1="110" x2="55" y2="145" />
        {/* Foot way ahead */}
        <line x1="55" y1="145" x2="40" y2="155" />
        <line x1="40" y1="155" x2="55" y2="158" strokeWidth="2" />
        {/* Ground */}
        <line x1="20" y1="160" x2="140" y2="160" stroke="#475569" strokeWidth="1" />
        {/* Vertical reference from hip */}
        <line x1="80" y1="110" x2="80" y2="160" stroke="#475569" strokeWidth="1" strokeDasharray="3 2" />
      </g>
      {/* Distance arrow */}
      <line x1="42" y1="165" x2="78" y2="165" stroke="#f87171" strokeWidth="1" />
      <text x="60" y="175" textAnchor="middle" className="fill-red-300 text-[9px]">too far ahead</text>
      <line x1="160" y1="24" x2="160" y2="175" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
      {/* Correct: midfoot under hips */}
      <g stroke="#22d3ee" strokeWidth="3" strokeLinecap="round">
        <circle cx="240" cy="35" r="7" fill="none" />
        <line x1="240" y1="42" x2="237" y2="75" />
        <line x1="237" y1="75" x2="240" y2="110" />
        <line x1="240" y1="110" x2="238" y2="145" />
        {/* Foot under hips */}
        <line x1="238" y1="145" x2="232" y2="155" />
        <line x1="232" y1="155" x2="245" y2="158" strokeWidth="2" />
        <line x1="180" y1="160" x2="300" y2="160" stroke="#475569" strokeWidth="1" />
        <line x1="240" y1="110" x2="240" y2="160" stroke="#475569" strokeWidth="1" strokeDasharray="3 2" />
      </g>
      <text x="240" y="175" textAnchor="middle" className="fill-cyan-300 text-[9px]">under hips</text>
    </svg>
  );
}
