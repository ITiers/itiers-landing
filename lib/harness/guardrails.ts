import { z } from 'zod';

// =====================================================================
// 1. ESQUEMA DE NAVEGACIÓN Y CANALIZACIÓN A WHATSAPP
// =====================================================================

export const WhatsAppChannelSchema = z.object({
  phoneNumber: z.string().regex(/^\+?[1-9]\d{1,14}$/, {
    message: "El número de teléfono debe incluir el código de país (ej: +5492614171612)."
  }),
  prefilledMessage: z.string().min(5, {
    message: "El mensaje de bienvenida predefinido debe tener al menos 5 caracteres."
  }),
  targetUrl: z.string().url({
    message: "La URL generada debe ser un enlace HTTPS válido a api.whatsapp.com o wa.me."
  })
});

export type WhatsAppChannel = z.infer<typeof WhatsAppChannelSchema>;


// =====================================================================
// 2. ESQUEMA DE VALIDACIÓN DEL FORMULARIO DE CONTACTO
// =====================================================================

export const ContactFormSchema = z.object({
  name: z.string().min(2, { message: "El nombre completo debe tener al menos 2 caracteres." }),
  email: z.string().email({ message: "Debe ingresar una dirección de correo electrónico válida." }),
  company: z.string().optional(),
  serviceOfInterest: z.string().min(1, { message: "Debe seleccionar un servicio válido." }),
  message: z.string().min(10, { message: "El mensaje debe tener al menos 10 caracteres explicativos." }),
  recaptchaToken: z.string().optional()
});

export type ContactFormData = z.infer<typeof ContactFormSchema>;


// =====================================================================
// 3. ESQUEMA JSON-LD SCHEMA.ORG (ProfessionalService con 3 Sedes)
// =====================================================================

export const PostalAddressSchema = z.object({
  '@type': z.literal('PostalAddress'),
  streetAddress: z.string(),
  addressLocality: z.string(),
  addressRegion: z.string().optional(),
  addressCountry: z.string()
});

export const JsonLdProfessionalServiceSchema = z.object({
  '@context': z.literal('https://schema.org'),
  '@type': z.enum(['ProfessionalService', 'Organization']),
  name: z.string().min(3),
  url: z.string().url(),
  logo: z.string().url(),
  description: z.string().min(20),
  telephone: z.string(),
  email: z.string().email(),
  sameAs: z.array(z.string().url()).optional(),
  address: z.array(PostalAddressSchema).min(3, {
    message: "Debe registrar las 3 sedes corporativas obligatorias (Mendoza, Santiago de Chile, Delaware USA)."
  }),
  knowsAbout: z.array(z.string()).min(3, {
    message: "Debe listar al menos tres áreas de servicio documentadas."
  })
});

export type JsonLdProfessionalService = z.infer<typeof JsonLdProfessionalServiceSchema>;


// =====================================================================
// 4. ESTRUCTURA Y DATOS OFICIALES DE ITIERS CON VALIDACIÓN ZOD
// =====================================================================

export const OFFICIAL_ITIERS_JSON_LD: JsonLdProfessionalService = {
  '@context': 'https://schema.org',
  '@type': 'ProfessionalService',
  name: 'Itiers Data Sense',
  url: 'https://www.itiers.com',
  logo: 'https://www.itiers.com/logo.png',
  description: 'En Itiers Data Sense convertimos el caos de datos en decisiones estratégicas con un enfoque personalizado.',
  telephone: '+5492614171612',
  email: 'hola@itiers.com',
  address: [
    {
      '@type': 'PostalAddress',
      streetAddress: 'Mendoza Centro',
      addressLocality: 'Mendoza',
      addressRegion: 'Mendoza',
      addressCountry: 'AR'
    },
    {
      '@type': 'PostalAddress',
      streetAddress: 'Providencia',
      addressLocality: 'Santiago',
      addressRegion: 'Región Metropolitana',
      addressCountry: 'CL'
    },
    {
      '@type': 'PostalAddress',
      streetAddress: 'Delaware Corporate Center',
      addressLocality: 'Wilmington',
      addressRegion: 'Delaware',
      addressCountry: 'US'
    }
  ],
  knowsAbout: [
    'Data Engineering',
    'Data Analytics',
    'Business Intelligence',
    'Training',
    'Data Staffing'
  ]
};


// =====================================================================
// 5. FUNCIONES DE AUDITORÍA Y COMPROBACIÓN DE PARIDAD
// =====================================================================

export function validateWhatsAppConfig(phone: string, text: string): { success: boolean; url?: string; error?: string } {
  const encodedText = encodeURIComponent(text);
  const targetUrl = `https://api.whatsapp.com/send?phone=${phone.replace(/\+/g, '')}&text=${encodedText}`;
  const result = WhatsAppChannelSchema.safeParse({
    phoneNumber: phone,
    prefilledMessage: text,
    targetUrl
  });

  if (!result.success) {
    return { success: false, error: result.error.issues.map((e: z.ZodIssue) => e.message).join(' | ') };
  }
  return { success: true, url: targetUrl };
}

export function validateJsonLdStructure(data: unknown): { success: boolean; error?: string } {
  const result = JsonLdProfessionalServiceSchema.safeParse(data);
  if (!result.success) {
    return { success: false, error: result.error.issues.map((e: z.ZodIssue) => `${e.path.join('.')}: ${e.message}`).join(' | ') };
  }
  return { success: true };
}

export function validateI18nParity(esDict: Record<string, unknown>, enDict: Record<string, unknown>): { isPar: boolean; missingInEn: string[]; missingInEs: string[] } {
  function getKeys(obj: Record<string, unknown>, prefix = ''): string[] {
    let keys: string[] = [];
    for (const k in obj) {
      const fullKey = prefix ? `${prefix}.${k}` : k;
      if (typeof obj[k] === 'object' && obj[k] !== null && !Array.isArray(obj[k])) {
        keys = keys.concat(getKeys(obj[k] as Record<string, unknown>, fullKey));
      } else {
        keys.push(fullKey);
      }
    }
    return keys;
  }

  const esKeys = new Set(getKeys(esDict));
  const enKeys = new Set(getKeys(enDict));

  const missingInEn = Array.from(esKeys).filter(k => !enKeys.has(k));
  const missingInEs = Array.from(enKeys).filter(k => !esKeys.has(k));

  return {
    isPar: missingInEn.length === 0 && missingInEs.length === 0,
    missingInEn,
    missingInEs
  };
}
