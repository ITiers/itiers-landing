'use client';

import React, { useState } from 'react';
import { Locale } from '@/data/i18n';
import { ThemeMode } from '@/components/Header';
import { INFO_ITIERS } from '@/data/mockData';
import { ContactFormSchema, validateWhatsAppConfig } from '@/lib/harness/guardrails';

interface ContactSectionProps {
  currentLang: Locale;
  theme?: ThemeMode;
}

export const ContactSection: React.FC<ContactSectionProps> = ({ currentLang, theme = 'light' }) => {
  const isDark = theme === 'dark';

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    service: '',
    message: '',
  });

  const [status, setStatus] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  const content = {
    es: {
      tag: 'CONTACTO',
      titleLine1: 'Hablemos de tus',
      titleLine2: 'datos',
      description: 'Completá el formulario para enviarnos un correo directo a hola@itiers.com o contactanos por WhatsApp para empezar a diseñar tu solución.',
      directEmailTitle: 'Correo directo',
      whatsappTitle: 'WhatsApp corporativo',
      locationsTitle: 'Nuestras Sedes',
      locations: 'Mendoza (AR) · Santiago (CL) · Delaware (USA)',
      form: {
        name: 'Nombre y Apellido',
        namePlaceholder: 'Tu nombre completo',
        email: 'Correo Electrónico',
        emailPlaceholder: 'tunombre@empresa.com',
        company: 'Empresa',
        companyPlaceholder: 'Tu organización o empresa',
        service: 'Tipo de Solución',
        options: [
          'Seleccioná una opción',
          'Ingeniería de Datos',
          'IA & Automatizaciones',
          'Capacitaciones',
          'Staffing de Datos',
          'Gobernanza de Datos',
          'Diagnóstico y Consultoría'
        ],
        message: 'Mensaje',
        messagePlaceholder: 'Contanos brevemente sobre tu proyecto o necesidad (mínimo 10 caracteres)...',
        submit: 'Enviar Mensaje a hola@itiers.com',
        submitting: 'Enviando mensaje...',
        successTitle: '¡Mensaje enviado con éxito!',
        successMessage: 'Gracias por escribirnos. El equipo de Itiers recibió tu mensaje en hola@itiers.com y te responderá a la brevedad.',
        sendAnother: 'Enviar otro mensaje',
        errorTitle: 'No se pudo enviar automáticamente',
        openMailClient: 'Abrir en tu cliente de correo (hola@itiers.com) →',
      }
    },
    en: {
      tag: 'CONTACT',
      titleLine1: "Let's talk about",
      titleLine2: 'your data',
      description: 'Fill out the form to send a direct email to hola@itiers.com or reach out via WhatsApp to start designing your solution.',
      directEmailTitle: 'Direct Email',
      whatsappTitle: 'Corporate WhatsApp',
      locationsTitle: 'Our Locations',
      locations: 'Mendoza (AR) · Santiago (CL) · Delaware (USA)',
      form: {
        name: 'Full Name',
        namePlaceholder: 'Your full name',
        email: 'Email Address',
        emailPlaceholder: 'yourname@company.com',
        company: 'Company',
        companyPlaceholder: 'Your organization or company',
        service: 'Type of Solution',
        options: [
          'Select an option',
          'Data Engineering',
          'AI & Automations',
          'Training',
          'Data Staffing',
          'Data Governance',
          'Diagnosis and Consulting'
        ],
        message: 'Message',
        messagePlaceholder: 'Briefly tell us about your project or need (minimum 10 characters)...',
        submit: 'Send Message to hola@itiers.com',
        submitting: 'Sending message...',
        successTitle: 'Message sent successfully!',
        successMessage: 'Thank you for reaching out. The Itiers team received your email at hola@itiers.com and will get back to you shortly.',
        sendAnother: 'Send another message',
        errorTitle: 'Could not send automatically',
        openMailClient: 'Open in your email client (hola@itiers.com) →',
      }
    }
  }[currentLang];

  const whatsappValidation = validateWhatsAppConfig(
    INFO_ITIERS.whatsapp,
    currentLang === 'es'
      ? 'Hola Itiers Data Sense, me gustaría consultar sobre sus soluciones de datos e IA.'
      : 'Hello Itiers Data Sense, I would like to inquire about your data and AI solutions.'
  );
  const whatsappUrl = whatsappValidation.success && whatsappValidation.url
    ? whatsappValidation.url
    : `https://api.whatsapp.com/send?phone=5492614171612`;

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (fieldErrors[name]) {
      setFieldErrors((prev) => {
        const updated = { ...prev };
        delete updated[name];
        return updated;
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    setFieldErrors({});

    // 1. Validación estricta con Guardrails Zod
    const validation = ContactFormSchema.safeParse({
      name: formData.name.trim(),
      email: formData.email.trim(),
      company: formData.company.trim() || undefined,
      serviceOfInterest: formData.service || '',
      message: formData.message.trim(),
    });

    if (!validation.success) {
      const errors: Record<string, string> = {};
      validation.error.issues.forEach((issue) => {
        const fieldName = issue.path[0] as string;
        if (fieldName) {
          errors[fieldName] = issue.message;
        }
      });
      setFieldErrors(errors);
      setErrorMessage(
        currentLang === 'es'
          ? 'Por favor completá los campos requeridos correctamente.'
          : 'Please complete all required fields correctly.'
      );
      return;
    }

    setStatus('submitting');

    try {
      // 2. Envío directo al buzón hola@itiers.com mediante servicio FormSubmit AJAX
      const response = await fetch(`https://formsubmit.co/ajax/${INFO_ITIERS.email}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({
          Nombre: formData.name.trim(),
          Email: formData.email.trim(),
          Empresa: formData.company.trim() || 'No especificada',
          'Tipo de Solución': formData.service,
          Mensaje: formData.message.trim(),
          _subject: `Nuevo contacto web: ${formData.name.trim()} (${formData.service})`,
          _replyto: formData.email.trim(),
          _template: 'table',
        }),
      });

      if (response.ok) {
        setStatus('success');
        setFormData({
          name: '',
          email: '',
          company: '',
          service: '',
          message: '',
        });
      } else {
        setStatus('error');
        setErrorMessage(
          currentLang === 'es'
            ? 'No pudimos procesar el envío automático. Podés hacer clic abajo para enviar tu mensaje por correo directo a hola@itiers.com.'
            : 'Could not process the automatic submission. You can click below to send your email directly to hola@itiers.com.'
        );
      }
    } catch {
      setStatus('error');
      setErrorMessage(
        currentLang === 'es'
          ? 'Error de conexión. Podés enviarnos el correo directamente haciendo clic en el enlace de abajo.'
          : 'Connection error. You can email us directly by clicking the link below.'
      );
    }
  };

  const mailtoHref = `mailto:${INFO_ITIERS.email}?subject=${encodeURIComponent(
    `Contacto web: ${formData.service || 'Consulta'}`
  )}&body=${encodeURIComponent(
    `Nombre: ${formData.name}\nEmail: ${formData.email}\nEmpresa: ${formData.company}\nServicio: ${formData.service}\n\nMensaje:\n${formData.message}`
  )}`;

  return (
    <section id="contacto" className="py-24 relative overflow-hidden bg-[#161616]" aria-labelledby="contacto-heading">
      
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none" aria-hidden="true">
        <div className="absolute top-1/2 -translate-y-1/2 -left-40 w-[45rem] h-[45rem] bg-[#ff4f00] rounded-full blur-[200px] opacity-[0.12]"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-start">
          
          {/* Columna Izquierda: Información Corporativa */}
          <div className="lg:col-span-5 text-left pt-6 lg:pt-0">
            <span className="text-[#ff4f00] text-xs font-bold uppercase tracking-widest mb-4 block">
              {content.tag}
            </span>
            <h2 id="contacto-heading" className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight leading-tight text-white mb-6">
              {content.titleLine1} <br />
              <span className="text-[#ff4f00]">{content.titleLine2}</span>
            </h2>
            <div className="w-16 h-1 bg-[#ff4f00] mb-8" aria-hidden="true"></div>
            <p className="text-[#b2b2b2] text-sm sm:text-base max-w-md font-medium leading-relaxed mb-10">
              {content.description}
            </p>

            <div className="space-y-6 pt-4 border-t border-[#262626]">
              <div>
                <span className="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">
                  {content.directEmailTitle}
                </span>
                <a
                  href={`mailto:${INFO_ITIERS.email}`}
                  className="text-white hover:text-[#ff4f00] transition-colors font-semibold text-base focus:outline-none focus:ring-2 focus:ring-[#ff4f00]"
                >
                  {INFO_ITIERS.email}
                </a>
              </div>

              <div>
                <span className="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">
                  {content.whatsappTitle}
                </span>
                <a
                  href={whatsappUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-white hover:text-[#ff4f00] transition-colors font-semibold text-base inline-flex items-center gap-2 focus:outline-none focus:ring-2 focus:ring-[#ff4f00]"
                >
                  <span>{INFO_ITIERS.whatsapp}</span>
                  <span className="text-xs text-[#ff4f00]">↗</span>
                </a>
              </div>

              <div>
                <span className="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">
                  {content.locationsTitle}
                </span>
                <p className="text-sm text-gray-300">
                  {content.locations}
                </p>
              </div>
            </div>
          </div>

          {/* Columna Derecha: Formulario Interactivo */}
          <div className={`lg:col-span-7 rounded-none p-8 sm:p-12 shadow-2xl border transition-colors duration-300 ${
            isDark ? 'bg-[#212121] border-[#333333]' : 'bg-white border-transparent'
          }`}>
            
            {status === 'success' ? (
              <div className="py-8 text-center space-y-4" role="status" aria-live="polite">
                <div className="w-16 h-16 mx-auto bg-green-500/10 text-green-500 rounded-full flex items-center justify-center text-3xl font-bold">
                  ✓
                </div>
                <h3 className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                  {content.form.successTitle}
                </h3>
                <p className={`text-sm max-w-md mx-auto leading-relaxed ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                  {content.form.successMessage}
                </p>
                <div className="pt-4">
                  <button
                    type="button"
                    onClick={() => setStatus('idle')}
                    className="bg-[#ff4f00] hover:bg-[#e04500] text-white text-xs font-bold px-6 py-3 uppercase tracking-wider transition-all focus:outline-none focus:ring-2 focus:ring-[#ff4f00]"
                  >
                    {content.form.sendAnother}
                  </button>
                </div>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-6" noValidate>
                
                {errorMessage && (
                  <div
                    className="p-4 bg-red-500/10 border border-red-500/30 text-red-500 text-sm rounded-none"
                    role="alert"
                  >
                    <p className="font-semibold">{errorMessage}</p>
                    {status === 'error' && (
                      <a
                        href={mailtoHref}
                        className="inline-block mt-2 text-xs font-bold underline hover:text-red-400 focus:outline-none focus:ring-2 focus:ring-red-400"
                      >
                        {content.form.openMailClient}
                      </a>
                    )}
                  </div>
                )}

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  {/* Nombre */}
                  <div>
                    <label
                      htmlFor="contact-name"
                      className={`block text-[11px] font-bold mb-2 uppercase tracking-wider transition-colors ${
                        isDark ? 'text-gray-300' : 'text-slate-500'
                      }`}
                    >
                      {content.form.name} *
                    </label>
                    <input
                      id="contact-name"
                      name="name"
                      type="text"
                      required
                      value={formData.name}
                      onChange={handleInputChange}
                      placeholder={content.form.namePlaceholder}
                      className={`w-full px-4 py-3.5 rounded-none border focus:outline-none focus:ring-2 focus:ring-[#ff4f00] focus:border-transparent transition-colors text-sm ${
                        fieldErrors.name ? 'border-red-500' : isDark ? 'border-[#333333]' : 'border-gray-200'
                      } ${isDark ? 'bg-[#161616] text-white' : 'bg-white text-gray-800'}`}
                    />
                    {fieldErrors.name && (
                      <span className="text-red-500 text-xs mt-1 block">{fieldErrors.name}</span>
                    )}
                  </div>

                  {/* Correo Electrónico */}
                  <div>
                    <label
                      htmlFor="contact-email"
                      className={`block text-[11px] font-bold mb-2 uppercase tracking-wider transition-colors ${
                        isDark ? 'text-gray-300' : 'text-slate-500'
                      }`}
                    >
                      {content.form.email} *
                    </label>
                    <input
                      id="contact-email"
                      name="email"
                      type="email"
                      required
                      value={formData.email}
                      onChange={handleInputChange}
                      placeholder={content.form.emailPlaceholder}
                      className={`w-full px-4 py-3.5 rounded-none border focus:outline-none focus:ring-2 focus:ring-[#ff4f00] focus:border-transparent transition-colors text-sm ${
                        fieldErrors.email ? 'border-red-500' : isDark ? 'border-[#333333]' : 'border-gray-200'
                      } ${isDark ? 'bg-[#161616] text-white' : 'bg-white text-gray-800'}`}
                    />
                    {fieldErrors.email && (
                      <span className="text-red-500 text-xs mt-1 block">{fieldErrors.email}</span>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  {/* Empresa */}
                  <div>
                    <label
                      htmlFor="contact-company"
                      className={`block text-[11px] font-bold mb-2 uppercase tracking-wider transition-colors ${
                        isDark ? 'text-gray-300' : 'text-slate-500'
                      }`}
                    >
                      {content.form.company}
                    </label>
                    <input
                      id="contact-company"
                      name="company"
                      type="text"
                      value={formData.company}
                      onChange={handleInputChange}
                      placeholder={content.form.companyPlaceholder}
                      className={`w-full px-4 py-3.5 rounded-none border focus:outline-none focus:ring-2 focus:ring-[#ff4f00] focus:border-transparent transition-colors text-sm ${
                        isDark ? 'bg-[#161616] border-[#333333] text-white' : 'bg-white border-gray-200 text-gray-800'
                      }`}
                    />
                  </div>

                  {/* Servicio de Interés */}
                  <div>
                    <label
                      htmlFor="contact-service"
                      className={`block text-[11px] font-bold mb-2 uppercase tracking-wider transition-colors ${
                        isDark ? 'text-gray-300' : 'text-slate-500'
                      }`}
                    >
                      {content.form.service} *
                    </label>
                    <select
                      id="contact-service"
                      name="service"
                      required
                      value={formData.service}
                      onChange={handleInputChange}
                      className={`w-full px-4 py-3.5 rounded-none border focus:outline-none focus:ring-2 focus:ring-[#ff4f00] focus:border-transparent transition-colors text-sm ${
                        fieldErrors.serviceOfInterest ? 'border-red-500' : isDark ? 'border-[#333333]' : 'border-gray-200'
                      } ${isDark ? 'bg-[#161616] text-white' : 'bg-white text-slate-700'}`}
                    >
                      {content.form.options.map((opt, i) => (
                        <option
                          key={i}
                          value={i === 0 ? '' : opt}
                          className={isDark ? 'bg-[#161616] text-white' : 'bg-white text-gray-800'}
                        >
                          {opt}
                        </option>
                      ))}
                    </select>
                    {fieldErrors.serviceOfInterest && (
                      <span className="text-red-500 text-xs mt-1 block">
                        {fieldErrors.serviceOfInterest}
                      </span>
                    )}
                  </div>
                </div>

                {/* Mensaje */}
                <div>
                  <label
                    htmlFor="contact-message"
                    className={`block text-[11px] font-bold mb-2 uppercase tracking-wider transition-colors ${
                      isDark ? 'text-gray-300' : 'text-slate-500'
                    }`}
                  >
                    {content.form.message} *
                  </label>
                  <textarea
                    id="contact-message"
                    name="message"
                    rows={4}
                    required
                    value={formData.message}
                    onChange={handleInputChange}
                    placeholder={content.form.messagePlaceholder}
                    className={`w-full px-4 py-3.5 rounded-none border focus:outline-none focus:ring-2 focus:ring-[#ff4f00] focus:border-transparent transition-colors text-sm resize-none ${
                      fieldErrors.message ? 'border-red-500' : isDark ? 'border-[#333333]' : 'border-gray-200'
                    } ${isDark ? 'bg-[#161616] text-white' : 'bg-white text-gray-800'}`}
                  ></textarea>
                  {fieldErrors.message && (
                    <span className="text-red-500 text-xs mt-1 block">{fieldErrors.message}</span>
                  )}
                </div>

                {/* Botón de Envío */}
                <div className="pt-2">
                  <button
                    type="submit"
                    disabled={status === 'submitting'}
                    className="bg-[#ff4f00] hover:bg-[#e04500] disabled:bg-[#ff4f00]/60 text-white text-[11px] sm:text-xs font-bold px-8 py-4 rounded-none uppercase tracking-wider transition-all w-full sm:w-auto flex items-center justify-center gap-2 focus:outline-none focus:ring-2 focus:ring-[#ff4f00]"
                  >
                    {status === 'submitting' && (
                      <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                    )}
                    <span>
                      {status === 'submitting' ? content.form.submitting : content.form.submit}
                    </span>
                  </button>
                </div>

              </form>
            )}

          </div>

        </div>
      </div>
    </section>
  );
};
