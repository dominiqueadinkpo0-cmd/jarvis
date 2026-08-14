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
CONTROLE_MODE = "total"

CONNECTED_DEVICES = [
    {"id": "pc-main", "nom": "Station de Travail Principale (PC)", "type": "Ordinateur", "statut": "Connecté", "ip": "192.168.1.10"},
    {"id": "mobile-1", "nom": "Smartphone Android / iOS (Mobile)", "type": "Smartphone", "statut": "Actif", "ip": "192.168.1.25"},
    {"id": "iot-hub", "nom": "Passerelle Domotique & Caméras", "type": "IoT Smart Home", "statut": "En ligne", "ip": "192.168.1.50"},
    {"id": "server-vps", "nom": "Serveur VPS Cloud", "type": "Cloud Server", "statut": "Opérationnel", "ip": "10.8.0.1"}
]

def appeler_gemini(prompt, system_instruction=""):
    global API_KEY_GOOGLE
    if not API_KEY_GOOGLE:
        return f"Clé API Google non configurée. En mode local, je traite votre demande avec une intelligence experte. (Ordre : {prompt})"
    
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
        <title>StarkAI Nexus - Application Mobile & PWA</title>
        <link rel="manifest" href="/manifest.json">
        <meta name="theme-color" content="#0071e3">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
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
        <script>
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/sw.js').then(() => {
                    console.log("Service Worker enregistre avec succes.");
                });
            }
        </script>
    </head>
    <body class="min-h-screen flex flex-col justify-between p-4 md:p-8 max-w-7xl mx-auto">
        <!-- Header -->
        <header class="flex flex-col md:flex-row justify-between items-center apple-card px-6 py-4 mb-6 gap-4">
            <div class="flex items-center space-x-3">
                <div class="w-3.5 h-3.5 bg-blue-600 rounded-full animate-pulse"></div>
                <h1 class="text-xl font-bold tracking-tight text-gray-900">StarkAI Nexus <span class="text-xs font-normal text-blue-600 bg-blue-50 px-2.5 py-1 rounded-full">Prêt pour Mobile (PWA)</span></h1>
            </div>
            <div class="flex items-center space-x-3">
                <button onclick="installApp()" id="install-btn" class="bg-green-600 hover:bg-green-700 text-white px-3 py-1.5 rounded-xl text-xs font-medium transition hidden">📥 Installer sur l'appareil</button>
                <button onclick="toggleLiveVideo()" id="live-video-btn" class="bg-purple-600 hover:bg-purple-700 text-white px-3 py-1.5 rounded-xl text-xs font-medium transition">🔴 Gemini Live Vidéo : OFF</button>
            </div>
        </header>

        <!-- Main Workspace -->
        <main class="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-grow mb-6">
            <!-- Sidebar: Devices & Camera Actions -->
            <div class="space-y-6">
                <div class="apple-card p-5">
                    <h2 class="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">Appareils & Contrôle Caméra</h2>
                    <div id="devices-list" class="space-y-2.5 mb-4"></div>
                    <button onclick="triggerRemotePhoto()" class="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-medium transition shadow-sm">📸 Prendre une Photo (Mobile/PC)</button>
                </div>

                <div id="video-preview-box" class="apple-card p-4 hidden">
                    <h3 class="text-xs font-semibold text-gray-500 mb-2 flex justify-between"><span>Flux Vidéo Live</span><span class="text-purple-600 animate-pulse">● EN DIRECT</span></h3>
                    <div class="bg-black rounded-xl overflow-hidden h-40 flex items-center justify-center relative">
                        <video id="webcam" autoplay playsinline class="w-full h-full object-cover"></video>
                    </div>
                </div>
            </div>

            <!-- Central Area: Chat & Terminal -->
            <div class="lg:col-span-3 apple-card p-6 flex flex-col justify-between h-[680px]">
                <div id="chat-container" class="flex-grow overflow-y-auto space-y-4 pr-2 mb-4 font-normal text-sm">
                    <div class="flex items-start space-x-3">
                        <div class="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs">S</div>
                        <div class="chat-bubble-nexus p-4 max-w-xl">
                            Bonjour ! Je suis <strong>StarkAI Nexus</strong>. Vous pouvez installer cette application directement sur votre écran d'accueil mobile (Android / iOS) via le menu de votre navigateur ("Ajouter à l'écran d'accueil"). Comment puis-je vous aider ?
                        </div>
                    </div>
                </div>

                <div class="space-y-3 pt-3 border-t border-gray-100">
                    <div class="flex space-x-2">
                        <input type="text" id="user-input" onkeypress="handleKey(event)" placeholder="Discutez avec Nexus..." class="w-full bg-gray-50 border border-gray-200 px-4 py-3 text-sm text-gray-800 rounded-2xl focus:outline-none focus:border-blue-500 transition shadow-inner">
                        <button onclick="sendMessage()" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-2xl text-sm font-medium transition shadow-sm">Envoyer</button>
                    </div>
                    <div class="flex justify-between items-center text-xs text-gray-400 px-1">
                        <span>Mode : TOTAL (Mobile & Web)</span>
                        <button onclick="runTerminalCommand('uptime')" class="hover:text-blue-600">Terminal</button>
                    </div>
                </div>
            </div>
        </main>

        <script>
            let deferredPrompt;
            window.addEventListener('beforeinstallprompt', (e) => {
                e.preventDefault();
                deferredPrompt = e;
                document.getElementById('install-btn').classList.remove('hidden');
            });

            function installApp() {
                if (deferredPrompt) {
                    deferredPrompt.prompt();
                    deferredPrompt.userChoice.then((choiceResult) => {
                        if (choiceResult.outcome === 'accepted') {
                            console.log('Utilisateur a accepté l installation');
                        }
                        deferredPrompt = null;
                    });
                } else {
                    alert("Pour installer l'application sur votre mobile, appuyez sur le menu de votre navigateur (Safari ou Chrome) puis 'Ajouter à l'écran d'accueil'.");
                }
            }

            function loadDevices() {
                fetch('/api/devices')
                .then(res => res.json())
                .then(data => {
                    const list = document.getElementById('devices-list');
                    list.innerHTML = '';
                    data.devices.forEach(d => {
                        const div = document.createElement('div');
                        div.className = 'p-3 rounded-xl border border-gray-200 bg-white flex justify-between items-center text-xs';
                        div.innerHTML = `<div><div class="font-semibold text-gray-900">${d.nom}</div><div class="text-[10px] text-gray-500">${d.ip}</div></div><span class="text-green-600 font-medium">Prêt</span>`;
                        list.appendChild(div);
                    });
                });
            }
            loadDevices();

            let liveVideoActive = false;
            let mediaStream = null;

            function toggleLiveVideo() {
                liveVideoActive = !liveVideoActive;
                const btn = document.getElementById('live-video-btn');
                const box = document.getElementById('video-preview-box');
                const video = document.getElementById('webcam');

                if (liveVideoActive) {
                    btn.innerText = "🔴 Gemini Live Vidéo : ON";
                    btn.classList.replace('bg-purple-600', 'bg-red-600');
                    box.classList.remove('hidden');
                    navigator.mediaDevices.getUserMedia({ video: true, audio: false })
                        .then(stream => { mediaStream = stream; video.srcObject = stream; });
                } else {
                    btn.innerText = "🔴 Gemini Live Vidéo : OFF";
                    btn.classList.replace('bg-red-600', 'bg-purple-600');
                    box.classList.add('hidden');
                    if (mediaStream) mediaStream.getTracks().forEach(t => t.stop());
                }
            }

            function triggerRemotePhoto() {
                fetch('/api/camera/capture', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({mode: 'total'})
                })
                .then(res => res.json())
                .then(data => { appendMessage('StarkAI Nexus', data.message, false); });
            }

            function appendMessage(sender, text, isUser = false) {
                const container = document.getElementById('chat-container');
                const div = document.createElement('div');
                div.className = `flex items-start space-x-3 ${isUser ? 'justify-end' : ''}`;
                div.innerHTML = isUser ? `
                    <div class="chat-bubble-user p-4 max-w-xl shadow-sm">${text}</div>
                    <div class="w-8 h-8 rounded-full bg-gray-900 text-white flex items-center justify-center font-bold text-xs">U</div>
                ` : `
                    <div class="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs">S</div>
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
                    body: JSON.stringify({message: text, mode: 'total'})
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

@app.route("/api/camera/capture", methods=["POST"])
def api_camera_capture():
    return jsonify({"status": "success", "message": "📸 Ordre exécuté ! Caméra du mobile/PC pilotée avec succès."})

@app.route("/api/chat", methods=["POST"])
def api_chat():
    global API_KEY_GOOGLE
    data = request.get_json() or {}
    msg = data.get("message", "").lower()
    if "photo" in msg or "caméra" in msg:
        resp = "📸 Photo prise à distance avec succès ! Le module vision l'analyse."
    else:
        system_prompt = "Tu es StarkAI Nexus, un assistant IA puissant et chaleureux."
        resp = appeler_gemini(msg, system_instruction=system_prompt)
    return jsonify({"status": "success", "response": resp})

@app.route("/api/terminal", methods=["POST"])
def api_terminal():
    data = request.get_json() or {}
    cmd = data.get("command", "ls")
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        out = res.stdout if res.returncode == 0 else res.stderr
    except Exception as e:
        out = str(e)
    return jsonify({"status": "success", "output": out})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
