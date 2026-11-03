'use client';

import React from 'react';
import Image from 'next/image';
import { Locale } from '@/data/i18n';
import { ThemeMode } from '@/components/Header';

interface IntroSectionProps {
  currentLang: Locale;
  theme: ThemeMode;
}

export const IntroSection: React.FC<IntroSectionProps> = ({ currentLang, theme }) => {
  const isDark = theme === 'dark';

  const content = {
    es: {
      titleLine1: 'El poder transformador',
      titleLine2: 'de los datos',
      p1: 'En Itiers Data Sense, nos define una profunda pasión por el poder transformador de los datos y las tecnologías emergentes. Con más de 20 años de trayectoria, nos hemos consolidado como referentes en el mercado, destacándonos como una organización innovadora en el desarrollo de soluciones de gestión, automatización e Inteligencia Artificial (IA).',
      p2: 'Nuestro propósito aporta a la organización: Mejorando la capacidad de manejar información y teniendo tiempo para decidir, ayudamos directamente a mejorar la rentabilidad u optimización de recursos en función del fin organizacional. Se apunta a mejorar la creatividad del equipo de trabajo, maximizando la propuesta de valor.',
    },
    en: {
      titleLine1: 'The transformative power',
      titleLine2: 'of data',
      p1: 'At Itiers Data Sense, we are defined by a deep passion for the transformative power of data and emerging technologies. With over 20 years of experience, we have established ourselves as market leaders, standing out as an innovative organization in the development of management, automation, and Artificial Intelligence (AI) solutions.',
      p2: 'Our purpose adds value to the organization: By improving information management capacity and gaining time to decide, we directly help improve profitability or resource optimization aligned with organizational goals. The aim is to enhance the work team creativity, maximizing the value proposition.',
    },
  }[currentLang];

  return (
    <section id="nosotros" className={`py-16 md:py-24 relative overflow-hidden transition-colors duration-300 ${isDark ? 'bg-[#1A1A1A]' : 'bg-[#f9f9f9]'}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
          
          <div className="lg:col-span-6 text-left">
            <h2 className={`text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight mb-6 sm:mb-8 leading-tight ${isDark ? 'text-white' : 'text-[#4d4d4d]'}`}>
              <span className="block">{content.titleLine1}</span>
              <span className="block">{content.titleLine2}</span>
            </h2>
            <div className={`space-y-4 sm:space-y-6 text-sm sm:text-base leading-relaxed ${isDark ? 'text-[#b2b2b2]' : 'text-[#898a8d]'}`}>
              <p>{content.p1}</p>
              <p>{content.p2}</p>
            </div>
          </div>

          <div className="lg:col-span-6 relative w-full max-w-[320px] sm:max-w-[380px] lg:max-w-[420px] mx-auto flex justify-center">
            <Image
              src="/imagen-2da-seccion.png"
              alt="Itiers Data Sense Overview"
              width={2084}
              height={2084}
              className="w-full h-auto object-contain"
              sizes="(max-width: 1024px) 100vw, 50vw"
              priority
            />
          </div>

        </div>
      </div>
    </section>
  );
};