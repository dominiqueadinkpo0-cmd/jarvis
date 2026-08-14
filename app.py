import os
import subprocess
import json
import random
import urllib.request
import urllib.parse
from flask import Flask, jsonify, render_template_string, request, send_from_directory
from bs4 import BeautifulSoup

app = Flask(__name__, static_folder='.', static_url_path='')

APP_NAME = "StarkAI Nexus"
AGENTS = {
    "architecte": {"nom": "Nexus - Architecte", "role": "Architecture quantique & stratégie.", "avatar": "🏛️"},
    "developpeur": {"nom": "Nexus - Développeur Full-Stack", "role": "Code & holographie.", "avatar": "💻"},
    "securite": {"nom": "Nexus - Sécurité & Défense", "role": "Contrôle absolu & boucliers.", "avatar": "🛡️"},
    "createur": {"nom": "Nexus - Créateur & UX", "role": "Interface & esthétique.", "avatar": "✨"}
}

API_KEY_GOOGLE = os.environ.get("GOOGLE_API_KEY", "")
DEFAULT_MODEL = "gemini-1.5-flash"
CONTROLE_MODE = "total"

CONNECTED_DEVICES = [
    {"id": "pc-main", "nom": "Station de Travail Principale (PC)", "type": "Ordinateur", "statut": "Hologramme Actif", "ip": "192.168.1.10"},
    {"id": "mobile-1", "nom": "Smartphone / Armure Tactile", "type": "Mobile", "statut": "Synchronisé", "ip": "192.168.1.25"},
    {"id": "iot-hub", "nom": "Passerelle Domotique & Manoir Stark", "type": "IoT Smart Home", "statut": "Contrôle Absolu", "ip": "192.168.1.50"},
    {"id": "server-vps", "nom": "Noyau Quantique Cloud", "type": "Cloud Server", "statut": "Opérationnel", "ip": "10.8.0.1"}
]

def appeler_gemini(prompt, system_instruction=""):
    global API_KEY_GOOGLE
    if not API_KEY_GOOGLE:
        return f"Noyau quantique opérationnel. (Ordre reçu en mode local : {prompt})"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{DEFAULT_MODEL}:generateContent?key={API_KEY_GOOGLE}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]} if system_instruction else None
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            candidates = res_data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "Pas de réponse générée.")
    except Exception as e:
        return f"Erreur Google Gemini : {str(e)}"
    return "Réponse vide."

@app.route("/")
def index():
    html_template = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>StarkAI Nexus - Interface Holographique Quantique</title>
        <link rel="manifest" href="/manifest.json">
        <meta name="theme-color" content="#00f0ff">
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Inter:wght@300;400;500;600&display=swap');
            
            body {
                font-family: 'Inter', sans-serif;
                background-color: #f5f5f7;
                color: #1d1d1f;
                transition: all 0.5s ease;
            }

            /* Thème Holographique Quantique */
            body.holo-theme {
                font-family: 'Share Tech Mono', monospace;
                background-color: #030712;
                color: #00f0ff;
            }

            .apple-card {
                background: rgba(255, 255, 255, 0.9);
                backdrop-filter: blur(25px);
                border: 1px solid rgba(0, 0, 0, 0.08);
                box-shadow: 0 12px 35px rgba(0, 0, 0, 0.05);
                border-radius: 1.5rem;
                transition: all 0.5s ease;
            }

            body.holo-theme .apple-card {
                background: rgba(3, 7, 18, 0.85);
                border: 1px solid rgba(0, 240, 255, 0.4);
                box-shadow: 0 0 25px rgba(0, 240, 255, 0.2);
                color: #00f0ff;
            }

            .chat-bubble-user {
                background: #0071e3;
                color: white;
                border-radius: 1.25rem 1.25rem 0.25rem 1.25rem;
            }
            body.holo-theme .chat-bubble-user {
                background: #0044ff;
                color: #ffffff;
                border: 1px solid #00f0ff;
            }

            .chat-bubble-nexus {
                background: #f0f0f2;
                color: #1d1d1f;
                border-radius: 1.25rem 1.25rem 1.25rem 0.25rem;
            }
            body.holo-theme .chat-bubble-nexus {
                background: rgba(0, 240, 255, 0.08);
                color: #00f0ff;
                border: 1px solid rgba(0, 240, 255, 0.3);
            }

            .holo-glow {
                box-shadow: 0 0 30px rgba(0, 240, 255, 0.5);
                animation: pulse-holo 2s infinite ease-in-out;
            }
            @keyframes pulse-holo {
                0% { box-shadow: 0 0 15px rgba(0, 240, 255, 0.3); }
                50% { box-shadow: 0 0 40px rgba(0, 240, 255, 0.8); }
                100% { box-shadow: 0 0 15px rgba(0, 240, 255, 0.3); }
            }
        </style>
    </head>
    <body id="main-body" class="min-h-screen flex flex-col justify-between p-4 md:p-8 max-w-7xl mx-auto">
        <!-- Header -->
        <header class="flex flex-col md:flex-row justify-between items-center apple-card px-6 py-4 mb-6 gap-4">
            <div class="flex items-center space-x-3">
                <div class="w-3.5 h-3.5 bg-blue-600 rounded-full animate-pulse" id="status-dot"></div>
                <h1 class="text-xl font-bold tracking-tight">StarkAI Nexus <span class="text-xs font-normal px-2.5 py-1 rounded-full bg-blue-50 text-blue-600" id="badge-theme">Holographique Quantique</span></h1>
            </div>
            <div class="flex items-center space-x-3">
                <button onclick="toggleHolographicMode()" id="holo-btn" class="bg-cyan-600 hover:bg-cyan-700 text-white px-3.5 py-1.5 rounded-xl text-xs font-medium transition holo-glow">🌀 Mode Hologramme : ON</button>
                <button onclick="toggleLiveVideo()" id="live-video-btn" class="bg-purple-600 hover:bg-purple-700 text-white px-3.5 py-1.5 rounded-xl text-xs font-medium transition">🔴 Live Vidéo : OFF</button>
            </div>
        </header>

        <!-- Main Workspace -->
        <main class="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-grow mb-6">
            <!-- Sidebar: Devices & Absolute Control -->
            <div class="space-y-6">
                <div class="apple-card p-5">
                    <h2 class="text-xs font-semibold uppercase tracking-wider opacity-60 mb-3">Contrôle Absolu & Appareils</h2>
                    <div id="devices-list" class="space-y-2.5 mb-4"></div>
                    <button onclick="absoluteTakeover()" class="w-full py-2.5 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600 text-white rounded-xl text-xs font-medium transition shadow-sm">⚡ Activer le Contrôle Absolu</button>
                </div>

                <div id="video-preview-box" class="apple-card p-4 hidden">
                    <h3 class="text-xs font-semibold opacity-60 mb-2 flex justify-between"><span>Flux Holographique Live</span><span class="text-cyan-400 animate-pulse">● QUANTIQUE</span></h3>
                    <div class="bg-black rounded-xl overflow-hidden h-40 flex items-center justify-center relative border border-cyan-500/40">
                        <video id="webcam" autoplay playsinline class="w-full h-full object-cover"></video>
                    </div>
                </div>
            </div>

            <!-- Central Area: Chat & Terminal -->
            <div class="lg:col-span-3 apple-card p-6 flex flex-col justify-between h-[680px]">
                <div id="chat-container" class="flex-grow overflow-y-auto space-y-4 pr-2 mb-4 font-normal text-sm">
                    <div class="flex items-start space-x-3">
                        <div class="w-8 h-8 rounded-full bg-cyan-500 text-black flex items-center justify-center font-bold text-xs">S</div>
                        <div class="chat-bubble-nexus p-4 max-w-xl">
                            Interface holographique quantique initialisée. J'ai le contrôle absolu sur l'ensemble de votre réseau et de vos appareils, Monsieur. Que devons-nous projeter ou accomplir ?
                        </div>
                    </div>
                </div>

                <div class="space-y-3 pt-3 border-t border-gray-200/20">
                    <div class="flex space-x-2">
                        <input type="text" id="user-input" onkeypress="handleKey(event)" placeholder="Donnez un ordre en contrôle absolu..." class="w-full bg-black/5 border border-cyan-500/30 px-4 py-3 text-sm rounded-2xl focus:outline-none focus:border-cyan-400 transition shadow-inner">
                        <button onclick="sendMessage()" class="bg-cyan-600 hover:bg-cyan-700 text-white px-6 py-3 rounded-2xl text-sm font-medium transition shadow-sm">Projeter</button>
                    </div>
                    <div class="flex justify-between items-center text-xs opacity-60 px-1">
                        <span>Noyau : Contrôle Total & Holographie</span>
                        <button onclick="runTerminalCommand('uptime')" class="hover:text-cyan-400">Terminal Quantique</button>
                    </div>
                </div>
            </div>
        </main>

        <script>
            let holoMode = true;
            function toggleHolographicMode() {
                holoMode = !holoMode;
                const body = document.getElementById('main-body');
                const btn = document.getElementById('holo-btn');
                const badge = document.getElementById('badge-theme');
                if (holoMode) {
                    body.classList.add('holo-theme');
                    btn.innerText = "🌀 Mode Hologramme : ON";
                    badge.innerText = "Holographique Quantique";
                } else {
                    body.classList.remove('holo-theme');
                    btn.innerText = "🌀 Mode Hologramme : OFF";
                    badge.innerText = "Apple Blanc Premium";
                }
            }
            toggleHolographicMode(); // Activer par defaut

            function loadDevices() {
                fetch('/api/devices')
                .then(res => res.json())
                .then(data => {
                    const list = document.getElementById('devices-list');
                    list.innerHTML = '';
                    data.devices.forEach(d => {
                        const div = document.createElement('div');
                        div.className = 'p-3 rounded-xl border border-cyan-500/30 bg-black/10 flex justify-between items-center text-xs';
                        div.innerHTML = `<div><div class="font-semibold">${d.nom}</div><div class="text-[10px] opacity-60">${d.ip}</div></div><span class="text-cyan-400 font-medium">Connecté</span>`;
                        list.appendChild(div);
                    });
                });
            }
            loadDevices();

            function absoluteTakeover() {
                fetch('/api/absolute-takeover', {method: 'POST'})
                .then(res => res.json())
                .then(data => {
                    appendMessage('StarkAI Nexus', data.message, false);
                });
            }

            let liveVideoActive = false;
            let mediaStream = null;
            function toggleLiveVideo() {
                liveVideoActive = !liveVideoActive;
                const btn = document.getElementById('live-video-btn');
                const box = document.getElementById('video-preview-box');
                const video = document.getElementById('webcam');
                if (liveVideoActive) {
                    btn.innerText = "🔴 Live Vidéo : ON";
                    box.classList.remove('hidden');
                    navigator.mediaDevices.getUserMedia({ video: true, audio: false })
                        .then(stream => { mediaStream = stream; video.srcObject = stream; });
                } else {
                    btn.innerText = "🔴 Live Vidéo : OFF";
                    box.classList.add('hidden');
                    if (mediaStream) mediaStream.getTracks().forEach(t => t.stop());
                }
            }

            function appendMessage(sender, text, isUser = false) {
                const container = document.getElementById('chat-container');
                const div = document.createElement('div');
                div.className = `flex items-start space-x-3 ${isUser ? 'justify-end' : ''}`;
                div.innerHTML = isUser ? `
                    <div class="chat-bubble-user p-4 max-w-xl shadow-sm">${text}</div>
                    <div class="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs">U</div>
                ` : `
                    <div class="w-8 h-8 rounded-full bg-cyan-500 text-black flex items-center justify-center font-bold text-xs">S</div>
                    <div class="chat-bubble-nexus p-4 max-w-xl shadow-sm">${text}</div>
                `;
                container.appendChild(div);
                container.scrollTop = container.scrollHeight;
            }

            function sendMessage() {
                const input = document.getElementById('user-input');
                const text = input.value.trim();
                if (!text) return;
                appendMessage('Utilisateur', text, true);
                input.value = '';
                fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                })
                .then(res => res.json())
                .then(data => { appendMessage('StarkAI Nexus', data.response, false); });
            }

            function handleKey(e) { if (e.key === 'Enter') sendMessage(); }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route("/manifest.json")
def manifest():
    return send_from_directory('.', 'manifest.json')

@app.route("/sw.js")
def sw():
    return send_from_directory('.', 'sw.js')

@app.route("/api/devices")
def api_devices():
    return jsonify({"status": "success", "devices": CONNECTED_DEVICES})

@app.route("/api/absolute-takeover", methods=["POST"])
def api_absolute_takeover():
    return jsonify({"status": "success", "message": "⚡ Contrôle absolu activé sur tous les nœuds du réseau. Projections holographiques synchronisées, Monsieur."})

@app.route("/api/chat", methods=["POST"])
def api_chat():
    global API_KEY_GOOGLE
    data = request.get_json() or {}
    msg = data.get("message", "")
    system_prompt = "Tu es StarkAI Nexus, doté d'une interface holographique quantique et d'un contrôle absolu sur tous les appareils connectés."
    resp = appeler_gemini(msg, system_instruction=system_prompt)
    return jsonify({"status": "success", "response": resp})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
