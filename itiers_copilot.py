#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
ITIERS AI HARNESS COPILOT
=============================================================================
"""

import os
import sys
import json
import time
import shutil
import socket
import urllib.parse
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

if sys.platform == "win32":
    try:
        if sys.stdout: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr: sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from harness_engine import HarnessAgent

PORT = 8765
HOST = "127.0.0.1"
DEV_PORT = 3000

agent = HarnessAgent()
dev_process = None
HISTORY_FILE = ".copilot_chats.json"

def load_chats_db():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    default_id = str(int(time.time()))
    return {
        "active_id": default_id,
        "chats": {
            default_id: {
                "title": "Chat Inicial",
                "messages": [{
                    "role": "assistant",
                    "text": "¡Hola! El arnés está configurado con tus claves de `.env.local`. Selecciona un archivo en la barra lateral para comenzar con total libertad de edición."
                }]
            }
        }
    }

def save_chats_db(db):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

chats_db = load_chats_db()

def is_port_3000_open():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.4)
            return s.connect_ex(('127.0.0.1', DEV_PORT)) == 0
    except Exception:
        return False

def start_dev_server():
    global dev_process
    if is_port_3000_open():
        return True, "El servidor local ya estaba activo en http://localhost:3000."
    try:
        dev_process = subprocess.Popen("npm run dev", shell=True)
        for _ in range(30):
            time.sleep(0.5)
            if is_port_3000_open():
                return True, "Servidor Next.js iniciado con éxito en http://localhost:3000."
        return False, "El servidor tardó más de 15 segundos en responder."
    except Exception as e:
        return False, f"Error al ejecutar npm run dev: {e}"

HTML_PAGE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Itiers AI Copilot — Suite de Harness & QA</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }
    
    :root {
      --bg: #FFFFFF;
      --surface: #FAFAFA;
      --surface-elevated: #F0F0F0;
      --text: #1C1917;
      --text-muted: #4d4d4d;
      --border: #b2b2b2;
      --brand-gray: #4d4d4d;
      --primary: #ff4f00;
      --primary-hover: #e04500;
      --accent: #1F1F1F;
      --radius-sm: 12px;
      --radius-md: 16px;
      --sidebar-bg: #FAFAFA;
      --chat-card-bg: #FFFFFF;
      --user-card-bg: #F4F4F5;
      --input-bg: #FFFFFF;
    }

    [data-theme="dark"] {
      --bg: #0F0F0F;
      --surface: #1A1A1A;
      --surface-elevated: #141414;
      --text: #b2b2b2;
      --text-muted: #898a8d;
      --border: #333333;
      --brand-gray: #898a8d;
      --primary: #ff4f00;
      --primary-hover: #e04500;
      --accent: #F2F2F2;
      --sidebar-bg: #121212;
      --chat-card-bg: #121212;
      --user-card-bg: #181818;
      --input-bg: #181818;
    }

    body {
      background-color: var(--bg);
      color: var(--text);
      font-family: 'Nunito', sans-serif;
      margin: 0;
      padding: 0;
      display: flex;
      height: 100vh;
      overflow: hidden;
      transition: background-color 0.2s, color 0.2s;
    }

    sidebar { width: 320px; background-color: var(--sidebar-bg); border-right: 1px solid var(--border); display: flex; flex-direction: column; justify-content: space-between; flex-shrink: 0; z-index: 20; transition: background-color 0.2s, border-color 0.2s; }
    main { flex: 1; display: flex; flex-direction: column; height: 100%; background-color: var(--bg); position: relative; transition: background-color 0.2s; overflow: hidden; }
    
    .brand-header { padding: 16px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
    .brand-left { display: flex; align-items: center; gap: 12px; }
    .brand-logo { width: 36px; height: 36px; border-radius: var(--radius-sm); background: linear-gradient(135deg, var(--primary), #b33600); display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; font-size: 14px; box-shadow: 0 4px 12px rgba(255,79,0,0.3); }
    .brand-title { font-size: 14px; font-weight: 700; color: var(--text); display: flex; align-items: center; gap: 6px; }
    .brand-tag { font-size: 10px; padding: 2px 6px; border-radius: 10px; background: rgba(255,79,0,0.15); color: var(--primary); border: 1px solid rgba(255,79,0,0.3); font-weight: 600; }
    
    .new-chat-btn { background: var(--primary); border: none; border-radius: 8px; width: 32px; height: 32px; color: white; font-size: 16px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background 0.2s; }
    .new-chat-btn:hover { background: var(--primary-hover); }

    .widget-box { padding: 16px; display: flex; flex-direction: column; gap: 16px; }
    .widget-label { font-size: 11px; font-weight: 600; text-transform: uppercase; color: var(--text-muted); display: block; margin-bottom: 6px; }
    
    .target-btn { width: 100%; background: var(--input-bg); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 10px 12px; font-size: 12px; color: var(--text); text-align: left; display: flex; justify-content: space-between; align-items: center; cursor: pointer; transition: all 0.2s; }
    .target-btn:hover { border-color: var(--primary); }
    
    .mode-toggle-btn { width: 100%; padding: 12px; border-radius: var(--radius-sm); border: 1px solid var(--border); background: var(--input-bg); display: flex; align-items: center; justify-content: space-between; cursor: pointer; transition: all 0.2s; }
    .mode-toggle-btn.active { border-color: var(--primary); background: rgba(255,79,0,0.1); }
    
    .toggle-switch { width: 36px; height: 20px; border-radius: 20px; background: #374151; padding: 2px; transition: background 0.2s; display: flex; align-items: center; }
    .toggle-switch.active { background: var(--primary); }
    .toggle-knob { width: 16px; height: 16px; border-radius: 50%; background: #9CA3AF; transition: transform 0.2s; }
    .toggle-switch.active .toggle-knob { transform: translateX(16px); background: white; }

    .chats-list-container { flex: 1; overflow-y: auto; padding: 0 16px; display: flex; flex-direction: column; gap: 4px; border-top: 1px solid var(--border); margin-top: 8px; padding-top: 12px; }
    .chat-history-row { display: flex; align-items: center; justify-content: space-between; border-radius: 8px; transition: background 0.2s; }
    .chat-history-row:hover { background: var(--surface); }
    .chat-history-row.active { background: rgba(255,79,0,0.15); border: 1px solid rgba(255,79,0,0.3); }

    .chat-history-item { flex: 1; font-size: 12px; padding: 8px 10px; color: var(--text-muted); cursor: pointer; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .chat-history-row.active .chat-history-item { color: var(--primary); font-weight: 600; }
    
    .delete-chat-btn { background: none; border: none; color: var(--text-muted); font-size: 13px; padding: 4px 8px; cursor: pointer; transition: color 0.2s; }
    .delete-chat-btn:hover { color: #EF4444; }

    .sidebar-footer { padding: 16px; border-top: 1px solid var(--border); background: var(--surface); display: flex; flex-direction: column; gap: 12px; }
    .model-status { display: flex; align-items: center; gap: 8px; }
    .status-dot { width: 8px; height: 8px; border-radius: 50%; background: #10B981; box-shadow: 0 0 8px #10B981; }
    
    .btn-secondary { width: 100%; padding: 8px 12px; border-radius: 8px; background: rgba(255,79,0,0.1); border: 1px solid rgba(255,79,0,0.3); color: var(--primary); font-size: 12px; font-weight: 600; cursor: pointer; text-align: center; transition: all 0.2s; }
    .btn-secondary:hover { background: rgba(255,79,0,0.2); }
    
    .top-bar { height: 56px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; padding: 0 24px; background: var(--surface); flex-shrink: 0; }
    .chat-area { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 20px; max-width: 860px; width: 100%; margin: 0 auto; }
    
    .msg-card { display: flex; gap: 16px; padding: 20px; border-radius: var(--radius-md); border: 1px solid var(--border); background: var(--chat-card-bg); transition: background-color 0.2s, border-color 0.2s; }
    .msg-card.user { background: var(--user-card-bg); margin-left: 48px; }
    .msg-card.assistant { background: var(--chat-card-bg); margin-right: 48px; }
    .msg-avatar { width: 32px; height: 32px; border-radius: 8px; background: var(--primary); display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; font-size: 12px; flex-shrink: 0; }
    .msg-avatar.user-av { background: #4B5563; }
    .msg-content { flex: 1; font-size: 14px; line-height: 1.6; color: var(--text); }
    .msg-meta { font-size: 11px; font-weight: 600; color: var(--primary); margin-bottom: 4px; display: flex; justify-content: space-between; }
    
    .input-container { padding: 16px; border-top: 1px solid var(--border); background: var(--surface); max-width: 860px; width: 100%; margin: 0 auto; transition: background-color 0.2s, border-color 0.2s; flex-shrink: 0; }
    .input-wrapper { position: relative; display: flex; align-items: center; }
    .chat-textarea { 
      flex: 1;
      background: var(--input-bg); 
      border: 1px solid var(--border); 
      border-radius: var(--radius-md); 
      padding: 14px 16px;
      font-size: 14px; 
      color: var(--text); 
      resize: none; 
      outline: none; 
      transition: border-color 0.2s, background-color 0.2s, color 0.2s; 
      max-height: 180px; 
      overflow-y: auto;  
      line-height: 1.5;
    }
    .chat-textarea:focus { border-color: var(--primary); }
    .send-btn { 
      position: static; 
      transform: none;
      width: 48px; 
      height: 48px; 
      border-radius: var(--radius-sm); 
      background: var(--primary); 
      border: none; 
      color: white; 
      font-weight: bold; 
      font-size: 18px; 
      cursor: pointer; 
      display: flex; 
      align-items: center; 
      justify-content: center; 
      transition: background 0.2s, transform 0.1s;
      flex-shrink: 0;
    }
    .send-btn:hover { background: var(--primary-hover); }
    .send-btn:active { transform: scale(0.95); }
    
    .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); backdrop-filter: blur(4px); z-index: 50; display: flex; align-items: center; justify-content: center; padding: 16px; }
    .modal-box { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); max-width: 440px; width: 100%; padding: 24px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5); display: flex; flex-direction: column; gap: 16px; }
    .modal-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 12px; font-weight: bold; font-size: 14px; color: var(--text); }
    .close-btn { background: none; border: none; color: var(--text-muted); font-size: 18px; cursor: pointer; }
    .close-btn:hover { color: var(--text); }
    
    .form-select { width: 100%; background: var(--input-bg); border: 1px solid var(--border); border-radius: 10px; padding: 10px; font-size: 13px; color: var(--text); outline: none; margin-top: 6px; }
    .btn-primary { width: 100%; padding: 10px; border-radius: 10px; background: var(--primary); border: none; color: white; font-size: 13px; font-weight: bold; cursor: pointer; transition: background 0.2s; }
    .btn-primary:hover { background: var(--primary-hover); }
    
    /* ESTILOS EXACTOS PARA EL EXPLORADOR */
    .slide-panel { position: fixed; top: 0; bottom: 0; right: 0; width: 460px; background: var(--surface); border-left: 1px solid var(--border); z-index: 50; transform: translateX(100%); transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.2s; display: flex; flex-direction: column; box-shadow: -15px 0 30px rgba(0,0,0,0.6); }
    .slide-panel.open { transform: translateX(0); }
    .tree-container { flex: 1; overflow-y: auto; padding: 20px; background: var(--bg); transition: background-color 0.2s; }
    
    .tree-folder-header { 
      background: var(--surface-elevated); 
      border: 1px solid var(--border); 
      border-radius: 8px; 
      padding: 10px 14px; 
      font-size: 12px; 
      color: var(--text); 
      display: flex; 
      align-items: center; 
      justify-content: space-between; 
      cursor: pointer; 
      transition: background 0.2s, border-color 0.2s; 
      margin-bottom: 6px; 
    }
    .tree-folder-header:hover { 
      background: var(--surface); 
      border-color: var(--primary); 
    }
    
    .tree-file-item { 
      font-size: 12px; 
      padding: 8px 12px; 
      border-radius: 6px; 
      color: var(--text-muted); 
      cursor: pointer; 
      display: flex; 
      align-items: center; 
      gap: 10px; 
      margin-bottom: 2px; 
      font-family: monospace; 
      transition: all 0.15s; 
      border: 1px solid transparent; 
    }
    .tree-file-item:hover { 
      background: var(--input-bg); 
      color: var(--text); 
      border-color: var(--border); 
    }
    .tree-file-item.selected { 
      background: rgba(255,79,0,0.15); 
      color: var(--primary); 
      border-color: rgba(255,79,0,0.4); 
      font-weight: bold; 
    }
    
    .hidden { display: none !important; }
  </style>
</head>
<body>

  <sidebar>
    <div>
      <div class="brand-header">
        <div class="brand-left">
          <div class="brand-logo">IT</div>
          <div>
            <div class="brand-title">
              Itiers Copilot
              <span class="brand-tag">Harness</span>
            </div>
          </div>
        </div>
        <button onclick="createNewChat()" class="new-chat-btn" title="Nuevo Chat">＋</button>
      </div>

      <div class="widget-box" style="padding-bottom: 8px;">
        <div>
          <span class="widget-label">Objetivo Actual (Seleccionar Archivo)</span>
          <button onclick="openFileExplorer()" class="target-btn">
            <span id="targetDisplay" style="font-family: monospace; color: var(--primary);">Ninguno seleccionado</span>
            <span>📂</span>
          </button>
        </div>

        <div>
          <button type="button" id="sidebarEditToggle" onclick="toggleEditMode()" class="mode-toggle-btn">
            <div style="display: flex; align-items: center; gap: 10px;">
              <span id="sidebarEditIcon" style="font-size: 16px;">💬</span>
              <div style="text-align: left;">
                <div id="sidebarEditTitle" style="font-size: 12px; font-weight: bold; color: var(--text);">Modo Consulta</div>
                <div id="sidebarEditSub" style="font-size: 10px; color: var(--text-muted);">Sólo lectura y análisis</div>
              </div>
            </div>
            <div id="sidebarEditSwitch" class="toggle-switch">
              <div id="sidebarEditKnob" class="toggle-knob"></div>
            </div>
          </button>
        </div>
      </div>

      <div style="padding: 0 16px;"><span class="widget-label">Historial de Chats</span></div>
      <div id="chatsListContainer" class="chats-list-container"></div>
    </div>

    <div class="sidebar-footer">
      <div class="model-status">
        <div id="statusDot" class="status-dot"></div>
        <div>
          <div id="modelBadge" style="font-size: 12px; font-weight: 600; color: var(--text);">Gemini / Ollama</div>
          <div id="statusSubtext" style="font-size: 10px; color: var(--text-muted);">Claves desde .env.local</div>
        </div>
      </div>
      <button onclick="openKeySelectorModal()" class="btn-secondary">
        ⚙️ Seleccionar Proveedor de IA
      </button>
    </div>
  </sidebar>

  <main>
    <header class="top-bar">
      <span style="font-size: 13px; font-weight: 500; color: var(--text);">Itiers AI Copilot — Libertad Total de Edición y Diseño</span>
      
      <div style="display: flex; align-items: center; gap: 10px;">
        <button id="webBtn" onclick="handleWebClick()" style="padding: 6px 12px; border-radius: 8px; background: var(--input-bg); border: 1px solid var(--border); color: var(--text); font-size: 12px; cursor: pointer; display: flex; align-items: center; gap: 6px; transition: all 0.2s;">
          <span id="webDot" style="width: 8px; height: 8px; border-radius: 50%; background: #6B7280; display: inline-block;"></span>
          <span id="webText">🌐 Iniciar y Abrir Web (localhost:3000)</span>
        </button>

        <button onclick="toggleTheme()" title="Cambiar modo claro / oscuro" style="padding: 6px 10px; border-radius: 8px; background: var(--input-bg); border: 1px solid var(--border); color: var(--text); font-size: 13px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s;">
          🌓
        </button>
      </div>
    </header>

    <div id="chatContainer" class="chat-area"></div>

    <div class="input-container">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <span id="chatEditLabel" style="font-size: 11px; font-weight: bold; color: var(--text-muted);">💬 Modo Consulta (Lectura)</span>
        <span id="targetInputBadge" style="font-family: monospace; font-size: 11px; color: var(--primary);">Ningún archivo seleccionado</span>
      </div>

      <form onsubmit="sendMessage(event)" class="input-wrapper">
        <div style="display: flex; align-items: flex-end; gap: 10px; width: 100%; position: relative;">
          <textarea id="messageInput" rows="1" placeholder="Escribe tu solicitud de diseño, cambios o consultas..." oninput="autoResizeTextarea(this)" onkeydown="handleKey(event)" class="chat-textarea"></textarea>
          <button type="submit" class="send-btn" title="Enviar mensaje">➤</button>
        </div>
      </form>
    </div>
  </main>

  <!-- MODAL SELECCIÓN MODELOS -->
  <div id="keySelectorModal" class="modal-overlay hidden">
    <div class="modal-box">
      <div class="modal-header">
        <span>⚙️ Seleccionar Proveedor de IA Activo</span>
        <button onclick="closeKeySelectorModal()" class="close-btn">&times;</button>
      </div>
      <div>
        <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 12px;">Tus claves API se leen de forma automática y segura desde tu archivo <code>.env.local</code>. Elige cuál deseas usar:</p>
        <label class="widget-label">Proveedor / Motor:</label>
        <select id="modelProviderSelect" class="form-select">
          <option value="gemini">Google Gemini API (.env.local)</option>
          <option value="groq">Groq API (.env.local)</option>
          <option value="openai">OpenAI GPT-4o (.env.local)</option>
          <option value="ollama">Ollama Local (100% Privado / Sin Internet)</option>
        </select>
      </div>
      <div style="display: flex; gap: 8px; margin-top: 8px;">
        <button onclick="saveApiKeyModal()" class="btn-primary">Guardar Selección</button>
      </div>
    </div>
  </div>

  <!-- EXPLORADOR DE ARCHIVOS -->
  <div id="fileExplorerOverlay" onclick="closeFileExplorer()" class="modal-overlay hidden" style="background: rgba(0,0,0,0.5);"></div>
  <div id="fileExplorerPanel" class="slide-panel">
    <div class="modal-header" style="padding: 16px; background: var(--sidebar-bg); border-bottom: 1px solid var(--border);">
      <span>📂 Explorador de Código (Proyecto Itiers)</span>
      <button onclick="closeFileExplorer()" class="close-btn">&times;</button>
    </div>
    <div class="tree-container" id="fileTreeContainer"></div>
  </div>

  <script>
    let globalSelectedTarget = "";
    let isEditModeActive = false;
    let isServerRunning = false;
    let isStartingServer = false;

    async function loadChats() {
      const res = await fetch('/api/chats');
      const data = await res.json();
      renderChatsList(data);
    }

    function renderChatsList(db) {
      const container = document.getElementById('chatsListContainer');
      container.innerHTML = '';
      
      const chatIds = Object.keys(db.chats).reverse();
      chatIds.forEach(id => {
        const chat = db.chats[id];
        const row = document.createElement('div');
        row.className = `chat-history-row ${id === db.active_id ? 'active' : ''}`;
        
        const item = document.createElement('div');
        item.className = 'chat-history-item';
        item.innerText = chat.title || "Chat sin título";
        item.onclick = () => switchChat(id);
        
        const delBtn = document.createElement('button');
        delBtn.className = 'delete-chat-btn';
        delBtn.innerHTML = '🗑️';
        delBtn.title = 'Eliminar chat';
        delBtn.onclick = (e) => { e.stopPropagation(); deleteChat(id); };
        
        row.appendChild(item);
        row.appendChild(delBtn);
        container.appendChild(row);
      });

      const activeChat = db.chats[db.active_id];
      const chatContainer = document.getElementById('chatContainer');
      chatContainer.innerHTML = '';
      if (activeChat && activeChat.messages) {
        activeChat.messages.forEach(m => {
          appendMessageUI(m.role === 'user' ? 'user' : 'assistant', m.text, false);
        });
      }
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    async function createNewChat() {
      const res = await fetch('/api/chats/new', { method: 'POST' });
      const data = await res.json();
      renderChatsList(data);
    }

    async function switchChat(chatId) {
      const res = await fetch('/api/chats/switch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id: chatId })
      });
      const data = await res.json();
      renderChatsList(data);
    }

    async function deleteChat(chatId) {
      if (!confirm("¿Estás seguro de eliminar este chat?")) return;
      const res = await fetch('/api/chats/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id: chatId })
      });
      const data = await res.json();
      renderChatsList(data);
    }

    function toggleEditMode() {
      if (!globalSelectedTarget && !isEditModeActive) {
        alert("⚠️ Selecciona primero un archivo objetivo en la barra lateral antes de activar el Modo Edición.");
        openFileExplorer();
        return;
      }
      isEditModeActive = !isEditModeActive;
      updateEditModeUi();
    }

    function updateEditModeUi() {
      const chatLabel = document.getElementById('chatEditLabel');
      const sideTitle = document.getElementById('sidebarEditTitle');
      const sideSub = document.getElementById('sidebarEditSub');
      const sideSwitch = document.getElementById('sidebarEditSwitch');
      const sideToggle = document.getElementById('sidebarEditToggle');

      if (isEditModeActive) {
        if (chatLabel) { chatLabel.innerText = "⚡ Modo Edición ACTIVO"; chatLabel.style.color = "#ff7333"; }
        if (sideTitle) { sideTitle.innerText = "Modo Edición ACTIVO"; sideTitle.style.color = "#ff7333"; }
        if (sideSub) { sideSub.innerText = "Edición libre y conectada"; sideSub.style.color = "#ff7333"; }
        if (sideSwitch) sideSwitch.classList.add('active');
        if (sideToggle) sideToggle.classList.add('active');
      } else {
        if (chatLabel) { chatLabel.innerText = "💬 Modo Consulta (Lectura)"; chatLabel.style.color = "#9CA3AF"; }
        if (sideTitle) { sideTitle.innerText = "Modo Consulta"; sideTitle.style.color = "#E5E7EB"; }
        if (sideSub) { sideSub.innerText = "Sólo lectura y análisis"; sideSub.style.color = "#9CA3AF"; }
        if (sideSwitch) sideSwitch.classList.remove('active');
        if (sideToggle) sideToggle.classList.remove('active');
      }
    }

    function openKeySelectorModal() { document.getElementById('keySelectorModal').classList.remove('hidden'); }
    function closeKeySelectorModal() { document.getElementById('keySelectorModal').classList.add('hidden'); }

    async function saveApiKeyModal() {
      const prov = document.getElementById('modelProviderSelect').value;
      const res = await fetch('/api/set_key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: prov })
      });
      const data = await res.json();
      alert(data.message);
      closeKeySelectorModal();
    }

    function openFileExplorer() {
      document.getElementById('fileExplorerOverlay').classList.remove('hidden');
      document.getElementById('fileExplorerPanel').classList.add('open');
      const container = document.getElementById('fileTreeContainer');
      container.innerHTML = '<div style="color: #9CA3AF; padding: 10px;">Escaneando estructura del proyecto...</div>';
      
      fetch('/api/fs/tree').then(res => res.json()).then(data => {
        container.innerHTML = '';
        buildInteractiveTree(data.tree, container);
      }).catch(() => {
        container.innerHTML = '<div style="color: red; padding: 10px;">Error cargando explorador.</div>';
      });
    }

    function closeFileExplorer() {
      document.getElementById('fileExplorerOverlay').classList.add('hidden');
      document.getElementById('fileExplorerPanel').classList.remove('open');
    }

    // REDISEÑO INTERACTIVO DEL ÁRBOL DE ARCHIVOS
    function buildInteractiveTree(nodes, container) {
      container.innerHTML = '';
      
      const folders = nodes.filter(n => n.type === 'folder');
      const files = nodes.filter(n => n.type === 'file');

      folders.forEach(folder => {
        const folderDiv = document.createElement('div');
        folderDiv.style.marginBottom = '6px';

        const header = document.createElement('div');
        header.className = "tree-folder-header";
        header.innerHTML = `
          <div style="display: flex; align-items: center; gap: 8px;">
            <span>📁</span>
            <span style="color: #F59E0B; font-weight: 600;">${folder.name}/</span>
          </div>
          <span class="folder-arrow" style="font-size: 10px; color: #888;">▼</span>
        `;

        const subContainer = document.createElement('div');
        subContainer.style.paddingLeft = '14px';
        subContainer.style.marginTop = '4px';
        subContainer.style.display = 'none'; // Colapsadas por defecto

        header.onclick = () => {
          const arrow = header.querySelector('.folder-arrow');
          if (subContainer.style.display === 'none') {
            subContainer.style.display = 'block';
            if (arrow) arrow.innerText = '▲';
          } else {
            subContainer.style.display = 'none';
            if (arrow) arrow.innerText = '▼';
          }
        };

        folderDiv.appendChild(header);
        
        if (folder.children && folder.children.length > 0) {
          buildInteractiveTree(folder.children, subContainer);
        }
        folderDiv.appendChild(subContainer);
        container.appendChild(folderDiv);
      });

      files.forEach(file => {
        const item = document.createElement('div');
        const isSelected = globalSelectedTarget === file.path;
        item.className = `tree-file-item ${isSelected ? 'selected' : ''}`;
        item.innerHTML = `<span>📄</span><span>${file.path}</span>`;
        item.onclick = (e) => {
          e.stopPropagation();
          globalSelectedTarget = file.path;
          document.getElementById('targetDisplay').innerText = globalSelectedTarget;
          document.getElementById('targetInputBadge').innerText = globalSelectedTarget;
          closeFileExplorer();
        };
        container.appendChild(item);
      });
    }

    async function checkDevStatus() {
      try {
        const res = await fetch('/api/dev_status');
        const data = await res.json();
        isServerRunning = data.running;
        updateDevUi(data.running);
      } catch (e) {}
    }

    function updateDevUi(running) {
      const dot = document.getElementById('webDot');
      const text = document.getElementById('webText');
      if (!dot || !text) return;
      if (running) {
        dot.style.background = "#10B981";
        dot.style.boxShadow = "0 0 8px #10B981";
        text.innerText = "🌐 Abrir Web en Vivo (localhost:3000)";
      } else {
        dot.style.background = "#6B7280";
        dot.style.boxShadow = "none";
        text.innerText = "🌐 Iniciar y Abrir Web (localhost:3000)";
      }
    }

    async function handleWebClick() {
      if (isServerRunning) { window.open('http://localhost:3000', '_blank'); return; }
      if (isStartingServer) return;
      isStartingServer = true;
      const text = document.getElementById('webText');
      const dot = document.getElementById('webDot');
      if (text) text.innerText = "Iniciando Next.js...";
      if (dot) dot.style.background = "#F59E0B";

      try {
        const res = await fetch('/api/dev_start', { method: 'POST' });
        const data = await res.json();
        isStartingServer = false;
        if (data.running) {
          isServerRunning = true;
          updateDevUi(true);
          window.open('http://localhost:3000', '_blank');
        } else {
          updateDevUi(false);
          alert('Aviso: ' + data.message);
        }
      } catch (e) {
        isStartingServer = false;
        updateDevUi(false);
        alert('Error al iniciar servidor: ' + e);
      }
    }

    async function sendMessage(e) {
      if (e) e.preventDefault();
      const input = document.getElementById('messageInput');
      const text = input.value.trim();
      if (!text) return;

      if (isEditModeActive && !globalSelectedTarget) {
        alert("⚠️ Selecciona un archivo objetivo antes de aplicar cambios.");
        openFileExplorer();
        return;
      }

      appendMessageUI('user', text, true);
      input.value = '';
      input.style.height = 'auto';

      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, target_file: globalSelectedTarget, edit_mode: isEditModeActive })
      });
      const data = await res.json();
      renderChatsList(data.db);
    }

    function appendMessageUI(role, text, scrollToBottom = true) {
      const chat = document.getElementById('chatContainer');
      const div = document.createElement('div');
      div.className = `msg-card ${role}`;
      div.innerHTML = `
        <div class="msg-avatar ${role === 'user' ? 'user-av' : ''}">${role === 'user' ? 'Tú' : 'IT'}</div>
        <div class="msg-content">
          <div class="msg-meta"><span>${role === 'user' ? 'Tú' : 'Itiers Copilot'}</span></div>
          <p>${text.replace(/\\n/g, '<br/>')}</p>
        </div>
      `;
      chat.appendChild(div);
      if (scrollToBottom) chat.scrollTop = chat.scrollHeight;
    }

    function autoResizeTextarea(el) {
      el.style.height = 'auto'; // Resetea temporalmente la altura para medir el contenido real
      el.style.height = (el.scrollHeight) + 'px'; // Ajusta la altura al contenido
    }

    function handleKey(e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }

    loadChats();
    checkDevStatus();
    setInterval(checkDevStatus, 4000);

    function toggleTheme() {
      const current = document.documentElement.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('itiers_theme', next);
    }

    (function() {
      const saved = localStorage.getItem('itiers_theme') || 'dark';
      document.documentElement.setAttribute('data-theme', saved);
    })();
  </script>
</body>
</html>
"""

class CopilotHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ["/", "/index.html"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif path == "/api/chats":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(chats_db).encode("utf-8"))
        elif path == "/api/dev_status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            running = is_port_3000_open()
            self.wfile.write(json.dumps({"running": running, "url": f"http://localhost:{DEV_PORT}"}).encode("utf-8"))
        elif path == "/api/fs/tree":
            ignore_dirs = {".git", "node_modules", ".next", "__pycache__", "out", "build", ".harness_backups", ".copilot_profile", "dist", ".vscode"}
            ignore_ext = {".ico", ".png", ".jpg", ".jpeg", ".svg", ".lock", ".log"}
            
            def build_tree(dir_path):
                tree = []
                try:
                    for entry in sorted(os.scandir(dir_path), key=lambda e: (not e.is_dir(), e.name.lower())):
                        name = entry.name
                        if name in ignore_dirs or name.startswith('.'): 
                            continue
                        rel_path = os.path.relpath(entry.path, os.getcwd()).replace("\\", "/")
                        if entry.is_dir():
                            children = build_tree(entry.path)
                            if children: 
                                tree.append({"name": name, "type": "folder", "path": rel_path, "children": children})
                        else:
                            if os.path.splitext(name)[1].lower() not in ignore_ext:
                                tree.append({"name": name, "type": "file", "path": rel_path})
                except Exception:
                    pass
                return tree
            
            tree_data = build_tree(os.getcwd())
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"tree": tree_data}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
        data = json.loads(body) if body else {}

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()

        response = {}
        global chats_db

        if self.path == "/api/chats/new":
            new_id = str(int(time.time()))
            chats_db["active_id"] = new_id
            chats_db["chats"][new_id] = {"title": f"Chat {time.strftime('%H:%M:%S')}", "messages": [{"role": "assistant", "text": "¡Nuevo chat listo!"}]}
            save_chats_db(chats_db)
            response = chats_db
        elif self.path == "/api/chats/switch":
            tid = data.get("chat_id")
            if tid in chats_db["chats"]:
                chats_db["active_id"] = tid
                save_chats_db(chats_db)
            response = chats_db
        elif self.path == "/api/chats/delete":
            tid = data.get("chat_id")
            if tid in chats_db["chats"] and len(chats_db["chats"]) > 1:
                del chats_db["chats"][tid]
                if chats_db["active_id"] == tid: chats_db["active_id"] = list(chats_db["chats"].keys())[-1]
                save_chats_db(chats_db)
            response = chats_db
        elif self.path == "/api/chat":
            msg = data.get("message", "")
            target = data.get("target_file")
            edit_mode = data.get("edit_mode", False)

            aid = chats_db["active_id"]
            if aid not in chats_db["chats"]:
                aid = str(int(time.time()))
                chats_db["active_id"] = aid
                chats_db["chats"][aid] = {"title": "Chat Principal", "messages": []}

            current = chats_db["chats"][aid]
            if len(current["messages"]) <= 1: current["title"] = msg[:28]
            current["messages"].append({"role": "user", "text": msg})

            reply, _, _ = agent.process_chat(msg, selected_file=target, edit_mode=edit_mode)
            current["messages"].append({"role": "assistant", "text": reply})
            save_chats_db(chats_db)
            response = {"reply": reply, "db": chats_db}
        elif self.path == "/api/set_key":
            prov = data.get("provider", "gemini")
            agent.set_api_key(prov, "")
            response = {"success": True, "message": f"⚙️ Proveedor activo cambiado a {prov.upper()} usando `.env.local`."}
        elif self.path == "/api/dev_start":
            ok, msg = start_dev_server()
            response = {"success": ok, "message": msg, "running": is_port_3000_open()}

        self.wfile.write(json.dumps(response).encode("utf-8"))

def launch_desktop_window():
    url = f"http://{HOST}:{PORT}"
    time.sleep(0.8)
    browser_paths = [
        shutil.which("msedge"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        shutil.which("chrome"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    ]
    temp_dir = os.environ.get("TEMP", os.path.expanduser("~"))
    profile_dir = os.path.join(temp_dir, "itiers_copilot_profile")
    for p in browser_paths:
        if p and os.path.exists(p):
            try:
                subprocess.Popen([p, f"--app={url}", f"--user-data-dir={profile_dir}", "--disable-gpu", "--window-size=1280,850"])
                return
            except Exception:
                pass
    import webbrowser
    webbrowser.open(url)

def main():
    server = HTTPServer((HOST, PORT), CopilotHandler)
    print(f">> [Itiers Copilot] Servidor activo en http://{HOST}:{PORT}")
    threading.Thread(target=launch_desktop_window, daemon=True).start()
    server.serve_forever()

if __name__ == "__main__":
    main()