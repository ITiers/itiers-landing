'use client';

import React, { useState } from 'react';
import { Locale } from '@/data/i18n';
import { ThemeMode } from '@/components/Header';
import { INFO_ITIERS } from '@/data/mockData';
import { ContactFormSchema } from '@/lib/harness/guardrails';

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
      description: 'Completa el formulario o contactanos por WhatsApp para empezar a diseñar tu solución.',
      form: {
        name: 'Nombre y Apellido',
        email: 'Correo Electrónico',
        company: 'Empresa',
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
        submit: 'Enviar Mensaje',
        submitting: 'Enviando...',
        successMessage: '¡Mensaje enviado con éxito! Nos pondremos en contacto a la brevedad.',
        errorMessage: 'Ocurrió un error al enviar el formulario. Por favor intentá nuevamente.',
      }
    },
    en: {
      tag: 'CONTACT',
      titleLine1: "Let's talk about",
      titleLine2: 'your data',
      description: 'Fill out the form or contact us via WhatsApp to start designing your solution.',
      form: {
        name: 'Full Name',
        email: 'Email Address',
        company: 'Company',
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
        submit: 'Send Message',
        submitting: 'Sending...',
        successMessage: 'Message sent successfully! We will get in touch shortly.',
        errorMessage: 'An error occurred while sending the form. Please try again.',
      }
    }
  }[currentLang];

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (fieldErrors[name]) {
      setFieldErrors((prev) => {
        const next = { ...prev };
        delete next[name];
        return next;
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    setFieldErrors({});

    // Validación mediante Guardrails Zod
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
        const field = issue.path[0] as string;
        if (field) errors[field] = issue.message;
      });
      setFieldErrors(errors);
      setErrorMessage(
        currentLang === 'es'
          ? 'Por favor completá los campos obligatorios correctamente.'
          : 'Please complete all required fields correctly.'
      );
      return;
    }

    setStatus('submitting');

    try {
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
        setErrorMessage(content.form.errorMessage);
      }
    } catch {
      setStatus('error');
      setErrorMessage(content.form.errorMessage);
    }
  };

  return (
    <section id="contacto" className="py-24 relative overflow-hidden bg-[#161616]">
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/2 -translate-y-1/2 -left-40 w-[45rem] h-[45rem] bg-[#ff4f00] rounded-full blur-[200px] opacity-[0.12]"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
          
          {/* Columna Izquierda: Tal cual el diseño original */}
          <div className="lg:col-span-5 text-left pt-10 lg:pt-0">
            <span className="text-[#ff4f00] text-xs font-bold uppercase tracking-widest mb-4 block">
              {content.tag}
            </span>
            <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight leading-tight text-white mb-6">
              {content.titleLine1} <br />
              {content.titleLine2}
            </h2>
            <div className="w-16 h-1 bg-[#ff4f00] mb-8"></div>
            <p className="text-[#b2b2b2] text-sm sm:text-base max-w-md font-medium leading-relaxed">
              {content.description}
            </p>
          </div>

          {/* Columna Derecha: Formulario conectado */}
          <div className={`lg:col-span-7 rounded-none p-8 sm:p-12 shadow-2xl border transition-colors duration-300 ${
            isDark ? 'bg-[#212121] border-[#333333]' : 'bg-white border-transparent'
          }`}>
            <form onSubmit={handleSubmit} className="space-y-6" noValidate>
              
              {status === 'success' && (
                <div className="p-4 bg-green-500/10 border border-green-500/30 text-green-600 dark:text-green-400 text-sm font-semibold rounded-none">
                  {content.form.successMessage}
                </div>
              )}

              {errorMessage && (
                <div className="p-4 bg-red-500/10 border border-red-500/30 text-red-500 text-sm font-semibold rounded-none">
                  {errorMessage}
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div>
                  <label className={`block text-[11px] font-bold mb-2 uppercase tracking-wider transition-colors ${isDark ? 'text-gray-300' : 'text-slate-500'}`}>
                    {content.form.name} *
                  </label>
                  <input 
                    type="text" 
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    className={`w-full px-4 py-3.5 rounded-none border focus:outline-none focus:ring-2 focus:ring-[#ff4f00] focus:border-transparent transition-colors text-sm ${
                      fieldErrors.name ? 'border-red-500' : isDark ? 'border-[#333333]' : 'border-gray-200'
                    } ${isDark ? 'bg-[#161616] text-white' : 'bg-white text-gray-800'}`} 
                  />
                  {fieldErrors.name && (
                    <span className="text-red-500 text-xs mt-1 block">{fieldErrors.name}</span>
                  )}
                </div>

                <div>
                  <label className={`block text-[11px] font-bold mb-2 uppercase tracking-wider transition-colors ${isDark ? 'text-gray-300' : 'text-slate-500'}`}>
                    {content.form.email} *
                  </label>
                  <input 
                    type="email" 
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
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
                <div>
                  <label className={`block text-[11px] font-bold mb-2 uppercase tracking-wider transition-colors ${isDark ? 'text-gray-300' : 'text-slate-500'}`}>
                    {content.form.company}
                  </label>
                  <input 
                    type="text" 
                    name="company"
                    value={formData.company}
                    onChange={handleInputChange}
                    className={`w-full px-4 py-3.5 rounded-none border focus:outline-none focus:ring-2 focus:ring-[#ff4f00] focus:border-transparent transition-colors text-sm ${
                      isDark ? 'bg-[#161616] border-[#333333] text-white' : 'bg-white border-gray-200 text-gray-800'
                    }`} 
                  />
                </div>

                <div>
                  <label className={`block text-[11px] font-bold mb-2 uppercase tracking-wider transition-colors ${isDark ? 'text-gray-300' : 'text-slate-500'}`}>
                    {content.form.service} *
                  </label>
                  <select 
                    name="service"
                    value={formData.service}
                    onChange={handleInputChange}
                    className={`w-full px-4 py-3.5 rounded-none border focus:outline-none focus:ring-2 focus:ring-[#ff4f00] focus:border-transparent transition-colors text-sm appearance-none ${
                      fieldErrors.serviceOfInterest ? 'border-red-500' : isDark ? 'border-[#333333]' : 'border-gray-200'
                    } ${isDark ? 'bg-[#161616] text-white' : 'bg-white text-slate-700'}`}
                  >
                    {content.form.options.map((opt, i) => (
                      <option key={i} value={i === 0 ? '' : opt} className={isDark ? 'bg-[#161616] text-white' : 'bg-white text-gray-800'}>
                        {opt}
                      </option>
                    ))}
                  </select>
                  {fieldErrors.serviceOfInterest && (
                    <span className="text-red-500 text-xs mt-1 block">{fieldErrors.serviceOfInterest}</span>
                  )}
                </div>
              </div>

              <div>
                <label className={`block text-[11px] font-bold mb-2 uppercase tracking-wider transition-colors ${isDark ? 'text-gray-300' : 'text-slate-500'}`}>
                  {content.form.message} *
                </label>
                <textarea 
                  rows={4} 
                  name="message"
                  value={formData.message}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-3.5 rounded-none border focus:outline-none focus:ring-2 focus:ring-[#ff4f00] focus:border-transparent transition-colors text-sm resize-none ${
                    fieldErrors.message ? 'border-red-500' : isDark ? 'border-[#333333]' : 'border-gray-200'
                  } ${isDark ? 'bg-[#161616] text-white' : 'bg-white text-gray-800'}`}
                ></textarea>
                {fieldErrors.message && (
                  <span className="text-red-500 text-xs mt-1 block">{fieldErrors.message}</span>
                )}
              </div>

              <div className="pt-2">
                <button 
                  type="submit" 
                  disabled={status === 'submitting'}
                  className="bg-[#ff4f00] hover:bg-[#e04500] disabled:bg-[#ff4f00]/60 text-white text-[11px] sm:text-xs font-bold px-8 py-4 rounded-none uppercase tracking-wider transition-all w-full sm:w-auto"
                >
                  {status === 'submitting' ? content.form.submitting : content.form.submit}
                </button>
              </div>

            </form>
          </div>

        </div>
      </div>
    </section>
  );
};
