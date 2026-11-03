import type { NextConfig } from "next";

// Detección de despliegue en GitHub Pages (Actions)
const isGithubActions = process.env.GITHUB_ACTIONS === 'true';
// Nombre del repositorio en GitHub: https://github.com/iTiers/itiers-landing
const repoName = 'itiers-landing';
const basePath = isGithubActions ? `/${repoName}` : '';

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
