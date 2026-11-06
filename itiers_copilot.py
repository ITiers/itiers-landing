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
import glob
import time
import shutil
import socket
import urllib.parse
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

if sys.platform == "win32":
    try:
        if sys.stdout:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
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
                "messages": [
                    {
                        "role": "assistant",
                        "text": "¡Hola! Selecciona un archivo en la barra lateral para comenzar. Puedo agregar imágenes, carruseles, formularios, modificar colores, tipografías y lo que necesites en el código."
                    }
                ]
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

def stop_dev_server():
    global dev_process
    if dev_process:
        try:
            subprocess.run(f"taskkill /F /T /PID {dev_process.pid}", shell=True, capture_output=True)
        except Exception:
            pass
        dev_process = None
    return True, "Servidor local detenido."

HTML_PAGE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Itiers AI Copilot — Suite de Harness & QA</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }
    body { background-color: #0A0A0A; color: #E5E7EB; height: 100vh; display: flex; overflow: hidden; }
    
    sidebar { width: 320px; background-color: #121212; border-right: 1px solid #2A2A2A; display: flex; flex-direction: column; justify-content: space-between; flex-shrink: 0; z-index: 20; }
    main { flex: 1; display: flex; flex-direction: column; height: 100%; background-color: #0A0A0A; position: relative; }
    
    .brand-header { padding: 16px; border-bottom: 1px solid #2A2A2A; display: flex; align-items: center; justify-content: space-between; }
    .brand-left { display: flex; align-items: center; gap: 12px; }
    .brand-logo { width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, #ff4f00, #b33600); display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; font-size: 14px; box-shadow: 0 4px 12px rgba(255,79,0,0.3); }
    .brand-title { font-size: 14px; font-weight: 700; color: white; display: flex; align-items: center; gap: 6px; }
    .brand-tag { font-size: 10px; padding: 2px 6px; border-radius: 10px; background: rgba(255,79,0,0.2); color: #ff4f00; border: 1px solid rgba(255,79,0,0.3); font-weight: 600; }
    
    .new-chat-btn { background: #ff4f00; border: none; border-radius: 8px; width: 32px; height: 32px; color: white; font-size: 16px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background 0.2s; }
    .new-chat-btn:hover { background: #e04500; }

    .widget-box { padding: 16px; display: flex; flex-direction: column; gap: 16px; }
    .widget-label { font-size: 11px; font-weight: 600; text-transform: uppercase; color: #9CA3AF; display: block; margin-bottom: 6px; }
    
    .target-btn { width: 100%; background: #181818; border: 1px solid #2A2A2A; border-radius: 12px; padding: 10px 12px; font-size: 12px; color: #E5E7EB; text-align: left; display: flex; justify-content: space-between; align-items: center; cursor: pointer; transition: all 0.2s; }
    .target-btn:hover { border-color: #ff4f00; }
    
    .mode-toggle-btn { width: 100%; padding: 12px; border-radius: 12px; border: 1px solid #2A2A2A; background: #181818; display: flex; align-items: center; justify-content: space-between; cursor: pointer; transition: all 0.2s; }
    .mode-toggle-btn.active { border-color: #ff4f00; background: rgba(255,79,0,0.1); }
    
    .toggle-switch { width: 36px; height: 20px; border-radius: 20px; background: #374151; padding: 2px; transition: background 0.2s; display: flex; align-items: center; }
    .toggle-switch.active { background: #ff4f00; }
    .toggle-knob { width: 16px; height: 16px; border-radius: 50%; background: #9CA3AF; transition: transform 0.2s; }
    .toggle-switch.active .toggle-knob { transform: translateX(16px); background: white; }

    .chats-list-container { flex: 1; overflow-y: auto; padding: 0 16px; display: flex; flex-direction: column; gap: 4px; border-top: 1px solid #2A2A2A; margin-top: 8px; padding-top: 12px; }
    
    .chat-history-row { display: flex; align-items: center; justify-content: space-between; border-radius: 8px; transition: background 0.2s; }
    .chat-history-row:hover { background: #1A1A1A; }
    .chat-history-row.active { background: rgba(255,79,0,0.15); border: 1px solid rgba(255,79,0,0.3); }

    .chat-history-item { flex: 1; font-size: 12px; padding: 8px 10px; color: #9CA3AF; cursor: pointer; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .chat-history-row.active .chat-history-item { color: #ff7333; font-weight: 600; }
    
    .delete-chat-btn { background: none; border: none; color: #6B7280; font-size: 13px; padding: 4px 8px; cursor: pointer; transition: color 0.2s; }
    .delete-chat-btn:hover { color: #EF4444; }

    .sidebar-footer { padding: 16px; border-top: 1px solid #2A2A2A; background: #0E0E0E; display: flex; flex-direction: column; gap: 12px; }
    .model-status { display: flex; align-items: center; gap: 8px; }
    .status-dot { width: 8px; height: 8px; border-radius: 50%; background: #10B981; box-shadow: 0 0 8px #10B981; }
    
    .btn-secondary { width: 100%; padding: 8px 12px; border-radius: 8px; background: rgba(255,79,0,0.1); border: 1px solid rgba(255,79,0,0.3); color: #ff7333; font-size: 12px; font-weight: 600; cursor: pointer; text-align: center; transition: all 0.2s; }
    .btn-secondary:hover { background: rgba(255,79,0,0.2); }
    
    .top-bar { height: 56px; border-bottom: 1px solid #2A2A2A; display: flex; align-items: center; justify-content: space-between; padding: 0 24px; background: rgba(14,14,14,0.8); }
    .chat-area { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 20px; max-width: 860px; width: 100%; margin: 0 auto; }
    
    .msg-card { display: flex; gap: 16px; padding: 20px; border-radius: 16px; border: 1px solid #2A2A2A; background: #141414; }
    .msg-card.user { background: #181818; margin-left: 48px; }
    .msg-card.assistant { background: #121212; margin-right: 48px; }
    .msg-avatar { width: 32px; height: 32px; border-radius: 8px; background: #ff4f00; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; font-size: 12px; flex-shrink: 0; }
    .msg-avatar.user-av { background: #4B5563; }
    .msg-content { flex: 1; font-size: 14px; line-height: 1.6; color: #D1D5DB; }
    .msg-meta { font-size: 11px; font-weight: 600; color: #ff7333; margin-bottom: 4px; display: flex; justify-content: space-between; }
    
    .input-container { padding: 16px; border-top: 1px solid #2A2A2A; background: #0E0E0E; max-width: 860px; width: 100%; margin: 0 auto; }
    .input-wrapper { position: relative; display: flex; align-items: center; }
    .chat-textarea { width: 100%; background: #181818; border: 1px solid #2A2A2A; border-radius: 16px; padding: 14px 50px 14px 16px; font-size: 14px; color: white; resize: none; outline: none; transition: border-color 0.2s; }
    .chat-textarea:focus { border-color: #ff4f00; }
    .send-btn { position: absolute; right: 10px; width: 36px; height: 36px; border-radius: 10px; background: #ff4f00; border: none; color: white; font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background 0.2s; }
    .send-btn:hover { background: #e04500; }
    
    .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); backdrop-filter: blur(4px); z-index: 50; display: flex; align-items: center; justify-content: center; padding: 16px; }
    .modal-box { background: #141414; border: 1px solid #2A2A2A; border-radius: 16px; max-width: 440px; width: 100%; padding: 24px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5); display: flex; flex-direction: column; gap: 16px; }
    .modal-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #2A2A2A; padding-bottom: 12px; font-weight: bold; font-size: 14px; color: white; }
    .close-btn { background: none; border: none; color: #9CA3AF; font-size: 18px; cursor: pointer; }
    .close-btn:hover { color: white; }
    
    .form-select, .form-input { width: 100%; background: #1C1C1C; border: 1px solid #2A2A2A; border-radius: 10px; padding: 10px; font-size: 13px; color: white; outline: none; margin-top: 6px; }
    .btn-primary { width: 100%; padding: 10px; border-radius: 10px; background: #ff4f00; border: none; color: white; font-size: 13px; font-weight: bold; cursor: pointer; }
    .btn-primary:hover { background: #e04500; }
    
    .slide-panel { position: fixed; top: 0; bottom: 0; right: 0; width: 440px; background: #0A0A0A; border-left: 1px solid #2A2A2A; z-index: 50; transform: translateX(100%); transition: transform 0.3s ease; display: flex; flex-direction: column; box-shadow: -10px 0 25px rgba(0,0,0,0.5); }
    .slide-panel.open { transform: translateX(0); }
    .tree-container { flex: 1; overflow-y: auto; padding: 16px; background: #0E0E0E; }
    .tree-item { font-size: 12px; padding: 8px 12px; border-radius: 6px; color: #D1D5DB; cursor: pointer; display: flex; align-items: center; gap: 8px; margin-bottom: 2px; }
    .tree-item:hover { background: #1E1E1E; color: white; }
    .tree-item.file { color: #60A5FA; font-family: monospace; }
    .tree-item.folder { color: #F59E0B; font-weight: 600; }
    
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
            <span id="targetDisplay" style="font-family: monospace; color: #ff7333;">Ninguno seleccionado</span>
            <span>📁</span>
          </button>
        </div>

        <div>
          <button type="button" id="sidebarEditToggle" onclick="toggleEditMode()" class="mode-toggle-btn">
            <div style="display: flex; align-items: center; gap: 10px;">
              <span id="sidebarEditIcon" style="font-size: 16px;">💬</span>
              <div style="text-align: left;">
                <div id="sidebarEditTitle" style="font-size: 12px; font-weight: bold; color: #E5E7EB;">Modo Consulta</div>
                <div id="sidebarEditSub" style="font-size: 10px; color: #9CA3AF;">Sólo lectura y análisis</div>
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
          <div id="modelBadge" style="font-size: 12px; font-weight: 600; color: white;">Gemini / Ollama</div>
          <div id="statusSubtext" style="font-size: 10px; color: #9CA3AF;">Modelo Activo</div>
        </div>
      </div>
      <button onclick="openKeySelectorModal()" class="btn-secondary">
        🔑 Seleccionar Modelo / API Key
      </button>
    </div>
  </sidebar>

  <main>
    <header class="top-bar">
      <span style="font-size: 13px; font-weight: 500; color: #D1D5DB;">Itiers AI Copilot — Libertad Total de Edición y Diseño</span>
      <button id="webBtn" onclick="handleWebClick()" style="padding: 6px 12px; border-radius: 8px; background: #1E1E1E; border: 1px solid #2A2A2A; color: white; font-size: 12px; cursor: pointer; display: flex; align-items: center; gap: 6px;">
        <span id="webDot" style="width: 8px; height: 8px; border-radius: 50%; background: #6B7280; display: inline-block;"></span>
        <span id="webText">🌐 Iniciar y Abrir Web (localhost:3000)</span>
      </button>
    </header>

    <div id="chatContainer" class="chat-area"></div>

    <div class="input-container">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <span id="chatEditLabel" style="font-size: 11px; font-weight: bold; color: #9CA3AF;">💬 Modo Consulta (Lectura)</span>
        <span id="targetInputBadge" style="font-family: monospace; font-size: 11px; color: #ff7333;">Ningún archivo seleccionado</span>
      </div>

      <form onsubmit="sendMessage(event)" class="input-wrapper">
        <textarea id="messageInput" rows="1" placeholder="Escribe tu solicitud de diseño, cambios o consultas..." onkeydown="handleKey(event)" class="chat-textarea"></textarea>
        <button type="submit" id="sendBtn" class="send-btn">➔</button>
      </form>
    </div>
  </main>

  <!-- MODAL SELECCIÓN MODELOS / API KEYS -->
  <div id="keySelectorModal" class="modal-overlay hidden">
    <div class="modal-box">
      <div class="modal-header">
        <span>🔑 Seleccionar Proveedor y Modelo de IA</span>
        <button onclick="closeKeySelectorModal()" class="close-btn">&times;</button>
      </div>
      <div>
        <label class="widget-label">Elige el Proveedor:</label>
        <select id="modelProviderSelect" onchange="onProviderChange()" class="form-select">
          <option value="gemini">Google Gemini API (Recomendado)</option>
          <option value="groq">Groq API (Ultra rápido)</option>
          <option value="openai">OpenAI GPT-4o</option>
          <option value="openrouter">OpenRouter</option>
          <option value="ollama">Ollama Local (100% Privado / Sin Internet)</option>
        </select>
        <div id="apiKeyFieldContainer" style="margin-top: 10px;">
          <label class="widget-label">API Key del Proveedor:</label>
          <input type="password" id="modalApiKeyInput" placeholder="Pega tu clave API aquí..." class="form-input">
        </div>
      </div>
      <div style="display: flex; gap: 8px; margin-top: 8px;">
        <button onclick="saveApiKeyModal()" class="btn-primary">Guardar y Conectar</button>
      </div>
    </div>
  </div>

  <!-- Explorador de Archivos Slide Panel -->
  <div id="fileExplorerOverlay" onclick="closeFileExplorer()" class="modal-overlay hidden" style="background: rgba(0,0,0,0.5);"></div>
  <div id="fileExplorerPanel" class="slide-panel">
    <div class="modal-header" style="padding: 16px; background: #121212;">
      <span>📁 Seleccionar Archivo Objetivo (Código)</span>
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
        delBtn.onclick = (e) => {
          e.stopPropagation();
          deleteChat(id);
        };
        
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
      if (!confirm("¿Estás seguro de que deseas eliminar este chat?")) return;
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
        alert("⚠️ Por favor selecciona primero un archivo en la barra lateral antes de activar el Modo Edición.");
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
        if (sideSub) { sideSub.innerText = "Modifica código directamente"; sideSub.style.color = "#ff7333"; }
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

    function onProviderChange() {
      const prov = document.getElementById('modelProviderSelect').value;
      document.getElementById('apiKeyFieldContainer').style.display = prov === 'ollama' ? 'none' : 'block';
    }

    async function saveApiKeyModal() {
      const prov = document.getElementById('modelProviderSelect').value;
      const key = document.getElementById('modalApiKeyInput').value.trim();
      if (prov !== 'ollama' && !key) { alert("Ingresa una clave válida."); return; }

      const res = await fetch('/api/set_key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: prov, key: key })
      });
      const data = await res.json();
      alert(data.message);
      closeKeySelectorModal();
    }

    function openFileExplorer() {
      document.getElementById('fileExplorerOverlay').classList.remove('hidden');
      document.getElementById('fileExplorerPanel').classList.add('open');
      const container = document.getElementById('fileTreeContainer');
      container.innerHTML = '<div style="color: #9CA3AF; padding: 10px;">Escaneando archivos del proyecto...</div>';
      
      fetch('/api/fs/tree').then(res => res.json()).then(data => {
        container.innerHTML = '';
        buildFlatFileList(data.tree, container);
      }).catch(err => {
        container.innerHTML = '<div style="color: red; padding: 10px;">Error cargando archivos.</div>';
      });
    }

    function closeFileExplorer() {
      document.getElementById('fileExplorerOverlay').classList.add('hidden');
      document.getElementById('fileExplorerPanel').classList.remove('open');
    }

    function buildFlatFileList(nodes, container) {
      nodes.forEach(node => {
        if (node.type === 'file') {
          const item = document.createElement('div');
          item.className = "tree-item file";
          item.innerHTML = `<span>📄</span><span>${node.path}</span>`;
          item.onclick = (e) => {
            e.stopPropagation();
            globalSelectedTarget = node.path;
            document.getElementById('targetDisplay').innerText = globalSelectedTarget;
            document.getElementById('targetInputBadge').innerText = globalSelectedTarget;
            closeFileExplorer();
          };
          container.appendChild(item);
        } else if (node.type === 'folder' && node.children && node.children.length > 0) {
          const header = document.createElement('div');
          header.className = "tree-item folder";
          header.innerHTML = `<span>📁</span><span>${node.name}/</span>`;
          container.appendChild(header);
          
          const subContainer = document.createElement('div');
          subContainer.style.paddingLeft = '14px';
          container.appendChild(subContainer);
          buildFlatFileList(node.children, subContainer);
        }
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
      if (isServerRunning) {
        window.open('http://localhost:3000', '_blank');
        return;
      }

      if (isStartingServer) return;
      isStartingServer = true;

      const text = document.getElementById('webText');
      const dot = document.getElementById('webDot');
      if (text) text.innerText = "Iniciando Next.js (npm run dev)...";
      if (dot) { dot.style.background = "#F59E0B"; dot.style.boxShadow = "0 0 8px #F59E0B"; }

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
          alert('Aviso del servidor: ' + data.message);
        }
      } catch (e) {
        isStartingServer = false;
        updateDevUi(false);
        alert('Error al levantar servidor: ' + e);
      }
    }

    async function sendMessage(e) {
      if (e) e.preventDefault();
      const input = document.getElementById('messageInput');
      const text = input.value.trim();
      if (!text) return;

      if (isEditModeActive && !globalSelectedTarget) {
        alert("⚠️ Debes seleccionar un archivo objetivo antes de aplicar cambios en Modo Edición.");
        openFileExplorer();
        return;
      }

      appendMessageUI('user', text, true);
      input.value = '';

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
      if (scrollToBottom) {
        chat.scrollTop = chat.scrollHeight;
      }
    }

    function handleKey(e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }

    loadChats();
    checkDevStatus();
    setInterval(checkDevStatus, 4000);
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
            ignore_dirs = {
                ".git", "node_modules", ".next", "__pycache__", "out", 
                "build", ".harness_backups", ".copilot_profile", "dist", ".vscode"
            }
            ignore_extensions = {".ico", ".png", ".jpg", ".jpeg", ".svg", ".lock", ".log"}

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
                            ext = os.path.splitext(name)[1].lower()
                            if ext not in ignore_extensions:
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
            chats_db["chats"][new_id] = {
                "title": f"Chat {time.strftime('%H:%M:%S')}",
                "messages": [
                    {
                        "role": "assistant",
                        "text": "¡Nuevo chat iniciado! Selecciona un archivo en la barra lateral para continuar."
                    }
                ]
            }
            save_chats_db(chats_db)
            response = chats_db

        elif self.path == "/api/chats/switch":
            target_id = data.get("chat_id")
            if target_id in chats_db["chats"]:
                chats_db["active_id"] = target_id
                save_chats_db(chats_db)
            response = chats_db

        elif self.path == "/api/chats/delete":
            target_id = data.get("chat_id")
            if target_id in chats_db["chats"] and len(chats_db["chats"]) > 1:
                del chats_db["chats"][target_id]
                # Si borramos el activo, cambiamos al primero que quede disponible
                if chats_db["active_id"] == target_id:
                    chats_db["active_id"] = list(chats_db["chats"].keys())[-1]
                save_chats_db(chats_db)
            response = chats_db

        elif self.path == "/api/chat":
            msg = data.get("message", "")
            target = data.get("target_file")
            edit_mode = data.get("edit_mode", False)

            active_id = chats_db["active_id"]
            if active_id not in chats_db["chats"]:
                active_id = str(int(time.time()))
                chats_db["active_id"] = active_id
                chats_db["chats"][active_id] = {"title": "Chat Principal", "messages": []}

            current_chat = chats_db["chats"][active_id]
            if len(current_chat["messages"]) <= 1:
                current_chat["title"] = msg[:28] + ("..." if len(msg) > 28 else "")

            current_chat["messages"].append({"role": "user", "text": msg})
            reply, _, _ = agent.process_chat(msg, selected_file=target, edit_mode=edit_mode)
            current_chat["messages"].append({"role": "assistant", "text": reply})
            save_chats_db(chats_db)

            response = {"reply": reply, "db": chats_db}

        elif self.path == "/api/set_key":
            prov = data.get("provider", "gemini")
            kval = data.get("key", "")
            agent.set_api_key(prov, kval)
            response = {"success": True, "message": f"✅ Proveedor {prov.upper()} configurado con éxito."}
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
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]

    temp_dir = os.environ.get("TEMP", os.path.expanduser("~"))
    profile_dir = os.path.join(temp_dir, "itiers_copilot_profile")

    for p in browser_paths:
        if p and os.path.exists(p):
            try:
                subprocess.Popen([
                    p, 
                    f"--app={url}", 
                    f"--user-data-dir={profile_dir}", 
                    "--disable-gpu", 
                    "--window-size=1280,850"
                ])
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