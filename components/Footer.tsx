'use client';

import React from 'react';
import Image from 'next/image';
import { Locale } from '@/data/i18n';
import { INFO_ITIERS } from '@/data/mockData';
import { validateWhatsAppConfig } from '@/lib/harness/guardrails';
import { ThemeMode } from '@/components/Header';

interface FooterProps {
  currentLang: Locale;
  theme?: ThemeMode;
}

export const Footer: React.FC<FooterProps> = ({ currentLang, theme = 'light' }) => {
  const isDark = theme === 'dark';

  const tagline = currentLang === 'es'
    ? 'Hacemos que los datos impulsen mejores decisiones y acciones.'
    : 'We make data drive better decisions and actions.';

  const whatsappChannel = validateWhatsAppConfig(INFO_ITIERS.whatsapp, 'Hola!');

  if (!whatsappChannel.success || !whatsappChannel.url) {
    throw new Error(whatsappChannel.error || 'La configuración del canal de WhatsApp no es válida.');
  }

  const handleScroll = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    e.preventDefault();
    const el = document.querySelector(href);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  const footerNav = {
    es: {
      navegacion: 'Navegación',
      inicio: 'Inicio',
      nosotros: 'Nosotros',
      servicios: 'Servicios',
      contacto: 'Contacto',
      ubicacion: 'Ubicación',
      redes: 'Redes Sociales',
    },
    en: {
      navegacion: 'Navigation',
      inicio: 'Home',
      nosotros: 'About Us',
      servicios: 'Services',
      contacto: 'Contact',
      ubicacion: 'Locations',
      redes: 'Social Media',
    }
  }[currentLang];

  const locations = [
    { flag: '/bandera-arg.png', text: 'Av. Perú 1841, Mendoza, Argentina', alt: 'Argentina' },
    { flag: '/bandera-chile.png', text: 'General del Canto 421, piso 6, Providencia, Santiago de Chile', alt: 'Chile' },
    { flag: '/bandera-usa.png', text: '651 North Broad Street, Middletown, DE 19709, USA', alt: 'USA' },
  ];

  return (
    <footer className={`relative pt-24 pb-12 border-t overflow-hidden transition-colors duration-300 ${isDark ? 'bg-[#1A1A1A] text-[#b2b2b2] border-[#4d4d4d]' : 'bg-white text-[#4d4d4d] border-[#b2b2b2]'}`}>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-x-8 gap-y-12 mb-20 items-start">

          <div className="flex flex-col">
            <div className="relative w-36 h-10 mb-6">
              <Image
                src={isDark ? '/itiers-blanco.png' : '/itiers.png'}
                alt="Itiers Data Sense"
                fill
                sizes="200px"
                className="object-contain object-left-top"
              />
            </div>

            <p className={`text-sm leading-relaxed font-medium ${isDark ? 'text-[#898a8d]' : 'text-[#4d4d4d]'}`}>
              {tagline}
            </p>
          </div>

          <div className="flex flex-col">
            <h4 className="text-xs font-bold uppercase tracking-widest text-[#ff4f00] mb-6">
              {footerNav.navegacion}
            </h4>
            <ul className={`space-y-4 text-sm font-medium ${isDark ? 'text-[#898a8d]' : 'text-[#4d4d4d]'}`}>
              <li><a href="#inicio" onClick={(e) => handleScroll(e, '#inicio')} className="hover:text-[#ff4f00] transition-colors">{footerNav.inicio}</a></li>
              <li><a href="#nosotros" onClick={(e) => handleScroll(e, '#nosotros')} className="hover:text-[#ff4f00] transition-colors">{footerNav.nosotros}</a></li>
              <li><a href="#servicios-cards" onClick={(e) => handleScroll(e, '#servicios-cards')} className="hover:text-[#ff4f00] transition-colors">{footerNav.servicios}</a></li>
              <li><a href="#contacto" onClick={(e) => handleScroll(e, '#contacto')} className="hover:text-[#ff4f00] transition-colors">{footerNav.contacto}</a></li>
            </ul>
          </div>

          <div className="flex flex-col">
            <h4 className="text-xs font-bold uppercase tracking-widest text-[#ff4f00] mb-6">
              {footerNav.ubicacion}
            </h4>
            <ul className={`space-y-5 text-sm font-medium ${isDark ? 'text-[#898a8d]' : 'text-[#4d4d4d]'}`}>
              {locations.map((loc, index) => (
                <li key={index} className="flex items-start gap-3 leading-relaxed">
                  <Image src={loc.flag} alt={loc.alt} width={18} height={14} className="w-4.5 h-3.5 object-cover rounded-sm mt-1 shrink-0" />
                  <span>{loc.text}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="flex flex-col">
            <h4 className="text-xs font-bold uppercase tracking-widest text-[#ff4f00] mb-6">
              {footerNav.contacto}
            </h4>

            <div className={`flex flex-col gap-4 text-sm font-medium ${isDark ? 'text-[#898a8d]' : 'text-[#4d4d4d]'}`}>
              <a
                href="mailto:hola@itiers.com"
                className="inline-flex items-center gap-3 transition-colors hover:text-[#ff4f00]"
              >
                <svg className="w-4 h-4 text-[#ff4f00] shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                hola@itiers.com
              </a>

              <a
                href={whatsappChannel.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-3 transition-colors hover:text-[#ff4f00]"
              >
                <svg className="w-4 h-4 text-[#ff4f00] shrink-0" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
                </svg>
                +54 9 261 417-1612
              </a>
            </div>
          </div>

          <div className="flex flex-col">
            <h4 className="text-xs font-bold uppercase tracking-widest text-[#ff4f00] mb-6">
              {footerNav.redes}
            </h4>

            <div className={`flex flex-col gap-4 text-sm font-medium ${isDark ? 'text-[#898a8d]' : 'text-[#4d4d4d]'}`}>
              <a href="https://ar.linkedin.com/company/itiers" target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-3 transition-colors hover:text-[#ff4f00]">
                <svg className="w-5 h-5 text-[#ff4f00] shrink-0" fill="currentColor" viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" /></svg>
                LinkedIn
              </a>
              <a href="https://www.instagram.com/itiersds/" target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-3 transition-colors hover:text-[#ff4f00]">
                <svg className="w-5 h-5 text-[#ff4f00] shrink-0" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.209-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" /></svg>
                Instagram
              </a>
              <a href="https://www.youtube.com/channel/UCrWeQoKi3bM8JtVYVG-44VA" target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-3 transition-colors hover:text-[#ff4f00]">
                <svg className="w-5 h-5 text-[#ff4f00] shrink-0" fill="currentColor" viewBox="0 0 24 24"><path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 3.993-8 4.007z" /></svg>
                YouTube
              </a>
            </div>
          </div>

        </div>

        <div className={`pt-8 border-t flex flex-col sm:flex-row items-center justify-between text-xs font-medium ${isDark ? 'border-[#4d4d4d] text-[#898a8d]' : 'border-[#b2b2b2] text-[#898a8d]'}`}>
          <div>© {new Date().getFullYear()} Itiers Data Sense. {currentLang === 'es' ? 'Todos los derechos reservados.' : 'All rights reserved.'}</div>
        </div>
      </div>
    </footer>
  );
};