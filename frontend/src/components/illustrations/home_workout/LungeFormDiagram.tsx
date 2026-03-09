export default function LungeFormDiagram() {
  return (
    <svg viewBox="0 0 320 180" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full" role="img" aria-label="Lunge form: shallow lunge vs 90 degree lunge">
      <text x="80" y="18" textAnchor="middle" className="fill-red-400 text-[13px] font-semibold">Too Shallow</text>
      <text x="240" y="18" textAnchor="middle" className="fill-cyan-400 text-[13px] font-semibold">Correct</text>
      {/* Incorrect: shallow lunge */}
      <g stroke="#f87171" strokeWidth="3" strokeLinecap="round">
        <circle cx="80" cy="35" r="7" fill="none" />
        <line x1="80" y1="42" x2="80" y2="80" />
        {/* Hips */}
        <line x1="80" y1="80" x2="80" y2="95" />
        {/* Front leg barely bent */}
        <line x1="80" y1="95" x2="60" y2="120" />
        <line x1="60" y1="120" x2="55" y2="155" />
        <line x1="50" y1="158" x2="62" y2="158" strokeWidth="2" />
        {/* Back leg */}
        <line x1="80" y1="95" x2="100" y2="125" />
        <line x1="100" y1="125" x2="105" y2="155" />
        {/* Ground */}
        <line x1="30" y1="160" x2="130" y2="160" stroke="#475569" strokeWidth="1" />
      </g>
      <text x="48" y="125" className="fill-red-300 text-[10px]">130&deg;</text>
      <line x1="160" y1="24" x2="160" y2="175" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
      {/* Correct: 90 degree lunge */}
      <g stroke="#22d3ee" strokeWidth="3" strokeLinecap="round">
        <circle cx="240" cy="40" r="7" fill="none" />
        <line x1="240" y1="47" x2="240" y2="80" />
        {/* Hips lower */}
        <line x1="240" y1="80" x2="240" y2="100" />
        {/* Front leg at 90 degrees */}
        <line x1="240" y1="100" x2="218" y2="130" />
        <line x1="218" y1="130" x2="218" y2="155" />
        <line x1="212" y1="158" x2="225" y2="158" strokeWidth="2" />
        {/* Back leg */}
        <line x1="240" y1="100" x2="265" y2="135" />
        <line x1="265" y1="135" x2="270" y2="155" />
        {/* Ground */}
        <line x1="195" y1="160" x2="290" y2="160" stroke="#475569" strokeWidth="1" />
      </g>
      <text x="205" y="130" className="fill-cyan-300 text-[10px]">90&deg;</text>
      <path d="M 224 120 Q 218 128 222 136" stroke="#22d3ee" strokeWidth="1.5" fill="none" strokeDasharray="3 2" />
    </svg>
  );
}
