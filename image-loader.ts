'use client';

// Image loader para que todas las imágenes en public/ lleven el prefijo del repositorio en GitHub Pages
export default function imageLoader({ src }: { src: string; width: number; quality?: number }) {
  const basePath = process.env.NEXT_PUBLIC_BASE_PATH || '';
  if (src.startsWith('http://') || src.startsWith('https://')) {
    return src;
  }
  // Evitar duplicar el basePath si ya lo incluye
  if (basePath && src.startsWith(basePath)) {
    return src;
  }
  return `${basePath}${src.startsWith('/') ? src : `/${src}`}`;
}

