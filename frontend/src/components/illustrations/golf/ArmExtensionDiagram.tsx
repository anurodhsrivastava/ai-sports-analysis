export default function ArmExtensionDiagram() {
  return (
    <svg viewBox="0 0 320 180" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full" role="img" aria-label="Arm extension: chicken wing vs straight lead arm at impact">
      <text x="80" y="18" textAnchor="middle" className="fill-red-400 text-[13px] font-semibold">Chicken Wing</text>
      <text x="240" y="18" textAnchor="middle" className="fill-cyan-400 text-[13px] font-semibold">Correct</text>
      {/* Incorrect: bent lead arm (chicken wing) */}
      <g stroke="#f87171" strokeWidth="3" strokeLinecap="round">
        <circle cx="85" cy="40" r="7" fill="none" />
        <line x1="85" y1="47" x2="85" y2="75" />
        {/* Shoulder */}
        <line x1="85" y1="75" x2="65" y2="75" />
        {/* Bent lead arm — elbow out */}
        <line x1="65" y1="75" x2="50" y2="100" />
        <line x1="50" y1="100" x2="45" y2="130" />
        {/* Angle marker at elbow */}
        <path d="M 58 83 A 10 10 0 0 0 50 90" stroke="#f87171" strokeWidth="1" fill="none" />
        {/* Club */}
        <line x1="45" y1="130" x2="40" y2="155" stroke="#f87171" strokeWidth="2" />
        {/* Ground */}
        <line x1="20" y1="160" x2="140" y2="160" stroke="#475569" strokeWidth="1" />
      </g>
      <text x="38" y="105" className="fill-red-300 text-[9px]">130°</text>
      <line x1="160" y1="24" x2="160" y2="175" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
      {/* Correct: straight lead arm */}
      <g stroke="#22d3ee" strokeWidth="3" strokeLinecap="round">
        <circle cx="245" cy="40" r="7" fill="none" />
        <line x1="245" y1="47" x2="245" y2="75" />
        {/* Shoulder */}
        <line x1="245" y1="75" x2="225" y2="75" />
        {/* Nearly straight lead arm */}
        <line x1="225" y1="75" x2="210" y2="105" />
        <line x1="210" y1="105" x2="200" y2="135" />
        {/* Club */}
        <line x1="200" y1="135" x2="195" y2="155" stroke="#22d3ee" strokeWidth="2" />
        <line x1="180" y1="160" x2="300" y2="160" stroke="#475569" strokeWidth="1" />
      </g>
      <text x="198" y="110" className="fill-cyan-300 text-[9px]">170°</text>
      <text x="80" y="175" textAnchor="middle" className="fill-red-300 text-[9px]">bent = power loss</text>
      <text x="240" y="175" textAnchor="middle" className="fill-cyan-300 text-[9px]">straight = consistent</text>
    </svg>
  );
}
