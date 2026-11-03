
import type { MetadataRoute } from 'next';

export const dynamic = 'force-static';

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://www.itiers.com';
  const currentDate = new Date();

  return [
    {
      url: `${baseUrl}/`,
      lastModified: currentDate,
      changeFrequency: 'weekly',
      priority: 1.0,
      alternates: {
        languages: {
          es: `${baseUrl}/es`,
          'x-default': `${baseUrl}/`,
        },
      },
    },
    {
      url: `${baseUrl}/es`,
      lastModified: currentDate,
      changeFrequency: 'weekly',
      priority: 1.0,
      alternates: {
        languages: {
          es: `${baseUrl}/es`,
          'x-default': `${baseUrl}/`,
        },
      },
    },
    {
      url: `${baseUrl}/servicios`,
      lastModified: currentDate,
      changeFrequency: 'weekly',
      priority: 0.9,
      alternates: {
        languages: {
          es: `${baseUrl}/servicios`,
          'x-default': `${baseUrl}/servicios`,
        },
      },
    },
  ];
}
