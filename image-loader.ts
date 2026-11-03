'use client';

// Image loader para que todas las imágenes en public/ lleven el prefijo
// del repositorio en GitHub Pages (o vacío si se usa dominio custom).
//
// El basePath se inyecta en build-time vía NEXT_PUBLIC_BASE_PATH.
// En producción con output:'export', el valor queda embebido en el JS estático.
export default function imageLoader({ src }: { src: string; width?: number; quality?: number }) {
  // NEXT_PUBLIC_BASE_PATH se resuelve en build-time (inline por Next.js)
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
