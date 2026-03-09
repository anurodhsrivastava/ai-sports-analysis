export default function PolePositionDiagram() {
  return (
    <svg viewBox="0 0 320 180" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full" role="img" aria-label="Pole position: trailing poles vs forward poles">
      <text x="80" y="18" textAnchor="middle" className="fill-red-400 text-[13px] font-semibold">Incorrect</text>
      <text x="240" y="18" textAnchor="middle" className="fill-cyan-400 text-[13px] font-semibold">Correct</text>
      {/* Incorrect: poles trailing behind */}
      <g stroke="#f87171" strokeWidth="3" strokeLinecap="round">
        <circle cx="80" cy="38" r="7" fill="none" />
        <line x1="80" y1="45" x2="80" y2="85" />
        <line x1="80" y1="85" x2="80" y2="115" />
        <line x1="80" y1="115" x2="80" y2="150" />
        {/* Skis */}
        <line x1="65" y1="153" x2="95" y2="153" strokeWidth="4" />
        {/* Arms trailing back */}
        <line x1="80" y1="58" x2="110" y2="85" />
        <line x1="80" y1="58" x2="50" y2="85" />
        {/* Poles trailing */}
        <line x1="110" y1="85" x2="125" y2="145" stroke="#f87171" strokeWidth="2" />
        <line x1="50" y1="85" x2="35" y2="145" stroke="#f87171" strokeWidth="2" />
      </g>
      <text x="80" y="170" textAnchor="middle" className="fill-red-300 text-[10px]">poles trailing</text>
      <line x1="160" y1="24" x2="160" y2="175" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
      {/* Correct: poles forward */}
      <g stroke="#22d3ee" strokeWidth="3" strokeLinecap="round">
        <circle cx="240" cy="42" r="7" fill="none" />
        <line x1="240" y1="49" x2="238" y2="85" />
        <line x1="238" y1="85" x2="244" y2="115" />
        <line x1="244" y1="115" x2="240" y2="150" />
        {/* Skis */}
        <line x1="225" y1="153" x2="255" y2="153" strokeWidth="4" />
        {/* Arms forward */}
        <line x1="238" y1="62" x2="220" y2="72" />
        <line x1="238" y1="62" x2="256" y2="72" />
        {/* Poles forward and down */}
        <line x1="220" y1="72" x2="215" y2="120" stroke="#22d3ee" strokeWidth="2" />
        <line x1="256" y1="72" x2="261" y2="120" stroke="#22d3ee" strokeWidth="2" />
      </g>
      <text x="240" y="170" textAnchor="middle" className="fill-cyan-300 text-[10px]">hands forward</text>
    </svg>
  );
}
