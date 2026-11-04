import type { Metadata } from 'next';
import { Comfortaa, Nunito } from 'next/font/google';
import Script from 'next/script';
import { JsonLd } from '@/components/JsonLd';
import './globals.css';

// Google Tag Manager ID
const GTM_ID = 'GTM-W54KXZZK';

const comfortaa = Comfortaa({
  subsets: ['latin'],
  weight: ['300', '400', '700'],
  variable: '--font-comfortaa',
  display: 'swap',
});

const nunito = Nunito({
  subsets: ['latin'],
  weight: ['300', '400', '600', '700', '800'],
  variable: '--font-nunito',
  display: 'swap',
});

export const metadata: Metadata = {
  metadataBase: new URL('https://www.itiers.com'),
  title: {
    default: 'Itiers Data Sense | Soluciones de Datos e Inteligencia Artificial',
    template: '%s | Itiers Data Sense',
  },
  description: 'En Itiers Data Sense convertimos el caos de datos en decisiones estratégicas. Acompañamos a organizaciones líderes a desbloquear el valor de su información con un enfoque 100% personalizado en ingeniería de datos, capacitaciones y staffing.',
  keywords: [
    'Itiers Data Sense',
    'Ingeniería de Datos',
    'Data Engineering',
    'Business Intelligence',
    'Data Analytics',
    'Modelos de IA',
    'Staffing de Datos',
    'Capacitaciones BI',
    'Gobernanza de Datos',
    'IBM Watsonx',
    'Mendoza',
    'Argentina',
    'Chile',
    'Delaware USA'
  ],
  authors: [{ name: 'Itiers Data Sense', url: 'https://www.itiers.com' }],
  creator: 'Itiers Data Sense',
  publisher: 'Itiers Data Sense',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  alternates: {
    canonical: 'https://www.itiers.com',
    languages: {
      'es-AR': 'https://www.itiers.com/es',
      'en-US': 'https://www.itiers.com/en',
      'x-default': 'https://www.itiers.com',
    },
  },
  openGraph: {
    title: 'Itiers Data Sense | Soluciones de Datos e Inteligencia Artificial',
    description: 'En Itiers Data Sense convertimos el caos de datos en decisiones estratégicas. Más de 20 años transformando información en valor real.',
    url: 'https://www.itiers.com',
    siteName: 'Itiers Data Sense',
    locale: 'es_AR',
    alternateLocale: ['en_US'],
    type: 'website',
    images: [
      {
        url: '/hero-banner-itiers.jpg',
        width: 1200,
        height: 630,
        alt: 'Itiers Data Sense - Soluciones de Datos e IA',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Itiers Data Sense | Soluciones de Datos e Inteligencia Artificial',
    description: 'En Itiers Data Sense convertimos el caos de datos en decisiones estratégicas.',
    images: ['/hero-banner-itiers.jpg'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  icons: {
    icon: '/Icono.ico',
    apple: '/Icono.ico',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" className={`${comfortaa.variable} ${nunito.variable}`}>
      <head>
        {/* Google Tag Manager */}
        <Script
          id="gtm-script"
          strategy="afterInteractive"
          src={`https://www.googletagmanager.com/gtm.js?id=${GTM_ID}`}
        />
        <Script
          id="gtm-dataLayer"
          strategy="afterInteractive"
          dangerouslySetInnerHTML={{
            __html: `
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
            `,
          }}
        />
        <JsonLd />
      </head>
      <body className="antialiased">
        {/* Google Tag Manager (noscript) - fallback para navegadores sin JS */}
        <noscript>
          <iframe
            src={`https://www.googletagmanager.com/ns.html?id=${GTM_ID}`}
            height="0"
            width="0"
            style={{ display: 'none', visibility: 'hidden' }}
            title="Google Tag Manager"
          />
        </noscript>
        {children}
      </body>
    </html>
  );
}