
import type { MetadataRoute } from 'next';

export const dynamic = 'force-static';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/api/', '/_next/'],
      },
      {
        userAgent: [
          'GPTBot',
          'ChatGPT-User',
          'ClaudeBot',
          'PerplexityBot',
          'Google-Extended',
          'CCBot',
          'Applebot-Extended',
          'Meta-ExternalAgent',
          'Bytespider',
          'cohere-ai'
        ],
        allow: '/',
      },
    ],
    sitemap: 'https://www.itiers.com/sitemap.xml',
    host: 'https://www.itiers.com',
  };
}
