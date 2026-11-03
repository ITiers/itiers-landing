import type { NextConfig } from "next";

// ─── Base Path para GitHub Pages ───────────────────────────────────────────
// Cuando el sitio se sirve desde un subdirectorio (ej: itiers.github.io/itiers-landing),
// se necesita un basePath. Cuando se usa un dominio custom (ej: www.itiers.com),
// el basePath debe ser vacío ('').
//
// Para cambiar a dominio custom: poner DEPLOY_BASE_PATH="" en el workflow,
// o simplemente borrar la línea `DEPLOY_BASE_PATH` del workflow.
// ────────────────────────────────────────────────────────────────────────────
const isGithubActions = process.env.GITHUB_ACTIONS === 'true';
// Se puede sobreescribir con la variable DEPLOY_BASE_PATH del workflow
// Si no está definida, se usa '/itiers-landing' por defecto en GitHub Actions
const basePath = isGithubActions
  ? (process.env.DEPLOY_BASE_PATH ?? '/itiers-landing')
  : '';

const nextConfig: NextConfig = {
  output: 'export', // Requerido para exportación estática a GitHub Pages
  basePath: basePath || undefined,
  assetPrefix: basePath ? `${basePath}/` : undefined,
  env: {
    NEXT_PUBLIC_BASE_PATH: basePath,
  },
  images: {
    loader: 'custom',
    loaderFile: './image-loader.ts',
    dangerouslyAllowSVG: true,
    contentDispositionType: 'attachment',
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },
};

export default nextConfig;
