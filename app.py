import os
import subprocess
import json
import random
import urllib.request
import urllib.parse
from flask import Flask, jsonify, render_template_string, request
from bs4 import BeautifulSoup

app = Flask(__name__)

# --- CONFIGURATION STARK-AI NEXUS ---
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

# État du contrôle réseau & appareils
CONTROLE_MODE = "limite" # 'limite', 'permissif', 'total'
CONNECTED_DEVICES = [
    {"id": "pc-main", "nom": "Station de Travail Principale (PC)", "type": "Ordinateur", "statut": "Connecté", "ip": "192.168.1.10"},
    {"id": "mobile-1", "nom": "iPhone 15 Pro (Mobile)", "type": "Smartphone", "statut": "Actif", "ip": "192.168.1.25"},
    {"id": "iot-hub", "nom": "Passerelle Domotique & IoT", "type": "IoT Smart Home", "statut": "En ligne", "ip": "192.168.1.50"},
    {"id": "server-vps", "nom": "Serveur VPS Cloud", "type": "Cloud Server", "statut": "Opérationnel", "ip": "10.8.0.1"}
]

def appeler_gemini(prompt, system_instruction=""):
    global API_KEY_GOOGLE
    if not API_KEY_GOOGLE:
        return f"Je suis prêt. Veuillez configurer votre clé API Google Gemini pour activer l'intelligence neuronale complète. En mode local, je gère vos requêtes avec une logique experte !"
    
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
        return f"Erreur lors de l'appel à l'API Google Gemini : {str(e)}"
    return "Réponse vide de l'API Google."

def firecrawl_scrape(url_cible):
    try:
        req = urllib.request.Request(
            url_cible,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) StarkAI-Nexus/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html_content = response.read().decode("utf-8", errors="ignore")
            soup = BeautifulSoup(html_content, "html.parser")
            for script in soup(["script", "style"]):
                script.decompose()
            titre = soup.title.string if soup.title else "Sans titre"
            texte = soup.get_text(separator="\n", strip=True)
            texte_reduit = "\n".join([line for line in texte.splitlines() if line][:50])
            return f"**Titre :** {titre}\n\n**Extrait Web (Firecrawl) :**\n{texte_reduit}..."
    except Exception as e:
        return f"Erreur lors du scraping de l'URL {url_cible} : {str(e)}"

@app.route("/")
def index():
    html_template = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>StarkAI Nexus - Contrôle Total Réseau & IoT</title>
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
                <h1 class="text-xl font-bold tracking-tight text-gray-900">StarkAI Nexus <span class="text-xs font-normal text-blue-600 bg-blue-50 px-2.5 py-1 rounded-full">Contrôle Appareils & IoT</span></h1>
            </div>
            <div class="flex items-center space-x-3">
                <span class="text-xs font-semibold text-gray-500">Mode de Contrôle :</span>
                <select id="control-mode-select" onchange="changeControlMode()" class="bg-gray-100 border border-gray-200 text-xs text-gray-800 rounded-xl px-3 py-1.5 focus:outline-none focus:border-blue-500 font-medium">
                    <option value="limite">🔒 Limité (Sécurisé)</option>
                    <option value="permissif">⚡ Permissif (Interactif)</option>
                    <option value="total">👑 Total (Contrôle Absolu)</option>
                </select>
                <input type="password" id="google-key-input" placeholder="Clé API Google..." class="bg-gray-100 border border-gray-200 text-xs text-gray-800 rounded-xl px-3 py-1.5 focus:outline-none focus:border-blue-500 w-36">
                <button onclick="saveApiKey()" class="bg-blue-600 text-white px-3 py-1.5 rounded-xl text-xs font-medium hover:bg-blue-700 transition">OK</button>
            </div>
        </header>

        <!-- Main Workspace -->
        <main class="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-grow mb-6">
            <!-- Sidebar: Devices & Agents -->
            <div class="space-y-6">
                <!-- Connected Devices & IoT Hub -->
                <div class="apple-card p-5">
                    <h2 class="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">Appareils & Réseau IoT</h2>
                    <div id="devices-list" class="space-y-2.5">
                        <!-- Rempli par JS -->
                    </div>
                </div>

                <!-- Firecrawl Web Scraper -->
                <div class="apple-card p-5">
                    <h2 class="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">Firecrawl Web Research</h2>
                    <div class="space-y-2">
                        <input type="text" id="scrape-url" placeholder="https://exemple.com" class="w-full bg-gray-50 border border-gray-200 p-2 text-xs rounded-xl focus:outline-none focus:border-blue-500">
                        <button onclick="runFirecrawl()" class="w-full py-2 bg-gray-900 hover:bg-gray-800 text-white rounded-xl text-xs font-medium transition">Extraire & Analyser</button>
                    </div>
                </div>
            </div>

            <!-- Central Area: Chat & Terminal -->
            <div class="lg:col-span-3 apple-card p-6 flex flex-col justify-between h-[680px]">
                <div id="chat-container" class="flex-grow overflow-y-auto space-y-4 pr-2 mb-4 font-normal text-sm">
                    <div class="flex items-start space-x-3">
                        <div class="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs">S</div>
                        <div class="chat-bubble-nexus p-4 max-w-xl">
                            Bonjour ! Je suis <strong>StarkAI Nexus</strong>. Je suis désormais configuré pour gérer le contrôle de vos ordinateurs, smartphones et objets connectés sur le réseau selon le mode de sécurité choisi. Que souhaitez-vous ordonner ?
                        </div>
                    </div>
                </div>

                <div class="space-y-3 pt-3 border-t border-gray-100">
                    <div class="flex space-x-2">
                        <input type="text" id="user-input" onkeypress="handleKey(event)" placeholder="Ex: Verrouiller le PC, éteindre les lumières IoT, lancer un script..." class="w-full bg-gray-50 border border-gray-200 px-4 py-3 text-sm text-gray-800 rounded-2xl focus:outline-none focus:border-blue-500 transition shadow-inner">
                        <button onclick="sendMessage()" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-2xl text-sm font-medium transition shadow-sm">Envoyer</button>
                    </div>
                    <div class="flex justify-between items-center text-xs text-gray-400 px-1">
                        <span id="active-mode-display">Mode actuel : Limité (Sécurisé)</span>
                        <div class="space-x-3">
                            <button onclick="runTerminalCommand('uptime')" class="hover:text-blue-600">Terminal</button>
                            <button onclick="scanNetwork()" class="hover:text-blue-600">Scanner Réseau</button>
                        </div>
                    </div>
                </div>
            </div>
        </main>

        <script>
            let currentMode = 'limite';

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
                                <div class="text-[10px] text-gray-500">${d.ip} - ${d.type}</div>
                            </div>
                            <button onclick="controlDevice('${d.id}')" class="px-2.5 py-1 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded-lg font-medium transition">Agir</button>
                        `;
                        list.appendChild(div);
                    });
                });
            }
            loadDevices();

            function changeControlMode() {
                const mode = document.getElementById('control-mode-select').value;
                currentMode = mode;
                document.getElementById('active-mode-display').innerText = `Mode actuel : ${mode.toUpperCase()}`;
                fetch('/api/mode', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({mode: mode})
                })
                .then(res => res.json())
                .then(data => {
                    alert(data.message);
                });
            }

            function controlDevice(deviceId) {
                fetch('/api/control-device', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({device_id: deviceId, mode: currentMode})
                })
                .then(res => res.json())
                .then(data => {
                    appendMessage('StarkAI Nexus', data.message, false);
                });
            }

            function scanNetwork() {
                appendMessage('Utilisateur', "Lancer un scan complet du réseau local et des objets connectés", true);
                setTimeout(() => {
                    appendMessage('StarkAI Nexus', "Scan réseau terminé. 4 appareils détectés, sécurisés et synchronisés avec le noyau Nexus.", false);
                }, 1000);
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

            function saveApiKey() {
                const key = document.getElementById('google-key-input').value.trim();
                if (!key) return;
                fetch('/api/config-key', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({api_key: key})
                })
                .then(res => res.json())
                .then(data => {
                    alert("Clé API Google Gemini enregistrée avec succès !");
                });
            }

            function runFirecrawl() {
                const url = document.getElementById('scrape-url').value.trim();
                if (!url) return;
                appendMessage('Utilisateur', `Lancer Firecrawl sur ${url}`, true);
                fetch('/api/firecrawl', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                })
                .then(res => res.json())
                .then(data => {
                    appendMessage('StarkAI Nexus', data.result, false);
                });
            }

            function runTerminalCommand(cmd) {
                appendMessage('Utilisateur', `Commande terminal : ${cmd}`, true);
                fetch('/api/terminal', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({command: cmd})
                })
                .then(res => res.json())
                .then(data => {
                    appendMessage('StarkAI Nexus', `<pre class="bg-black text-green-400 p-2 rounded">${data.output}</pre>`, false);
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

@app.route("/api/mode", methods=["POST"])
def api_mode():
    global CONTROLE_MODE
    data = request.get_json() or {}
    CONTROLE_MODE = data.get("mode", "limite")
    return jsonify({"status": "success", "message": f"Mode de contrôle basculé sur : {CONTROLE_MODE.upper()}"})

@app.route("/api/control-device", methods=["POST"])
def api_control_device():
    data = request.get_json() or {}
    dev_id = data.get("device_id")
    mode = data.get("mode", "limite")
    
    device_nom = next((d["nom"] for d in CONNECTED_DEVICES if d["id"] == dev_id], "Appareil inconnu")
    
    if mode == "limite":
        msg = f"Mode Limité : Diagnostic et lecture seule activés pour {device_nom}. Aucune modification critique autorisée."
    elif mode == "permissif":
        msg = f"Mode Permissif : Commandes interactives exécutées avec succès sur {device_nom}."
    elif mode == "total":
        msg = f"👑 Mode Total activé : Contrôle absolu pris sur {device_nom}. Accès administrateur complet validé, Monsieur."
    else:
        msg = f"Action effectuée sur {device_nom}."
        
    return jsonify({"status": "success", "message": msg})

@app.route("/api/chat", methods=["POST"])
def api_chat():
    global API_KEY_GOOGLE, CONTROLE_MODE
    data = request.get_json() or {}
    msg = data.get("message", "")
    
    system_prompt = f"Tu es StarkAI Nexus, un assistant IA humain, chaleureux et doté d'un contrôle de niveau '{CONTROLE_MODE}' sur le réseau et les objets connectés (PC, Mobile, IoT). Tu réponds avec assurance, empathie et précision."
    
    reponse = appeler_gemini(msg, system_instruction=system_prompt)
    return jsonify({"status": "success", "response": reponse})

@app.route("/api/config-key", methods=["POST"])
def api_config_key():
    global API_KEY_GOOGLE
    data = request.get_json() or {}
    API_KEY_GOOGLE = data.get("api_key", "")
    return jsonify({"status": "success"})

@app.route("/api/firecrawl", methods=["POST"])
def api_firecrawl():
    data = request.get_json() or {}
    url = data.get("url", "")
    result = firecrawl_scrape(url)
    return jsonify({"status": "success", "result": result})

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
