import os
import sys
import glob
import time
import re
import json
import urllib.request
import subprocess
from typing import List, Dict, Any, Optional

# Asegura encoding UTF-8 en consola de Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Intentar importar librerías de IA
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


# =====================================================================
# UTILS: Carga de Archivos de Entorno (.env)
# =====================================================================
def load_dotenv():
    """Carga variables desde archivos .env, .env.local, etc. sin librerías externas."""
    env_files = [".env.local", ".env", ".env.example", "specs/.env"]
    for env_file in env_files:
        if os.path.exists(env_file):
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            parts = line.split("=", 1)
                            k = parts[0].strip()
                            v = parts[1].strip()
                            if "$env:" in k:
                                k = k.split(":")[-1].strip()
                            if "$env:" in v:
                                match = re.search(r'["\']([^"\']+)["\']', v)
                                if match:
                                    v = match.group(1)
                                else:
                                    v = v.split("=")[-1].strip()
                            v = v.strip('"').strip("'")
                            if k and v and k not in os.environ:
                                os.environ[k] = v
            except Exception:
                pass

load_dotenv()


# =====================================================================
# MODELOS DISPONIBLES EN CASCADA DE FALLBACK
# =====================================================================
DEFAULT_MODELS = [
    # 1. Gemini API (Google AI - Modelos oficiales de última generación)
    {'provider': 'gemini', 'name': 'gemini-3.5-flash'},
    {'provider': 'gemini', 'name': 'gemini-3.5-flash-lite'},
    {'provider': 'gemini', 'name': 'gemini-3-flash-preview'},
    {'provider': 'gemini', 'name': 'gemini-2.5-pro'},

    # 2. Groq API (Ultra rápido con modelos de alto razonamiento)
    {'provider': 'groq', 'name': 'qwen/qwen3.8-27b'},
    {'provider': 'groq', 'name': 'openai/gpt-oss-120b'},
    {'provider': 'groq', 'name': 'openai/gpt-oss-20b'},
    {'provider': 'groq', 'name': 'llama-3.3-70b-versatile'},

    # 3. OpenAI
    {'provider': 'openai', 'name': 'gpt-4o-mini'},
    {'provider': 'openai', 'name': 'gpt-4o'},

    # 4. OpenRouter API (Comunidad gratis)
    {'provider': 'openrouter', 'name': 'google/gemini-2.0-flash-exp:free'},
    {'provider': 'openrouter', 'name': 'meta-llama/llama-3.3-70b-instruct:free'},

    # 5. Ollama Local (100% Gratis, Privado y Local)
    {'provider': 'ollama', 'name': 'llama3.2:latest'},
    {'provider': 'ollama', 'name': 'llama3.1:latest'},
    {'provider': 'ollama', 'name': 'llama3.2'},
    {'provider': 'ollama', 'name': 'llama3.2:3b'},
    {'provider': 'ollama', 'name': 'llama3.2:1b'},
    {'provider': 'ollama', 'name': 'qwen2.5'}
]


class HarnessAgent:
    """
    Agente de Arnés de IA Completo y Versátil para Itiers.
    Capaz de realizar cualquier modificación de diseño, inserción de imágenes,
    carruseles, formularios, estilos, tipografías y lógica web solicitada.
    """

    def read_path_content(self, target_path: str) -> str:
        """Lee un archivo individual o concatena todos los archivos de una carpeta completa."""
        resolved = self.resolve_project_path(target_path)
        if not os.path.exists(resolved):
            return f"❌ La ruta '{resolved}' no existe."
            
        if os.path.isfile(resolved):
            try:
                with open(resolved, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                return f"❌ Error leyendo archivo: {e}"
                
        elif os.path.isdir(resolved):
            valid_exts = {".tsx", ".ts", ".jsx", ".js", ".css", ".md", ".json", ".html", ".py"}
            ignore_dirs = {".git", "node_modules", ".next", "__pycache__", "out", "build", ".harness_backups"}
            
            concatenated = []
            for root, dirs, files in os.walk(resolved):
                dirs[:] = [d for d in dirs if d not in ignore_dirs]
                for file in files:
                    if any(file.endswith(ext) for ext in valid_exts):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()
                                rel_p = os.path.relpath(file_path, os.getcwd()).replace("\\", "/")
                                concatenated.append(f"--- ARCHIVO: {rel_p} ---\n{content}\n")
                        except Exception:
                            pass
            
            if not concatenated:
                return "⚠️ La carpeta está vacía o no contiene código válido."
            return "\n".join(concatenated)

    def __init__(self):
        self.clients = {}
        self.design_specs = ""
        self.conversation_history = []
        self.installed_ollama_models = []
        self.prefer_ollama = os.environ.get("PREFER_OLLAMA", "").lower() in ["true", "1", "yes"]
        self.available_models = []
        self.last_backups = {}
        self.last_modified_file = None
        self.current_directory = "."
        self.setup_clients()
        self.load_design_specs()

    def setup_clients(self):
        """Configura los clientes de Ollama, Groq, Gemini, OpenRouter y OpenAI."""
        self.clients = {}
        ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").rstrip('/')
        ollama_api_url = f"{ollama_base_url}/v1"

        self.installed_ollama_models = self.detect_ollama_models(ollama_base_url)

        if HAS_OPENAI and (self.installed_ollama_models or self.prefer_ollama):
            try:
                self.clients['ollama'] = OpenAI(base_url=ollama_api_url, api_key="ollama", timeout=60.0)
            except Exception:
                pass

        gemini_key = os.environ.get("GEMINI_API_KEY")
        if gemini_key and HAS_GENAI:
            try:
                self.clients['gemini'] = genai.Client(api_key=gemini_key)
            except Exception:
                pass

        groq_key = os.environ.get("GROQ_API_KEY")
        if groq_key and HAS_OPENAI:
            try:
                self.clients['groq'] = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=groq_key, timeout=15.0)
            except Exception:
                pass

        openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        if openrouter_key and HAS_OPENAI:
            try:
                self.clients['openrouter'] = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=openrouter_key, timeout=15.0)
            except Exception:
                pass

        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key and HAS_OPENAI:
            try:
                self.clients['openai'] = OpenAI(api_key=openai_key, timeout=15.0)
            except Exception:
                pass

        self.rebuild_model_priority()

    def detect_ollama_models(self, base_url: str) -> List[str]:
        try:
            url = f"{base_url}/api/tags"
            req = urllib.request.Request(url, headers={'User-Agent': 'HarnessEngine/1.0'})
            with urllib.request.urlopen(req, timeout=1.5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return [m['name'] for m in data.get('models', [])]
        except Exception:
            pass
        return []

    def rebuild_model_priority(self):
        cloud_models = [m for m in DEFAULT_MODELS if m['provider'] != 'ollama']
        ollama_models = [{'provider': 'ollama', 'name': om} for om in self.installed_ollama_models]
        for m in DEFAULT_MODELS:
            if m['provider'] == 'ollama' and m['name'] not in [o['name'] for o in ollama_models]:
                ollama_models.append(m)

        if self.prefer_ollama:
            self.available_models = ollama_models + cloud_models
        else:
            self.available_models = cloud_models + ollama_models

    def load_design_specs(self):
        paths = [os.path.join("specs", "design.md"), "design-md-itiers.md"]
        for path in paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        self.design_specs = f.read()
                        return
                except Exception:
                    pass

    def call_llm(self, prompt: str, system_prompt: Optional[str] = None, include_design_specs: bool = False) -> str:
        base_system = (
            "Eres un Agente de Arnés de IA Inteligente y Versátil (Full-Featured AI Harness Agent).\n"
            "Tienes libertad total para editar, rediseñar, crear componentes, agregar/eliminar imágenes, carruseles,\n"
            "formularios, gráficos, secciones, modificar colores, tipografías y cualquier aspecto visual o funcional pedido por el usuario.\n"
            "Sé conciso, preciso y directo."
        )

        if include_design_specs and self.design_specs:
            base_system += f"\n\n--- MANUAL DE MARCA Y DISEÑO DE REFERENCIA ---\n{self.design_specs}\n----------------------------------------"

        final_system_prompt = f"{base_system}\n\n{system_prompt}" if system_prompt else base_system

        if not self.clients:
            return self._offline_fallback_response(prompt)

        errors_log = []
        for model_info in self.available_models:
            provider = model_info['provider']
            model_name = model_info['name']

            if provider not in self.clients:
                continue

            try:
                if provider == 'gemini':
                    response = self.clients['gemini'].models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(system_instruction=final_system_prompt, temperature=0.2)
                    )
                    if response and response.text:
                        return response.text.strip()

                elif provider in ['openai', 'groq', 'openrouter', 'ollama']:
                    response = self.clients[provider].chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": final_system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.2
                    )
                    if response and response.choices:
                        return response.choices[0].message.content.strip()
            except Exception as e:
                errors_log.append(f"{provider}/{model_name}: {str(e)[:80]}")
                continue

        return self._offline_fallback_response(prompt, errors_log)

    def _offline_fallback_response(self, prompt: str, errors_log: Optional[List[str]] = None) -> str:
        return "**[Harness Copilot]** No hay un modelo activo configurado. Por favor ingresa tu API Key o inicia Ollama."

    def clean_code(self, raw_code: str) -> str:
        match = re.search(r'```(?:tsx|typescript|jsx|javascript|python|html|css|json|sh|bash)?\n(.*?)\n```', raw_code, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return raw_code.replace("```tsx", "").replace("```python", "").replace("```", "").strip()

    def execute_command(self, cmd: str) -> str:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60, encoding='utf-8', errors='replace')
            return f"--- STDOUT ---\n{result.stdout.strip()}\n--- STDERR ---\n{result.stderr.strip()}\nExit Code: {result.returncode}"
        except Exception as e:
            return f"❌ Execution error: {e}"

    def resolve_project_path(self, raw_path: str) -> str:
        """Resuelve rutas de archivo sin asumir por defecto un archivo arbitrario."""
        if not raw_path or raw_path.strip() in ["", ".", "./"]:
            return ""

        p = raw_path.strip().strip("'").strip('"')
        p_clean = p.replace("\\", "/").lstrip("/")

        cwd_name = os.path.basename(os.getcwd())
        for prefix in [f"{cwd_name}/", "itiers-web-main/", "itiers-web/"]:
            if p_clean.lower().startswith(prefix.lower()):
                p_clean = p_clean[len(prefix):]
                break

        p_clean = p_clean.lstrip("/")
        if os.path.exists(p_clean):
            return p_clean

        target_name = os.path.basename(p_clean).rstrip("/")
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in [".next", "node_modules", ".git", "__pycache__", "out", "build", ".harness_backups"]]
            for f in files:
                if f.lower() == target_name.lower():
                    return os.path.relpath(os.path.join(root, f), ".").replace("\\", "/")

        return p_clean

    def parse_command_input(self, text: str, default_path: Optional[str] = None) -> tuple:
        text = text.strip()
        if not text:
            return "", (default_path if default_path else "")

        tokens = text.split()
        if len(tokens) == 1:
            if "." in tokens[0] or any(ext in tokens[0] for ext in [".tsx", ".ts", ".jsx", ".js"]):
                return "", self.resolve_project_path(tokens[0])
            return tokens[0], (default_path if default_path else "")

        last_tok = tokens[-1].strip(" '\"`(),;:")
        if any(last_tok.lower().endswith(ext) for ext in [".tsx", ".ts", ".jsx", ".js", ".css", ".md", ".json", ".html"]):
            return " ".join(tokens[:-1]).strip(), self.resolve_project_path(last_tok)

        return text, (default_path if default_path else "")

    def audit_component(self, filepath: str) -> str:
        resolved = self.resolve_project_path(filepath)
        if not resolved or not os.path.exists(resolved):
            return "❌ Debes seleccionar un archivo válido para auditar."
        code = self.read_path_content(resolved)
        system_prompt = "Eres el Auditor de Calidad del Arnés de IA. Analiza accesibilidad WCAG AA y calidad."
        return self.call_llm(f"Audita '{resolved}':\n\n```\n{code}\n```", system_prompt, include_design_specs=True)

    def audit_geo(self, filepath: str) -> str:
        resolved = self.resolve_project_path(filepath)
        if not resolved or not os.path.exists(resolved):
            return "❌ Debes seleccionar un archivo válido para auditar SEO/GEO."
        code = self.read_path_content(resolved)
        return self.call_llm(f"Audita SEO y GEO para '{resolved}':\n\n```\n{code}\n```", "Especialista SEO y GEO.")

    def audit_all(self):
        for d in ["app", "components"]:
            if os.path.exists(d):
                for filepath in glob.glob(os.path.join(d, "**", "*.tsx"), recursive=True):
                    print(self.audit_component(filepath))

    def generate_or_edit_file(self, description: str, target_path: str) -> bool:
        resolved_path = self.resolve_project_path(target_path)
        if not resolved_path:
            print("❌ No se especificó un archivo objetivo.")
            return False

        system_prompt = (
            "Eres un Senior Software Architect y Developer parte del Arnés de IA de Itiers.\n"
            "Stack tecnológico: Next.js (App Router), React 19, Tailwind CSS v4 y TypeScript.\n"
            "LIBERTAD TOTAL DE DISEÑO Y ESTRUCTURA:\n"
            "1. Puedes agregar imágenes (<Image src='...' fill /> o width/height), eliminarlas, agrandarlas o disminuirlas.\n"
            "2. Puedes crear o editar carruseles de fotos, agregar botones, secciones, formularios interactivos, gráficos, estadísticas, testimonios o redes sociales.\n"
            "3. Puedes cambiar colores, tipografías, estilos y adaptar la página entera al gusto y diseño exacto que el usuario solicite.\n"
            "4. PRESERVACIÓN: Mantén los exports requeridos (ej. 'export const', 'export type').\n"
            "5. NEXT/IMAGE: Toda etiqueta <Image /> DEBE tener 'fill' O 'width={...}' y 'height={...}' obligatoriamente.\n"
            "Devuelve ÚNICAMENTE el código envuelto en un bloque markdown (```lenguaje ... ```)."
        )

        existing_code = ""
        if os.path.exists(resolved_path):
            try:
                with open(resolved_path, "r", encoding="utf-8") as f:
                    existing_code = f.read()
                self.last_backups[resolved_path] = existing_code
                self.last_modified_file = resolved_path
                os.makedirs(".harness_backups", exist_ok=True)
                bak_name = resolved_path.replace("/", "_").replace("\\", "_") + ".bak"
                with open(os.path.join(".harness_backups", bak_name), "w", encoding="utf-8") as bf:
                    bf.write(existing_code)
            except Exception:
                pass

        if existing_code:
            prompt = f"Modifica el archivo existente '{resolved_path}' para cumplir con: '{description}'.\n\nCódigo Actual:\n```\n{existing_code}\n```"
        else:
            prompt = f"Crea un nuevo archivo para '{resolved_path}' con la especificación: '{description}'."

        try:
            raw_response = self.call_llm(prompt, system_prompt, include_design_specs=True)
            clean_code = self.clean_code(raw_response)

            if not clean_code.strip():
                raise ValueError("Código vacío devuelto por la IA.")

            dir_name = os.path.dirname(resolved_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            with open(resolved_path, "w", encoding="utf-8") as f:
                f.write(clean_code)

            return True
        except Exception as e:
            print(f"❌ Error al generar archivo: {e}")
            return False

    def revert_last_change(self, target_path: Optional[str] = None) -> tuple:
        path_to_revert = self.resolve_project_path(target_path) if target_path else self.last_modified_file
        if not path_to_revert:
            return False, "⚠️ No hay archivos recientes para deshacer."

        prev_code = self.last_backups.get(path_to_revert)
        if not prev_code:
            bak_file = os.path.join(".harness_backups", path_to_revert.replace("/", "_").replace("\\", "_") + ".bak")
            if os.path.exists(bak_file):
                with open(bak_file, "r", encoding="utf-8") as bf:
                    prev_code = bf.read()

        if not prev_code:
            return False, f"⚠️ No se encontró respaldo para '{path_to_revert}'."

        if prev_code == "__NEW_FILE__":
            if os.path.exists(path_to_revert):
                os.remove(path_to_revert)
            return True, f"✅ Archivo '{path_to_revert}' eliminado (se deshizo la creación)."

        with open(path_to_revert, "w", encoding="utf-8") as f:
            f.write(prev_code)
        return True, f"✅ Archivo '{path_to_revert}' restaurado con éxito."

    def apply_code_change(self, instruction: str, target_path: Optional[str] = None) -> tuple:
        if not target_path or not target_path.strip():
            return False, "🛡️ **Protección de Archivo:** No has seleccionado ningún archivo objetivo en la interfaz. Por favor haz clic en **'Objetivo Actual'** en la barra lateral para elegir el archivo que deseas editar antes de aplicar cambios."

        resolved_path = self.resolve_project_path(target_path)
        success = self.generate_or_edit_file(instruction, resolved_path)
        if not success:
            return False, f"❌ No se pudo modificar el archivo '{resolved_path}'."

        # Validar TypeScript
        ts_check = subprocess.run("npx tsc --noEmit", shell=True, capture_output=True, text=True)
        if ts_check.returncode != 0:
            ts_err = (ts_check.stdout or ts_check.stderr).strip()[:300]
            return False, f"🛡️ **Rollback de Seguridad:** El cambio provocó un error de TypeScript:\n```\n{ts_err}\n```\nSe restauró la versión anterior."

        return True, f"✅ Modificación completada y validada con éxito en `{resolved_path}`."

    def answer_query(self, user_message: str, selected_file: Optional[str] = None) -> str:
        if selected_file and os.path.exists(selected_file):
            content = self.read_path_content(selected_file)
            prompt = f"Analiza el archivo '{selected_file}':\n```tsx\n{content}\n```\n\nPregunta: {user_message}"
            return self.call_llm(prompt, "Analista de código experto de Itiers.", include_design_specs=True)
        return self.call_llm(user_message, "Asistente Corporativo de Itiers Data Sense.")

    def process_chat(self, user_message: str, selected_file: Optional[str] = None, edit_mode: bool = False) -> tuple:
        if edit_mode and not selected_file:
            return "🛡️ **Selecciona un archivo objetivo:** Para editar o modificar código, debes seleccionar obligatoriamente un archivo en la barra lateral (botón 'Ninguno seleccionado').", None, self.current_directory

        if edit_mode:
            ok, msg = self.apply_code_change(user_message, target_path=selected_file)
            return msg, selected_file, self.current_directory
        else:
            reply = self.answer_query(user_message, selected_file=selected_file)
            return reply, selected_file, self.current_directory

    def set_api_key(self, key_type: str, key_value: str):
        k_lower = key_type.lower()
        var_name = "GEMINI_API_KEY" if "gemini" in k_lower else ("GROQ_API_KEY" if "groq" in k_lower else ("OPENAI_API_KEY" if "openai" in k_lower else "OPENROUTER_API_KEY"))
        os.environ[var_name] = key_value
        env_path = ".env.local"
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        new_lines = [l for l in lines if not l.startswith(f"{var_name}=")]
        new_lines.append(f"{var_name}={key_value}\n")
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        self.setup_clients()