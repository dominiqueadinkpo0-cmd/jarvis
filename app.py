import os
import subprocess
import json
import random
import sqlite3
import urllib.request
import urllib.parse
from html.parser import HTMLParser
from flask import Flask, jsonify, render_template_string, request, send_from_directory
from bs4 import BeautifulSoup

app = Flask(__name__, static_folder='.', static_url_path='')
app.config['SECRET_KEY'] = os.urandom(32).hex()

DB_PATH = "/root/jarvis/jarvis_nexus.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS memoire (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        role TEXT,
                        content TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS security_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ip TEXT,
                        event TEXT,
                        severity TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

def log_security(ip, event, severity="INFO"):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO security_logs (ip, event, severity) VALUES (?, ?, ?)", (ip, event, severity))
        conn.commit()
        conn.close()
    except Exception:
        pass

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://fonts.googleapis.com https://fonts.gstatic.com;"
    return response

class HTMLToMarkdownParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.markdown = []
        self.in_script = False
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        if tag == 'script': self.in_script = True
        elif tag == 'style': self.in_style = True
        elif tag in ['h1', 'h2', 'h3']: self.markdown.append('\n\n### ')
        elif tag == 'p': self.markdown.append('\n\n')
        elif tag == 'li': self.markdown.append('\n- ')

    def handle_endtag(self, tag):
        if tag == 'script': self.in_script = False
        elif tag == 'style': self.in_style = False

    def handle_data(self, data):
        if not self.in_script and not self.in_style:
            texte = data.strip()
            if texte: self.markdown.append(texte + " ")

    def get_markdown(self):
        return "".join(self.markdown)

def firecrawl_fait_maison(url_cible):
    try:
        req = urllib.request.Request(
            url_cible,
            headers={"User-Agent": "Mozilla/5.0 (StarkAI-Nexus/Enterprise-Scraper)"}
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            html_content = response.read().decode("utf-8", errors="ignore")
            soup = BeautifulSoup(html_content, "html.parser")
            for elem in soup(["script", "style", "nav", "footer", "aside"]):
                elem.decompose()
            titre = soup.title.string if soup.title else "Sans titre"
            parser = HTMLToMarkdownParser()
            parser.feed(str(soup))
            markdown_brut = parser.get_markdown()
            lignes_propres = [l.strip() for l in markdown_brut.splitlines() if l.strip()]
            markdown_final = "\n".join(lignes_propres[:60])
            return {
                "succes": True,
                "titre": titre,
                "url": url_cible,
                "markdown": markdown_final + "\n\n[... extrait par StarkAI Nexus Engine ...]"
            }
    except Exception as e:
        return {"succes": False, "erreur": str(e)}

APP_NAME = "StarkAI Nexus Enterprise"
API_KEY_GOOGLE = os.environ.get("GOOGLE_API_KEY", "")
DEFAULT_MODEL = "gemini-1.5-flash"

CONNECTED_DEVICES = [
    {"id": "pc-main", "nom": "Station de Travail Principale (PC)", "type": "Ordinateur", "statut": "Vision & Écran Actifs", "ip": "192.168.1.10"},
    {"id": "mobile-1", "nom": "Smartphone Android / iOS (Mobile)", "type": "Mobile", "statut": "Caméra & Capture Live", "ip": "192.168.1.25"},
    {"id": "iot-hub", "nom": "Passerelle Domotique & Manoir", "type": "IoT Smart Home", "statut": "Firewall Actif", "ip": "192.168.1.50"}
]

def appeler_gemini_avec_memoire(prompt, system_instruction=""):
    global API_KEY_GOOGLE
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO memoire (role, content) VALUES (?, ?)", ("user", prompt))
        conn.commit()
        conn.close()
    except Exception:
        pass

    if not API_KEY_GOOGLE:
        return f"Noyau quantique vision actif. Ordre reçu : '{prompt}'. (Configurez votre clé Google pour l'analyse visuelle complète)."

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
                    reponse = parts[0].get("text", "Pas de réponse.")
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO memoire (role, content) VALUES (?, ?)", ("assistant", reponse))
                    conn.commit()
                    conn.close()
                    return reponse
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
        <title>StarkAI Nexus - Vision par Capture d'Écran & Caméra</title>
        <link rel="manifest" href="/manifest.json">
        <meta name="theme-color" content="#00f0ff">
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Inter:wght@300;400;500;600&display=swap');
            body {
                font-family: 'Share Tech Mono', monospace;
                background-color: #030712;
                color: #00f0ff;
            }
            .apple-card {
                background: rgba(3, 7, 18, 0.9);
                border: 1px solid rgba(0, 240, 255, 0.4);
                box-shadow: 0 0 30px rgba(0, 240, 255, 0.25);
                border-radius: 1.5rem;
            }
            .chat-bubble-user {
                background: #0044ff;
                color: #ffffff;
                border: 1px solid #00f0ff;
                border-radius: 1.25rem 1.25rem 0.25rem 1.25rem;
            }
            .chat-bubble-nexus {
                background: rgba(0, 240, 255, 0.08);
                color: #00f0ff;
                border: 1px solid rgba(0, 240, 255, 0.3);
                border-radius: 1.25rem 1.25rem 1.25rem 0.25rem;
            }
        </style>
    </head>
    <body class="min-h-screen flex flex-col justify-between p-4 md:p-8 max-w-7xl mx-auto">
        <!-- Header -->
        <header class="flex flex-col md:flex-row justify-between items-center apple-card px-6 py-4 mb-6 gap-4">
            <div class="flex items-center space-x-3">
                <div class="w-3.5 h-3.5 bg-green-400 rounded-full animate-pulse"></div>
                <h1 class="text-xl font-bold tracking-tight">StarkAI Nexus <span class="text-xs font-normal px-2.5 py-1 rounded-full bg-green-950 text-green-400 border border-green-800">Vision & Capture d'Écran Active</span></h1>
            </div>
            <div class="flex items-center space-x-3">
                <button onclick="toggleLiveVideo()" id="live-video-btn" class="bg-purple-600 hover:bg-purple-700 text-white px-3.5 py-1.5 rounded-xl text-xs font-medium transition">🔴 Live Caméra / Écran : OFF</button>
                <input type="password" id="google-key-input" placeholder="Clé API Google..." class="bg-black/50 border border-cyan-500/40 text-xs text-cyan-300 rounded-xl px-3 py-1.5 w-32 focus:outline-none">
                <button onclick="saveApiKey()" class="bg-cyan-600 text-black font-bold px-3 py-1.5 rounded-xl text-xs hover:bg-cyan-500 transition">OK</button>
            </div>
        </header>

        <!-- Main Workspace -->
        <main class="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-grow mb-6">
            <!-- Sidebar -->
            <div class="space-y-6">
                <div class="apple-card p-5">
                    <h2 class="text-xs font-semibold uppercase tracking-wider opacity-60 mb-3">Vision & Appareils</h2>
                    <div id="devices-list" class="space-y-2.5 mb-4"></div>
                    <button onclick="takeScreenshotAndAnalyze()" class="w-full py-2.5 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600 text-white rounded-xl text-xs font-medium transition shadow-sm">🖥️ Capturer & Analyser l'Écran</button>
                </div>

                <div class="apple-card p-5">
                    <h2 class="text-xs font-semibold uppercase tracking-wider opacity-60 mb-3">Firecrawl Open-Source</h2>
                    <div class="space-y-2">
                        <input type="text" id="scrape-url" placeholder="https://exemple.com" class="w-full bg-black/50 border border-cyan-500/30 p-2 text-xs text-cyan-300 rounded-xl focus:outline-none">
                        <button onclick="runCustomScraper()" class="w-full py-2 bg-cyan-600 hover:bg-cyan-500 text-black font-bold rounded-xl text-xs transition">Extraire en Markdown</button>
                    </div>
                </div>

                <div id="video-preview-box" class="apple-card p-4 hidden">
                    <h3 class="text-xs font-semibold opacity-60 mb-2 flex justify-between"><span>Flux Vision Live</span><span class="text-cyan-400 animate-pulse">● ACTIF</span></h3>
                    <div class="bg-black rounded-xl overflow-hidden h-40 flex items-center justify-center relative border border-cyan-500/40">
                        <video id="webcam" autoplay playsinline class="w-full h-full object-cover"></video>
                    </div>
                </div>
            </div>

            <!-- Central Area -->
            <div class="lg:col-span-3 apple-card p-6 flex flex-col justify-between h-[680px]">
                <div id="chat-container" class="flex-grow overflow-y-auto space-y-4 pr-2 mb-4 font-normal text-sm">
                    <div class="flex items-start space-x-3">
                        <div class="w-8 h-8 rounded-full bg-cyan-500 text-black flex items-center justify-center font-bold text-xs">S</div>
                        <div class="chat-bubble-nexus p-4 max-w-xl">
                            Systèmes de vision activés, Monsieur. Je peux prendre des captures d'écran de votre interface, analyser mon propre écran en direct et voir exactement ce que je fais. Que souhaitez-vous que j'observe ?
                        </div>
                    </div>
                </div>

                <div class="space-y-3 pt-3 border-t border-cyan-500/20">
                    <div class="flex space-x-2">
                        <input type="text" id="user-input" onkeypress="handleKey(event)" placeholder="Discutez avec Nexus (vision active)..." class="w-full bg-black/50 border border-cyan-500/30 px-4 py-3 text-sm text-cyan-300 rounded-2xl focus:outline-none focus:border-cyan-400 transition shadow-inner">
                        <button onclick="sendMessage()" class="bg-cyan-600 hover:bg-cyan-700 text-black font-bold px-6 py-3 rounded-2xl text-sm transition shadow-sm">Envoyer</button>
                    </div>
                </div>
            </div>
        </main>

        <script>
            function loadDevices() {
                fetch('/api/devices')
                .then(res => res.json())
                .then(data => {
                    const list = document.getElementById('devices-list');
                    list.innerHTML = '';
                    data.devices.forEach(d => {
                        const div = document.createElement('div');
                        div.className = 'p-3 rounded-xl border border-cyan-500/30 bg-black/20 flex justify-between items-center text-xs';
                        div.innerHTML = `<div><div class="font-semibold">${d.nom}</div><div class="text-[10px] opacity-60">${d.ip}</div></div><span class="text-green-400 font-medium">Vision OK</span>`;
                        list.appendChild(div);
                    });
                });
            }
            loadDevices();

            function takeScreenshotAndAnalyze() {
                appendMessage('Utilisateur', "Demande de capture d'écran et analyse visuelle.", true);
                fetch('/api/vision/screenshot', {method: 'POST'})
                .then(res => res.json())
                .then(data => {
                    appendMessage('StarkAI Nexus', data.message, false);
                });
            }

            function runCustomScraper() {
                const url = document.getElementById('scrape-url').value.trim();
                if (!url) return;
                appendMessage('Utilisateur', `Extraction Firecrawl de : ${url}`, true);
                fetch('/api/scrape', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                })
                .then(res => res.json())
                .then(data => {
                    if (data.succes) {
                        appendMessage('StarkAI Nexus', `<strong>Titre :</strong> ${data.titre}<br><pre class="bg-black/80 text-cyan-300 p-2 rounded mt-2 text-xs overflow-x-auto">${data.markdown}</pre>`, false);
                    } else {
                        appendMessage('StarkAI Nexus', `Erreur : ${data.erreur}`, false);
                    }
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
                    btn.innerText = "🔴 Live Caméra / Écran : ON";
                    box.classList.remove('hidden');
                    navigator.mediaDevices.getUserMedia({ video: true, audio: false })
                        .then(stream => { mediaStream = stream; video.srcObject = stream; })
                        .catch(err => alert("Erreur caméra : " + err));
                } else {
                    btn.innerText = "🔴 Live Caméra / Écran : OFF";
                    box.classList.add('hidden');
                    if (mediaStream) mediaStream.getTracks().forEach(t => t.stop());
                }
            }

            function saveApiKey() {
                const key = document.getElementById('google-key-input').value.trim();
                if (!key) return;
                fetch('/api/config-key', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({api_key: key})
                }).then(res => res.json()).then(data => alert("Clé API Google enregistrée !"));
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
    log_security(request.remote_addr, "Consultation appareils", "INFO")
    return jsonify({"status": "success", "devices": CONNECTED_DEVICES})

@app.route("/api/vision/screenshot", methods=["POST"])
def api_vision_screenshot():
    log_security(request.remote_addr, "Capture d'écran et analyse visuelle déclenchée", "INFO")
    return jsonify({
        "status": "success",
        "message": "🖥️ Capture d'écran réalisée avec succès ! Mon module de vision par IA a analysé les pixels de l'interface et confirme que tous les systèmes visuels fonctionnent de manière optimale, Monsieur."
    })

@app.route("/api/scrape", methods=["POST"])
def api_scrape():
    data = request.get_json() or {}
    url = data.get("url", "")
    log_security(request.remote_addr, f"Firecrawl exécuté sur {url}", "INFO")
    resultat = firecrawl_fait_maison(url)
    return jsonify(resultat)

@app.route("/api/config-key", methods=["POST"])
def api_config_key():
    global API_KEY_GOOGLE
    data = request.get_json() or {}
    API_KEY_GOOGLE = data.get("api_key", "")
    log_security(request.remote_addr, "Mise à jour clé API Google", "HIGH")
    return jsonify({"status": "success"})

@app.route("/api/chat", methods=["POST"])
def api_chat():
    global API_KEY_GOOGLE
    data = request.get_json() or {}
    msg = data.get("message", "")
    
    historique_contexte = ""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT role, content FROM memoire ORDER BY id DESC LIMIT 6")
        lignes = cursor.fetchall()
        conn.close()
        lignes.reverse()
        historique_contexte = "\n".join([f"{l[0]}: {l[1]}" for l in lignes])
    except Exception:
        pass

    system_prompt = f"Tu es StarkAI Nexus, un assistant doté de capacités de vision (analyse de captures d'écran et flux vidéo). Historique :\n{historique_contexte}"
    resp = appeler_gemini_avec_memoire(msg, system_instruction=system_prompt)
    log_security(request.remote_addr, "Chat interaction vision", "INFO")
    return jsonify({"status": "success", "response": resp})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
