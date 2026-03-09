export default function HeadMovementDiagram() {
  return (
    <svg viewBox="0 0 320 180" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full" role="img" aria-label="Head movement: swaying laterally vs staying centered">
      <text x="80" y="18" textAnchor="middle" className="fill-red-400 text-[13px] font-semibold">Swaying</text>
      <text x="240" y="18" textAnchor="middle" className="fill-cyan-400 text-[13px] font-semibold">Centered</text>
      {/* Incorrect: head swaying laterally — front view */}
      <g stroke="#f87171" strokeWidth="3" strokeLinecap="round">
        {/* Head moved to the right */}
        <circle cx="95" cy="40" r="7" fill="none" />
        {/* Ghost head in original position */}
        <circle cx="75" cy="40" r="7" fill="none" stroke="#f8717155" strokeDasharray="3 2" />
        {/* Sway arrow */}
        <line x1="75" y1="35" x2="93" y2="35" stroke="#f87171" strokeWidth="1.5" />
        <line x1="90" y1="32" x2="93" y2="35" stroke="#f87171" strokeWidth="1.5" />
        <line x1="90" y1="38" x2="93" y2="35" stroke="#f87171" strokeWidth="1.5" />
        {/* Body */}
        <line x1="95" y1="47" x2="80" y2="80" />
        {/* Torso */}
        <line x1="80" y1="80" x2="80" y2="115" />
        {/* Hips */}
        <line x1="65" y1="115" x2="95" y2="115" />
        {/* Legs */}
        <line x1="65" y1="115" x2="60" y2="150" />
        <line x1="95" y1="115" x2="100" y2="150" />
        {/* Ground */}
        <line x1="20" y1="155" x2="140" y2="155" stroke="#475569" strokeWidth="1" />
        {/* Vertical reference from hip center */}
        <line x1="80" y1="30" x2="80" y2="155" stroke="#475569" strokeWidth="1" strokeDasharray="3 2" />
      </g>
      <text x="80" y="170" textAnchor="middle" className="fill-red-300 text-[9px]">head off-center</text>
      <line x1="160" y1="24" x2="160" y2="175" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
      {/* Correct: head stays centered — front view */}
      <g stroke="#22d3ee" strokeWidth="3" strokeLinecap="round">
        {/* Head centered */}
        <circle cx="240" cy="40" r="7" fill="none" />
        {/* Body straight */}
        <line x1="240" y1="47" x2="240" y2="80" />
        {/* Torso */}
        <line x1="240" y1="80" x2="240" y2="115" />
        {/* Hips */}
        <line x1="225" y1="115" x2="255" y2="115" />
        {/* Legs */}
        <line x1="225" y1="115" x2="220" y2="150" />
        <line x1="255" y1="115" x2="260" y2="150" />
        <line x1="180" y1="155" x2="300" y2="155" stroke="#475569" strokeWidth="1" />
        {/* Vertical reference — head aligned */}
        <line x1="240" y1="30" x2="240" y2="155" stroke="#475569" strokeWidth="1" strokeDasharray="3 2" />
      </g>
      <text x="240" y="170" textAnchor="middle" className="fill-cyan-300 text-[9px]">steady pivot</text>
    </svg>
  );
}
