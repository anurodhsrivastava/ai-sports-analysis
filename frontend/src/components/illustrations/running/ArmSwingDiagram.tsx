export default function ArmSwingDiagram() {
  return (
    <svg viewBox="0 0 320 180" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full" role="img" aria-label="Arm swing: straight arms vs 90 degree bend">
      <text x="80" y="18" textAnchor="middle" className="fill-red-400 text-[13px] font-semibold">Too Straight</text>
      <text x="240" y="18" textAnchor="middle" className="fill-cyan-400 text-[13px] font-semibold">Correct</text>
      {/* Incorrect: arms too straight */}
      <g stroke="#f87171" strokeWidth="3" strokeLinecap="round">
        <circle cx="80" cy="38" r="7" fill="none" />
        <line x1="80" y1="45" x2="80" y2="80" />
        {/* Arms hanging straight */}
        <line x1="80" y1="55" x2="65" y2="110" />
        <line x1="80" y1="55" x2="95" y2="110" />
        {/* Torso + legs */}
        <line x1="80" y1="80" x2="80" y2="115" />
        <line x1="80" y1="115" x2="75" y2="155" />
        <line x1="75" y1="155" x2="70" y2="160" strokeWidth="2" />
      </g>
      <text x="100" y="85" className="fill-red-300 text-[10px]">150&deg;</text>
      <line x1="160" y1="24" x2="160" y2="175" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
      {/* Correct: 90 degree arm bend */}
      <g stroke="#22d3ee" strokeWidth="3" strokeLinecap="round">
        <circle cx="240" cy="38" r="7" fill="none" />
        <line x1="240" y1="45" x2="240" y2="80" />
        {/* Left arm: upper down, forearm forward at 90 */}
        <line x1="240" y1="55" x2="228" y2="78" />
        <line x1="228" y1="78" x2="230" y2="58" />
        {/* Right arm: upper down, forearm back at 90 */}
        <line x1="240" y1="55" x2="252" y2="78" />
        <line x1="252" y1="78" x2="260" y2="90" />
        {/* Torso + legs */}
        <line x1="240" y1="80" x2="240" y2="115" />
        <line x1="240" y1="115" x2="235" y2="155" />
        <line x1="235" y1="155" x2="230" y2="160" strokeWidth="2" />
      </g>
      <text x="218" y="72" className="fill-cyan-300 text-[10px]">90&deg;</text>
      <path d="M 232 68 Q 228 74 232 78" stroke="#22d3ee" strokeWidth="1.5" fill="none" strokeDasharray="3 2" />
    </svg>
  );
}
