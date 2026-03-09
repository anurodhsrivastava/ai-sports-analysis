export default function StanceWidthDiagram() {
  return (
    <svg viewBox="0 0 320 180" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full" role="img" aria-label="Stance width: incorrect narrow stance vs correct shoulder-width stance">
      <text x="80" y="18" textAnchor="middle" className="fill-red-400 text-[13px] font-semibold">Incorrect</text>
      <text x="240" y="18" textAnchor="middle" className="fill-cyan-400 text-[13px] font-semibold">Correct</text>
      <g stroke="#f87171" strokeWidth="3" strokeLinecap="round">
        <circle cx="80" cy="36" r="8" fill="none" />
        <line x1="80" y1="44" x2="80" y2="85" />
        <line x1="80" y1="56" x2="62" y2="75" />
        <line x1="80" y1="56" x2="98" y2="75" />
        <line x1="72" y1="85" x2="88" y2="85" />
        <line x1="72" y1="85" x2="72" y2="130" />
        <line x1="72" y1="130" x2="72" y2="155" />
        <line x1="88" y1="85" x2="88" y2="130" />
        <line x1="88" y1="130" x2="88" y2="155" />
        <line x1="50" y1="158" x2="110" y2="158" strokeWidth="4" />
        <line x1="72" y1="155" x2="72" y2="162" strokeWidth="2" />
        <line x1="88" y1="155" x2="88" y2="162" strokeWidth="2" />
      </g>
      <line x1="72" y1="170" x2="88" y2="170" stroke="#f87171" strokeWidth="1" />
      <text x="80" y="178" textAnchor="middle" className="fill-red-300 text-[9px]">narrow</text>
      <line x1="62" y1="28" x2="98" y2="28" stroke="#475569" strokeWidth="1" strokeDasharray="2 2" />
      <line x1="160" y1="24" x2="160" y2="175" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
      <g stroke="#22d3ee" strokeWidth="3" strokeLinecap="round">
        <circle cx="240" cy="36" r="8" fill="none" />
        <line x1="240" y1="44" x2="240" y2="85" />
        <line x1="240" y1="56" x2="218" y2="75" />
        <line x1="240" y1="56" x2="262" y2="75" />
        <line x1="224" y1="85" x2="256" y2="85" />
        <line x1="224" y1="85" x2="220" y2="130" />
        <line x1="220" y1="130" x2="220" y2="155" />
        <line x1="256" y1="85" x2="260" y2="130" />
        <line x1="260" y1="130" x2="260" y2="155" />
        <line x1="200" y1="158" x2="280" y2="158" strokeWidth="4" />
        <line x1="220" y1="155" x2="220" y2="162" strokeWidth="2" />
        <line x1="260" y1="155" x2="260" y2="162" strokeWidth="2" />
      </g>
      <line x1="220" y1="170" x2="260" y2="170" stroke="#22d3ee" strokeWidth="1" />
      <text x="240" y="178" textAnchor="middle" className="fill-cyan-300 text-[9px]">shoulder width</text>
      <line x1="218" y1="28" x2="262" y2="28" stroke="#475569" strokeWidth="1" strokeDasharray="2 2" />
    </svg>
  );
}
