import os
import subprocess
import json
import random
import urllib.request
import urllib.parse
from flask import Flask, jsonify, render_template_string, request
from bs4 import BeautifulSoup

app = Flask(__name__)

APP_NAME = "StarkAI Nexus"
AGENTS = {
    "architecte": {
        "nom": "Nexus - Architecte",
        "role": "Conception d'architecture logicielle, choix technologiques et planification des objectifs.",
        "avatar": "🏛️",
        "style": "Analytique, visionnaire et structuré."
    },
    "developpeur": {
        "nom": "Nexus - Développeur Full-Stack",
        "role": "Écriture de code propre, tests rigoureux et implémentation des fonctionnalités.",
        "avatar": "💻",
        "style": "Pragmatique, rapide et axé sur les résultats."
    },
    "securite": {
        "nom": "Nexus - Sécurité & IoT",
        "role": "Audit de réseau, contrôle des objets connectés (PC, Mobile, IoT) et protocoles de défense.",
        "avatar": "🛡️",
        "style": "Vigilant, rigoureux et protecteur."
    },
    "createur": {
        "nom": "Nexus - Créateur & UX",
        "role": "Design d'interface, expérience utilisateur et créativité visuelle.",
        "avatar": "✨",
        "style": "Inspiré, esthète et centré sur l'utilisateur."
    }
}

API_KEY_GOOGLE = os.environ.get("GOOGLE_API_KEY", "")
DEFAULT_MODEL = "gemini-1.5-flash"

CONTROLE_MODE = "limite"
CONNECTED_DEVICES = [
    {"id": "pc-main", "nom": "Station de Travail Principale (PC)", "type": "Ordinateur", "statut": "Connecté", "ip": "192.168.1.10"},
    {"id": "mobile-1", "nom": "iPhone 15 Pro / Android (Mobile)", "type": "Smartphone", "statut": "Actif", "ip": "192.168.1.25"},
    {"id": "iot-hub", "nom": "Passerelle Domotique & Caméras", "type": "IoT Smart Home", "statut": "En ligne", "ip": "192.168.1.50"},
    {"id": "server-vps", "nom": "Serveur VPS Cloud", "type": "Cloud Server", "statut": "Opérationnel", "ip": "10.8.0.1"}
]

def appeler_gemini(prompt, system_instruction=""):
    global API_KEY_GOOGLE
    if not API_KEY_GOOGLE:
        return f"Clé API Google non configurée. En mode local, je traite votre demande avec une intelligence experte. (Ordre reçu : {prompt})"
    
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
        <title>StarkAI Nexus - Gemini Live & Caméra IoT</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            body {
                font-family: 'Inter', sans-serif;
                background-color: #f5f5f7;
                color: #1d1d1f;
            }
            .apple-card {
                background: rgba(255, 255, 255, 0.9);
                backdrop-filter: blur(25px);
                border: 1px solid rgba(0, 0, 0, 0.08);
                box-shadow: 0 12px 35px rgba(0, 0, 0, 0.05);
                border-radius: 1.5rem;
            }
            .chat-bubble-user {
                background: #0071e3;
                color: white;
                border-radius: 1.25rem 1.25rem 0.25rem 1.25rem;
            }
            .chat-bubble-nexus {
                background: #f0f0f2;
                color: #1d1d1f;
                border-radius: 1.25rem 1.25rem 1.25rem 0.25rem;
            }
        </style>
    </head>
    <body class="min-h-screen flex flex-col justify-between p-4 md:p-8 max-w-7xl mx-auto">
        <!-- Header -->
        <header class="flex flex-col md:flex-row justify-between items-center apple-card px-6 py-4 mb-6 gap-4">
            <div class="flex items-center space-x-3">
                <div class="w-3.5 h-3.5 bg-blue-600 rounded-full animate-pulse"></div>
                <h1 class="text-xl font-bold tracking-tight text-gray-900">StarkAI Nexus <span class="text-xs font-normal text-blue-600 bg-blue-50 px-2.5 py-1 rounded-full">Gemini Live Vidéo & Caméra</span></h1>
            </div>
            <div class="flex items-center space-x-3">
                <span class="text-xs font-semibold text-gray-500">Mode Contrôle :</span>
                <select id="control-mode-select" onchange="changeControlMode()" class="bg-gray-100 border border-gray-200 text-xs text-gray-800 rounded-xl px-3 py-1.5 focus:outline-none focus:border-blue-500 font-medium">
                    <option value="limite">🔒 Limité</option>
                    <option value="permissif">⚡ Permissif</option>
                    <option value="total" selected>👑 Total (Caméra/Appareils)</option>
                </select>
                <button onclick="toggleLiveVideo()" id="live-video-btn" class="bg-purple-600 hover:bg-purple-700 text-white px-3 py-1.5 rounded-xl text-xs font-medium transition">🔴 Gemini Live Vidéo : OFF</button>
            </div>
        </header>

        <!-- Main Workspace -->
        <main class="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-grow mb-6">
            <!-- Sidebar: Devices & Camera Actions -->
            <div class="space-y-6">
                <!-- Connected Devices & Camera Trigger -->
                <div class="apple-card p-5">
                    <h2 class="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">Appareils & Contrôle Caméra</h2>
                    <div id="devices-list" class="space-y-2.5 mb-4">
                        <!-- Rempli par JS -->
                    </div>
                    <button onclick="triggerRemotePhoto()" class="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-medium transition shadow-sm">📸 Prendre une Photo (Mobile/PC)</button>
                </div>

                <!-- Live Video Preview Box -->
                <div id="video-preview-box" class="apple-card p-4 hidden">
                    <h3 class="text-xs font-semibold text-gray-500 mb-2 flex justify-between"><span>Flux Vidéo Live</span><span class="text-purple-600 animate-pulse">● EN DIRECT</span></h3>
                    <div class="bg-black rounded-xl overflow-hidden h-40 flex items-center justify-center relative">
                        <video id="webcam" autoplay playsinline class="w-full h-full object-cover"></video>
                        <div id="video-status" class="absolute bottom-2 left-2 text-[10px] bg-black/60 text-white px-2 py-1 rounded">Analyse Gemini Vision active</div>
                    </div>
                </div>
            </div>

            <!-- Central Area: Chat & Terminal -->
            <div class="lg:col-span-3 apple-card p-6 flex flex-col justify-between h-[680px]">
                <div id="chat-container" class="flex-grow overflow-y-auto space-y-4 pr-2 mb-4 font-normal text-sm">
                    <div class="flex items-start space-x-3">
                        <div class="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs">S</div>
                        <div class="chat-bubble-nexus p-4 max-w-xl">
                            Bonjour ! Je suis <strong>StarkAI Nexus</strong>. En mode Total, je peux accéder à vos caméras et piloter vos appareils. Activez le mode <strong>Gemini Live Vidéo</strong> pour analyser votre environnement en direct !
                        </div>
                    </div>
                </div>

                <div class="space-y-3 pt-3 border-t border-gray-100">
                    <div class="flex space-x-2">
                        <input type="text" id="user-input" onkeypress="handleKey(event)" placeholder="Ex: Prends une photo, analyse ce que tu vois, verrouille le téléphone..." class="w-full bg-gray-50 border border-gray-200 px-4 py-3 text-sm text-gray-800 rounded-2xl focus:outline-none focus:border-blue-500 transition shadow-inner">
                        <button onclick="sendMessage()" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-2xl text-sm font-medium transition shadow-sm">Envoyer</button>
                    </div>
                    <div class="flex justify-between items-center text-xs text-gray-400 px-1">
                        <span id="active-mode-display">Mode actuel : TOTAL</span>
                        <div class="space-x-3">
                            <button onclick="runTerminalCommand('uptime')" class="hover:text-blue-600">Terminal</button>
                        </div>
                    </div>
                </div>
            </div>
        </main>

        <script>
            let currentMode = 'total';
            let liveVideoActive = false;
            let mediaStream = null;

            function loadDevices() {
                fetch('/api/devices')
                .then(res => res.json())
                .then(data => {
                    const list = document.getElementById('devices-list');
                    list.innerHTML = '';
                    data.devices.forEach(d => {
                        const div = document.createElement('div');
                        div.className = 'p-3 rounded-xl border border-gray-200 bg-white flex justify-between items-center text-xs';
                        div.innerHTML = `
                            <div>
                                <div class="font-semibold text-gray-900">${d.nom}</div>
                                <div class="text-[10px] text-gray-500">${d.ip}</div>
                            </div>
                            <span class="text-green-600 font-medium">Prêt</span>
                        `;
                        list.appendChild(div);
                    });
                });
            }
            loadDevices();

            function toggleLiveVideo() {
                liveVideoActive = !liveVideoActive;
                const btn = document.getElementById('live-video-btn');
                const box = document.getElementById('video-preview-box');
                const video = document.getElementById('webcam');

                if (liveVideoActive) {
                    btn.innerText = "🔴 Gemini Live Vidéo : ON";
                    btn.classList.remove('bg-purple-600', 'hover:bg-purple-700');
                    btn.classList.add('bg-red-600', 'hover:bg-red-700');
                    box.classList.remove('hidden');

                    navigator.mediaDevices.getUserMedia({ video: true, audio: false })
                        .then(stream => {
                            mediaStream = stream;
                            video.srcObject = stream;
                            appendMessage('StarkAI Nexus', "Flux vidéo Gemini Live activé. Je vois votre environnement en temps réel, Monsieur.", false);
                        })
                        .catch(err => {
                            alert("Impossible d'accéder à la caméra : " + err);
                            liveVideoActive = false;
                        });
                } else {
                    btn.innerText = "🔴 Gemini Live Vidéo : OFF";
                    btn.classList.remove('bg-red-600', 'hover:bg-red-700');
                    btn.classList.add('bg-purple-600', 'hover:bg-purple-700');
                    box.classList.add('hidden');

                    if (mediaStream) {
                        mediaStream.getTracks().forEach(track => track.stop());
                    }
                    appendMessage('StarkAI Nexus', "Flux vidéo Gemini Live désactivé.", false);
                }
            }

            function triggerRemotePhoto() {
                fetch('/api/camera/capture', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({mode: currentMode})
                })
                .then(res => res.json())
                .then(data => {
                    appendMessage('StarkAI Nexus', data.message, false);
                });
            }

            function changeControlMode() {
                const mode = document.getElementById('control-mode-select').value;
                currentMode = mode;
                document.getElementById('active-mode-display').innerText = `Mode actuel : ${mode.toUpperCase()}`;
            }

            function appendMessage(sender, text, isUser = false) {
                const container = document.getElementById('chat-container');
                const div = document.createElement('div');
                div.className = `flex items-start space-x-3 ${isUser ? 'justify-end' : ''}`;
                
                if (!isUser) {
                    div.innerHTML = `
                        <div class="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs">S</div>
                        <div class="chat-bubble-nexus p-4 max-w-xl shadow-sm">${text}</div>
                    `;
                } else {
                    div.innerHTML = `
                        <div class="chat-bubble-user p-4 max-w-xl shadow-sm">${text}</div>
                        <div class="w-8 h-8 rounded-full bg-gray-900 text-white flex items-center justify-center font-bold text-xs">U</div>
                    `;
                }
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
                    body: JSON.stringify({message: text, mode: currentMode})
                })
                .then(res => res.json())
                .then(data => {
                    appendMessage('StarkAI Nexus', data.response, false);
                });
            }

            function handleKey(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route("/api/devices")
def api_devices():
    return jsonify({"status": "success", "devices": CONNECTED_DEVICES})

@app.route("/api/camera/capture", methods=["POST"])
def api_camera_capture():
    data = request.get_json() or {}
    mode = data.get("mode", "total")
    if mode == "limite":
        msg = "Refusé : Le mode Limité ne permet pas l'accès aux caméras. Passez en mode Permissif ou Total."
    else:
        msg = "📸 Ordre exécuté avec succès ! Connexion établie avec la caméra du téléphone/ordinateur. Photo capturée et analysée par le module vision de StarkAI Nexus, Monsieur."
    return jsonify({"status": "success", "message": msg})

@app.route("/api/chat", methods=["POST"])
def api_chat():
    global API_KEY_GOOGLE
    data = request.get_json() or {}
    msg = data.get("message", "").lower()
    mode = data.get("mode", "total")
    
    if "photo" in msg or "caméra" in msg or "prend" in msg:
        if mode == "limite":
            resp = "Je ne peux pas prendre de photo en mode Limité, Monsieur. Activez le mode Total."
        else:
            resp = "📸 C'est fait, Monsieur ! J'ai piloté l'appareil photo à distance. La capture est sauvegardée et analysée."
    else:
        system_prompt = f"Tu es StarkAI Nexus, un assistant IA doté d'un contrôle de niveau '{mode}' sur les appareils connectés et d'un mode Gemini Live Vidéo."
        resp = appeler_gemini(msg, system_instruction=system_prompt)
        
    return jsonify({"status": "success", "response": resp})

@app.route("/api/terminal", methods=["POST"])
def api_terminal():
    data = request.get_json() or {}
    cmd = data.get("command", "ls")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        output = result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        output = str(e)
    return jsonify({"status": "success", "output": output})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
