import React from 'react';

const colorMap = {
  purple: {
    gradient: 'from-[#D9D1FF] to-[#A898FF]',
    text: 'text-indigo-950/70',
    subtext: 'text-indigo-900',
    glow: 'bg-white/10',
  },
  blue: {
    gradient: 'from-[#A5E3FB] to-[#7CB7EC]',
    text: 'text-blue-950/70',
    subtext: 'text-blue-900',
    glow: 'bg-white/10',
  },
  teal: {
    gradient: 'from-[#A7F3D0] to-[#34D399]',
    text: 'text-teal-950/70',
    subtext: 'text-teal-900',
    glow: 'bg-white/10',
  },
  orange: {
    gradient: 'from-[#FFE4B2] to-[#FFB970]',
    text: 'text-orange-950/70',
    subtext: 'text-orange-900',
    glow: 'bg-white/10',
  },
};

export default function KPICard({ title, value, subtitle, color = 'purple' }) {
  const theme = colorMap[color] ?? colorMap.purple;

  return (
    <div className={`bg-gradient-to-br ${theme.gradient} rounded-[24px] p-6 relative overflow-hidden group`}>
      {/* Title */}
      <div className="flex justify-between items-start mb-4 relative z-10">
        <span className={`${theme.text} font-medium tracking-wide`}>{title}</span>
      </div>

      {/* Value */}
      <div className="relative z-10 mt-2">
        <h2 className="text-3xl lg:text-4xl font-bold text-white drop-shadow-[0_2px_2px_rgba(0,0,0,0.1)]">
          {value}
        </h2>

        {/* Subtitle */}
        {subtitle && (
          <p className={`${theme.subtext} text-xs font-semibold mt-2`}>
            {subtitle}
          </p>
        )}
      </div>

      {/* Background glow orb */}
      <div className={`absolute -bottom-10 -right-10 w-40 h-40 ${theme.glow} rounded-full blur-2xl group-hover:bg-white/20 transition-all`}></div>
    </div>
  );
}
