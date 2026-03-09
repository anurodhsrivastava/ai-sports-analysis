export default function JointAnglesDiagram() {
  return (
    <svg viewBox="0 0 320 180" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full" role="img" aria-label="Knee joint: hyperextended vs micro-bend">
      <text x="80" y="18" textAnchor="middle" className="fill-red-400 text-[13px] font-semibold">Hyperextended</text>
      <text x="240" y="18" textAnchor="middle" className="fill-cyan-400 text-[13px] font-semibold">Micro-bend</text>
      {/* Incorrect: hyperextended knee — side view detail */}
      <g stroke="#f87171" strokeWidth="3" strokeLinecap="round">
        {/* Hip */}
        <circle cx="80" cy="40" r="4" fill="#f87171" />
        {/* Thigh */}
        <line x1="80" y1="44" x2="78" y2="80" />
        {/* Knee — pushed back */}
        <circle cx="78" cy="80" r="4" fill="none" />
        {/* Shin — angled forward past straight */}
        <line x1="78" y1="84" x2="72" y2="140" />
        {/* Ankle */}
        <circle cx="72" cy="140" r="3" fill="none" />
        {/* Foot */}
        <line x1="72" y1="143" x2="60" y2="155" />
        <line x1="60" y1="155" x2="85" y2="155" strokeWidth="2" />
        {/* Ground */}
        <line x1="30" y1="158" x2="130" y2="158" stroke="#475569" strokeWidth="1" />
      </g>
      {/* Angle arc showing >180 */}
      <path d="M 80 60 Q 68 80 72 100" stroke="#f87171" strokeWidth="1" fill="none" />
      <text x="58" y="82" className="fill-red-300 text-[9px]">&gt;185°</text>
      <line x1="160" y1="24" x2="160" y2="175" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
      {/* Correct: slight micro-bend — side view detail */}
      <g stroke="#22d3ee" strokeWidth="3" strokeLinecap="round">
        {/* Hip */}
        <circle cx="240" cy="40" r="4" fill="#22d3ee" />
        {/* Thigh */}
        <line x1="240" y1="44" x2="240" y2="80" />
        {/* Knee — slight bend */}
        <circle cx="240" cy="80" r="4" fill="none" />
        {/* Shin — nearly straight with slight bend */}
        <line x1="240" y1="84" x2="238" y2="140" />
        {/* Ankle */}
        <circle cx="238" cy="140" r="3" fill="none" />
        {/* Foot */}
        <line x1="238" y1="143" x2="226" y2="155" />
        <line x1="226" y1="155" x2="252" y2="155" strokeWidth="2" />
        {/* Ground */}
        <line x1="190" y1="158" x2="290" y2="158" stroke="#475569" strokeWidth="1" />
      </g>
      {/* Angle arc showing ~175 */}
      <path d="M 240 60 Q 232 80 238 100" stroke="#22d3ee" strokeWidth="1" fill="none" />
      <text x="220" y="82" className="fill-cyan-300 text-[9px]">~175°</text>
    </svg>
  );
}
