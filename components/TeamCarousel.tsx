'use client';

import React from 'react';
import Image from 'next/image';
import { ThemeMode } from '@/components/Header';

interface TeamCarouselProps {
  theme?: ThemeMode;
}

const TEAM_IMAGES = [
  { src: '/Fotos itiers y equipo para web 2026-18.jpg', format: 'vertical' },
  { src: '/Fotos itiers y equipo para web 2026-02.jpg', format: 'horizontal' },
  { src: '/Fotos itiers y equipo para web 2026-03.jpg', format: 'horizontal' },
  { src: '/Fotos itiers y equipo para web 2026-04.jpg', format: 'horizontal' },
  { src: '/Fotos itiers y equipo para web 2026-05.jpg', format: 'vertical' },
  { src: '/Fotos itiers y equipo para web 2026-06.jpg', format: 'vertical' },
  { src: '/Fotos itiers y equipo para web 2026-07.jpg', format: 'vertical' },
  { src: '/Fotos itiers y equipo para web 2026-08.jpg', format: 'horizontal' },
  { src: '/Fotos itiers y equipo para web 2026-09.jpg', format: 'vertical' },
  { src: '/Fotos itiers y equipo para web 2026-10.jpg', format: 'horizontal' },
  { src: '/Fotos itiers y equipo para web 2026-11.jpg', format: 'horizontal' },
  { src: '/Fotos itiers y equipo para web 2026-12.jpg', format: 'horizontal' },
  { src: '/Fotos itiers y equipo para web 2026-13.jpg', format: 'horizontal' },
  { src: '/Fotos itiers y equipo para web 2026-14.jpg', format: 'vertical' },
  { src: '/Fotos itiers y equipo para web 2026-15.jpg', format: 'vertical' },
  { src: '/Fotos itiers y equipo para web 2026-16.jpg', format: 'horizontal' },
  { src: '/Fotos itiers y equipo para web 2026-17.jpg', format: 'vertical' },
  { src: '/Fotos itiers y equipo para web 2026-01.jpg', format: 'vertical' },
  { src: '/Fotos itiers y equipo para web 2026-19.jpg', format: 'vertical' },
  { src: '/Fotos itiers y equipo para web 2026-20.jpg', format: 'vertical' },
  { src: '/Fotos itiers y equipo para web 2026-21.jpg', format: 'vertical' },
  { src: '/Fotos itiers y equipo para web 2026-22.jpg', format: 'vertical' },
  { src: '/Fotos itiers y equipo para web 2026-23.jpg', format: 'vertical' },
];

export const TeamCarousel: React.FC<TeamCarouselProps> = ({ theme = 'light' }) => {
  const isDark = theme === 'dark';
  
  const baseTrack = [...TEAM_IMAGES, ...TEAM_IMAGES];

  return (
    <div className={`relative w-full overflow-hidden py-16 sm:py-24 transition-colors duration-300 ${isDark ? 'bg-[#1A1A1A]' : 'bg-[#4d4d4d]'}`}>
      
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes scrollTeamInf {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        .animate-scroll-team-inf {
          display: flex;
          width: max-content;
          animation: scrollTeamInf 180s linear infinite;
          align-items: center;
        }
      `}} />

      <div className="relative w-full overflow-hidden flex z-0">
        <div className="animate-scroll-team-inf gap-4 sm:gap-6 px-4">
          {[...baseTrack, ...baseTrack].map((member, index) => {
            const isLarge = index % 2 === 0; // Alterna estrictamente entre grande y pequeño
            const isHorizontal = member.format === 'horizontal';

            let sizeClasses = '';
            if (isHorizontal) {
              sizeClasses = isLarge ? 'w-[360px] sm:w-[480px] aspect-[4/3]' : 'w-[240px] sm:w-[320px] aspect-[4/3]';
            } else {
              sizeClasses = isLarge ? 'w-[240px] sm:w-[320px] aspect-[3/4]' : 'w-[160px] sm:w-[210px] aspect-[3/4]';
            }

            return (
              <div 
                key={index} 
                className={`flex-shrink-0 ${sizeClasses}`}
              >
                 <div className={`w-full h-full rounded-2xl overflow-hidden relative shadow-xl bg-black/20 ${isDark ? 'border border-[#333333]' : 'border border-[#b2b2b2]/20'}`}>
                    <Image 
                      src={member.src}
                      fill
                      className="object-cover" 
                      alt="Equipo Itiers"
                      sizes="(max-width: 768px) 240px, 480px"
                    />
                 </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};