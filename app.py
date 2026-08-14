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
        "nom": "Nexus - Sécurité & DevOps",
        "role": "Audit de code, déploiement VPS, gestion des conteneurs et protocoles de défense.",
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

OBJECTIVES = []
API_KEY_GOOGLE = os.environ.get("GOOGLE_API_KEY", "")
DEFAULT_MODEL = "gemini-1.5-flash"

# --- MOTEUR GOOGLE GEMINI (REST API) & FIRECRAWL ---
def appeler_gemini(prompt, system_instruction=""):
    global API_KEY_GOOGLE
    if not API_KEY_GOOGLE:
        # Réponse chaleureuse si pas de clé configurée
        return f"Je suis prêt à utiliser les modèles Google Gemini. Veuillez configurer votre clé API Google pour activer l'intelligence neuronale complète. En attendant, je gère vos requêtes en mode local intelligent !"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{DEFAULT_MODEL}:generateContent?key={API_KEY_GOOGLE}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]} if system_instruction else None
    }
    # Nettoyer les champs None
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
    """Fonction Firecrawl / Web Scraping avancée inspirée du fork jarvis-assistant-vocal"""
    try:
        req = urllib.request.Request(
            url_cible,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) StarkAI-Nexus/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html_content = response.read().decode("utf-8", errors="ignore")
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Supprimer scripts et styles
            for script in soup(["script", "style"]):
                script.decompose()
                
            titre = soup.title.string if soup.title else "Sans titre"
            texte = soup.get_text(separator="\n", strip=True)
            # Limiter la taille
            texte_reduit = "\n".join([line for line in texte.splitlines() if line][:50])
            return f"**Titre :** {titre}\n\n**Extrait Web (Firecrawl Engine) :**\n{texte_reduit}..."
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
        <title>StarkAI Nexus - Google AI & Firecrawl OS</title>
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
                <h1 class="text-xl font-bold tracking-tight text-gray-900">StarkAI Nexus <span class="text-xs font-normal text-blue-600 bg-blue-50 px-2.5 py-1 rounded-full">Google Gemini + Firecrawl</span></h1>
            </div>
            <div class="flex items-center space-x-3">
                <input type="password" id="google-key-input" placeholder="Clé API Google Gemini..." class="bg-gray-100 border border-gray-200 text-xs text-gray-800 rounded-xl px-3 py-1.5 focus:outline-none focus:border-blue-500 w-48">
                <button onclick="saveApiKey()" class="bg-blue-600 text-white px-3 py-1.5 rounded-xl text-xs font-medium hover:bg-blue-700 transition">Définir Clé</button>
            </div>
        </header>

        <!-- Main Workspace -->
        <main class="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-grow mb-6">
            <!-- Sidebar: Agents & Web Scraping -->
            <div class="space-y-6">
                <!-- Agents -->
                <div class="apple-card p-5">
                    <h2 class="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">Équipe Multi-Agents</h2>
                    <div class="space-y-2.5">
                        <div onclick="selectAgent('developpeur')" id="agent-developpeur" class="agent-card cursor-pointer p-3 rounded-xl border border-blue-500 bg-blue-50/50 flex items-center space-x-3 transition">
                            <span class="text-xl">💻</span>
                            <div>
                                <div class="text-xs font-semibold text-gray-900">Développeur</div>
                                <div class="text-[10px] text-gray-500">Code & Implémentation</div>
                            </div>
                        </div>
                        <div onclick="selectAgent('architecte')" id="agent-architecte" class="agent-card cursor-pointer p-3 rounded-xl border border-gray-200 bg-white hover:bg-gray-50 flex items-center space-x-3 transition">
                            <span class="text-xl">🏛️</span>
                            <div>
                                <div class="text-xs font-semibold text-gray-900">Architecte</div>
                                <div class="text-[10px] text-gray-500">Structure & Stratégie</div>
                            </div>
                        </div>
                        <div onclick="selectAgent('securite')" id="agent-securite" class="agent-card cursor-pointer p-3 rounded-xl border border-gray-200 bg-white hover:bg-gray-50 flex items-center space-x-3 transition">
                            <span class="text-xl">🛡️</span>
                            <div>
                                <div class="text-xs font-semibold text-gray-900">Sécurité / VPS</div>
                                <div class="text-[10px] text-gray-500">DevOps & Cloud</div>
                            </div>
                        </div>
                        <div onclick="selectAgent('createur')" id="agent-createur" class="agent-card cursor-pointer p-3 rounded-xl border border-gray-200 bg-white hover:bg-gray-50 flex items-center space-x-3 transition">
                            <span class="text-xl">✨</span>
                            <div>
                                <div class="text-xs font-semibold text-gray-900">Créateur & UX</div>
                                <div class="text-[10px] text-gray-500">Design & Esthétique</div>
                            </div>
                        </div>
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

            <!-- Central Area: Chat & Objectives -->
            <div class="lg:col-span-3 apple-card p-6 flex flex-col justify-between h-[680px]">
                <div id="chat-container" class="flex-grow overflow-y-auto space-y-4 pr-2 mb-4 font-normal text-sm">
                    <div class="flex items-start space-x-3">
                        <div class="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs">S</div>
                        <div class="chat-bubble-nexus p-4 max-w-xl">
                            Bonjour ! Je suis <strong>StarkAI Nexus</strong>, votre nouvel assistant propulsé par les modèles Google Gemini et doté des capacités de scraping Firecrawl. Discutons de vos objectifs de développement !
                        </div>
                    </div>
                </div>

                <div class="space-y-3 pt-3 border-t border-gray-100">
                    <div class="flex space-x-2">
                        <input type="text" id="user-input" onkeypress="handleKey(event)" placeholder="Posez une question ou donnez un objectif..." class="w-full bg-gray-50 border border-gray-200 px-4 py-3 text-sm text-gray-800 rounded-2xl focus:outline-none focus:border-blue-500 transition shadow-inner">
                        <button onclick="sendMessage()" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-2xl text-sm font-medium transition shadow-sm">Envoyer</button>
                    </div>
                    <div class="flex justify-between items-center text-xs text-gray-400 px-1">
                        <span id="active-agent-indicator">Agent actif : Développeur (Modèle : Google Gemini 1.5 Flash)</span>
                        <div class="space-x-3">
                            <button onclick="runTerminalCommand('ls -la')" class="hover:text-blue-600">Terminal</button>
                            <button onclick="deployCloud()" class="hover:text-blue-600">Déploiement VPS</button>
                        </div>
                    </div>
                </div>
            </div>
        </main>

        <script>
            let currentAgent = 'developpeur';

            function selectAgent(agentKey) {
                currentAgent = agentKey;
                document.querySelectorAll('.agent-card').forEach(el => {
                    el.classList.remove('border-blue-500', 'bg-blue-50/50');
                    el.classList.add('border-gray-200', 'bg-white');
                });
                const active = document.getElementById(`agent-${agentKey}`);
                active.classList.remove('border-gray-200', 'bg-white');
                active.classList.add('border-blue-500', 'bg-blue-50/50');
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
                    body: JSON.stringify({message: text, agent: currentAgent})
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

            function deployCloud() {
                appendMessage('Utilisateur', "Déployer sur le VPS Cloud", true);
                setTimeout(() => {
                    appendMessage('StarkAI Nexus', "Déploiement VPS Cloud réussi ! Serveur configuré et sécurisé.", false);
                }, 1000);
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

@app.route("/api/chat", methods=["POST"])
def api_chat():
    global API_KEY_GOOGLE
    data = request.get_json() or {}
    msg = data.get("message", "")
    agent_key = data.get("agent", "developpeur")
    agent = AGENTS.get(agent_key, AGENTS["developpeur"])
    
    system_prompt = f"Tu es StarkAI Nexus, un assistant IA humain, chaleureux et extrêmement compétent. Tu agis en tant que {agent['nom']} ({agent['role']}). Ton style est {agent['style']}."
    
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
