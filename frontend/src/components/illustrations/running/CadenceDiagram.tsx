export default function CadenceDiagram() {
  return (
    <svg viewBox="0 0 320 180" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full" role="img" aria-label="Cadence: long slow stride vs quick short stride">
      <text x="80" y="18" textAnchor="middle" className="fill-red-400 text-[13px] font-semibold">Low Cadence</text>
      <text x="240" y="18" textAnchor="middle" className="fill-cyan-400 text-[13px] font-semibold">Optimal Cadence</text>
      {/* Low cadence: few long strides */}
      <g stroke="#f87171" strokeWidth="2" strokeLinecap="round">
        {/* Ground */}
        <line x1="20" y1="130" x2="140" y2="130" stroke="#475569" strokeWidth="1" />
        {/* Footprints - far apart */}
        <ellipse cx="30" cy="128" rx="8" ry="3" fill="#f87171" opacity="0.6" />
        <ellipse cx="80" cy="128" rx="8" ry="3" fill="#f87171" opacity="0.6" />
        <ellipse cx="130" cy="128" rx="8" ry="3" fill="#f87171" opacity="0.6" />
        {/* Distance markers */}
        <line x1="30" y1="140" x2="80" y2="140" strokeWidth="1" />
        <line x1="80" y1="140" x2="130" y2="140" strokeWidth="1" />
      </g>
      <text x="80" y="155" textAnchor="middle" className="fill-red-300 text-[10px]">&lt; 160 spm</text>
      <text x="80" y="167" textAnchor="middle" className="fill-red-300/60 text-[9px]">long, slow strides</text>
      <line x1="160" y1="24" x2="160" y2="175" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
      {/* Optimal cadence: many short strides */}
      <g stroke="#22d3ee" strokeWidth="2" strokeLinecap="round">
        <line x1="180" y1="130" x2="300" y2="130" stroke="#475569" strokeWidth="1" />
        {/* Footprints - close together */}
        <ellipse cx="190" cy="128" rx="6" ry="3" fill="#22d3ee" opacity="0.6" />
        <ellipse cx="210" cy="128" rx="6" ry="3" fill="#22d3ee" opacity="0.6" />
        <ellipse cx="230" cy="128" rx="6" ry="3" fill="#22d3ee" opacity="0.6" />
        <ellipse cx="250" cy="128" rx="6" ry="3" fill="#22d3ee" opacity="0.6" />
        <ellipse cx="270" cy="128" rx="6" ry="3" fill="#22d3ee" opacity="0.6" />
        <ellipse cx="290" cy="128" rx="6" ry="3" fill="#22d3ee" opacity="0.6" />
      </g>
      <text x="240" y="155" textAnchor="middle" className="fill-cyan-300 text-[10px]">170-190 spm</text>
      <text x="240" y="167" textAnchor="middle" className="fill-cyan-300/60 text-[9px]">quick, light steps</text>
      {/* Metronome icons */}
      <g>
        <text x="55" y="45" textAnchor="middle" className="fill-red-400/50 text-[28px]">{"\u266A"}</text>
        <text x="100" y="65" textAnchor="middle" className="fill-red-400/30 text-[22px]">{"\u266A"}</text>
      </g>
      <g>
        <text x="205" y="42" textAnchor="middle" className="fill-cyan-400/50 text-[22px]">{"\u266A"}</text>
        <text x="225" y="55" textAnchor="middle" className="fill-cyan-400/40 text-[22px]">{"\u266A"}</text>
        <text x="248" y="42" textAnchor="middle" className="fill-cyan-400/50 text-[22px]">{"\u266A"}</text>
        <text x="270" y="58" textAnchor="middle" className="fill-cyan-400/35 text-[22px]">{"\u266A"}</text>
      </g>
    </svg>
  );
}
