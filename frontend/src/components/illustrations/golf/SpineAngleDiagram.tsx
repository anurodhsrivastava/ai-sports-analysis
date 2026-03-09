export default function SpineAngleDiagram() {
  return (
    <svg viewBox="0 0 320 180" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full" role="img" aria-label="Spine angle: too upright vs correct forward tilt">
      <text x="80" y="18" textAnchor="middle" className="fill-red-400 text-[13px] font-semibold">Too Upright</text>
      <text x="240" y="18" textAnchor="middle" className="fill-cyan-400 text-[13px] font-semibold">Correct (30-45°)</text>
      {/* Incorrect: too upright spine */}
      <g stroke="#f87171" strokeWidth="3" strokeLinecap="round">
        <circle cx="80" cy="35" r="7" fill="none" />
        <line x1="80" y1="42" x2="80" y2="75" />
        {/* Nearly vertical spine */}
        <line x1="80" y1="75" x2="82" y2="115" />
        {/* Hips */}
        <line x1="70" y1="115" x2="94" y2="115" />
        {/* Legs */}
        <line x1="70" y1="115" x2="65" y2="150" />
        <line x1="94" y1="115" x2="99" y2="150" />
        {/* Ground */}
        <line x1="20" y1="155" x2="140" y2="155" stroke="#475569" strokeWidth="1" />
        {/* Vertical reference */}
        <line x1="80" y1="42" x2="80" y2="120" stroke="#475569" strokeWidth="1" strokeDasharray="3 2" />
      </g>
      {/* Angle arc - small */}
      <text x="92" y="95" className="fill-red-300 text-[9px]">~15°</text>
      <line x1="160" y1="24" x2="160" y2="175" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
      {/* Correct: 30-45° forward tilt */}
      <g stroke="#22d3ee" strokeWidth="3" strokeLinecap="round">
        <circle cx="225" cy="40" r="7" fill="none" />
        <line x1="225" y1="47" x2="228" y2="72" />
        {/* Spine angled forward */}
        <line x1="228" y1="72" x2="248" y2="115" />
        {/* Hips */}
        <line x1="238" y1="115" x2="262" y2="115" />
        {/* Legs */}
        <line x1="238" y1="115" x2="232" y2="150" />
        <line x1="262" y1="115" x2="268" y2="150" />
        <line x1="180" y1="155" x2="300" y2="155" stroke="#475569" strokeWidth="1" />
        {/* Vertical reference from neck */}
        <line x1="228" y1="47" x2="228" y2="120" stroke="#475569" strokeWidth="1" strokeDasharray="3 2" />
      </g>
      <text x="245" y="95" className="fill-cyan-300 text-[9px]">35°</text>
      <text x="80" y="172" textAnchor="middle" className="fill-red-300 text-[9px]">no tilt</text>
      <text x="240" y="172" textAnchor="middle" className="fill-cyan-300 text-[9px]">athletic posture</text>
    </svg>
  );
}
