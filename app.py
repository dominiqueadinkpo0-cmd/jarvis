import os
import random
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

PROTOCOLS = {
    "house party": "Activation du protocole House Party. Déploiement de toutes les armures en cours, Monsieur.",
    "clean slate": "Protocole Clean Slate initialisé. Effacement des données non essentielles.",
    "veronica": "Déploiement du satellite Veronica et de l'armure Hulkbuster en approche, Monsieur.",
    "urgence": "Protocoles d'urgence activés. Redirection de l'énergie sécurisée.",
}

RESPONSES = [
    "À votre service, Monsieur. Tous les systèmes fonctionnent de manière optimale.",
    "Analyse terminée. Aucune anomalie sur le réseau Apple / Stark.",
    "C'est fait, Monsieur. Voulez-vous que j'envoie un rapport à Pepper ?",
    "Mes algorithmes confirment la pertinence de cette action, Monsieur.",
    "L'armure est prête pour un éventuel déploiement.",
    "Connexion quantique sécurisée établie.",
]

@app.route("/")
def index():
    html_template = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>J.A.R.V.I.S. - Apple Stark Edition</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            body {
                font-family: 'Inter', sans-serif;
                background-color: #f5f5f7;
                color: #1d1d1f;
            }
            .apple-card {
                background: rgba(255, 255, 255, 0.8);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(0, 0, 0, 0.06);
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04);
                border-radius: 1.25rem;
            }
            .arc-reactor-apple {
                width: 120px;
                height: 120px;
                border-radius: 50%;
                background: radial-gradient(circle, #0071e3 0%, #0040dd 70%, #f5f5f7 100%);
                box-shadow: 0 0 25px rgba(0, 113, 227, 0.4), inset 0 0 15px rgba(255, 255, 255, 0.8);
                animation: apple-pulse 3s infinite ease-in-out;
            }
            @keyframes apple-pulse {
                0% { transform: scale(0.97); box-shadow: 0 0 15px rgba(0, 113, 227, 0.3); }
                50% { transform: scale(1.03); box-shadow: 0 0 35px rgba(0, 113, 227, 0.6); }
                100% { transform: scale(0.97); box-shadow: 0 0 15px rgba(0, 113, 227, 0.3); }
            }
        </style>
    </head>
    <body class="min-h-screen flex flex-col justify-between p-6 max-w-6xl mx-auto">
        <!-- Header -->
        <header class="flex justify-between items-center apple-card px-6 py-4 mb-6">
            <div class="flex items-center space-x-3">
                <div class="w-3 h-3 bg-blue-600 rounded-full"></div>
                <h1 class="text-lg font-semibold tracking-tight text-gray-900">J.A.R.V.I.S.</h1>
                <span class="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-medium">Pro</span>
            </div>
            <div class="text-xs text-gray-500 font-medium">STARK // APPLE ECOSYSTEM</div>
            <div id="clock" class="text-sm font-medium text-gray-700">00:00:00</div>
        </header>

        <!-- Main Content -->
        <main class="grid grid-cols-1 md:grid-cols-3 gap-6 flex-grow mb-6">
            <!-- Left Panel: Diagnostics -->
            <div class="apple-card p-6 flex flex-col justify-between">
                <div>
                    <h2 class="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-4">Diagnostics Système</h2>
                    <div class="space-y-4 text-sm">
                        <div>
                            <div class="flex justify-between mb-1 text-gray-700"><span class="font-medium">Noyau Arc</span><span id="reactor-power" class="text-blue-600 font-semibold">100%</span></div>
                            <div class="w-full bg-gray-200 h-2 rounded-full overflow-hidden"><div id="reactor-bar" class="bg-blue-600 h-full w-full rounded-full"></div></div>
                        </div>
                        <div>
                            <div class="flex justify-between mb-1 text-gray-700"><span class="font-medium">Charge CPU</span><span id="cpu-load" class="font-semibold text-gray-900">14.2%</span></div>
                            <div class="w-full bg-gray-200 h-2 rounded-full overflow-hidden"><div id="cpu-bar" class="bg-blue-500 h-full w-[14%] rounded-full"></div></div>
                        </div>
                        <div>
                            <div class="flex justify-between mb-1 text-gray-700"><span class="font-medium">Mémoire Unifiée</span><span id="ram-load" class="font-semibold text-gray-900">38.5%</span></div>
                            <div class="w-full bg-gray-200 h-2 rounded-full overflow-hidden"><div id="ram-bar" class="bg-indigo-500 h-full w-[38%] rounded-full"></div></div>
                        </div>
                    </div>
                </div>
                <div class="mt-6 pt-4 border-t border-gray-100">
                    <button onclick="runDiagnostics()" class="w-full py-2.5 bg-gray-900 hover:bg-gray-800 text-white rounded-xl text-xs font-medium tracking-wide transition shadow-sm">Lancer le diagnostic</button>
                </div>
            </div>

            <!-- Center Panel: Arc Reactor & Voice -->
            <div class="apple-card p-6 flex flex-col items-center justify-center text-center">
                <div class="arc-reactor-apple mb-6 cursor-pointer" onclick="speakJarvis('Systèmes opérationnels, Monsieur.')" title="Cliquer pour interagir"></div>
                <div id="status-text" class="text-sm font-medium text-gray-800 max-w-xs min-h-[3rem] flex items-center justify-center">
                    "Bonjour Monsieur. Tous les protocoles sont actifs."
                </div>
                <div class="flex space-x-3 mt-6">
                    <button onclick="toggleVoice()" id="voice-btn" class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded-xl text-xs font-medium transition border border-gray-200">Voix: OFF</button>
                    <button onclick="triggerProtocol('house party')" class="px-4 py-2 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded-xl text-xs font-medium transition border border-blue-200">House Party</button>
                </div>
            </div>

            <!-- Right Panel: Protocols & Terminal -->
            <div class="apple-card p-6 flex flex-col justify-between">
                <div>
                    <h2 class="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-4">Protocoles Rapides</h2>
                    <div class="grid grid-cols-2 gap-2 text-xs">
                        <button onclick="triggerProtocol('clean slate')" class="p-2.5 bg-gray-50 hover:bg-gray-100 text-gray-700 rounded-xl font-medium border border-gray-200 text-left transition">Clean Slate</button>
                        <button onclick="triggerProtocol('veronica')" class="p-2.5 bg-gray-50 hover:bg-gray-100 text-gray-700 rounded-xl font-medium border border-gray-200 text-left transition">Veronica</button>
                        <button onclick="triggerProtocol('urgence')" class="p-2.5 bg-gray-50 hover:bg-gray-100 text-gray-700 rounded-xl font-medium border border-gray-200 text-left transition">Urgence</button>
                        <button onclick="askJarvis('Statut global')" class="p-2.5 bg-gray-50 hover:bg-gray-100 text-gray-700 rounded-xl font-medium border border-gray-200 text-left transition">Statut</button>
                    </div>
                </div>
                <div class="mt-6 pt-4 border-t border-gray-100">
                    <div class="text-xs font-semibold text-gray-400 mb-2">COMMANDE DIRECTE</div>
                    <div class="flex">
                        <input type="text" id="command-input" onkeypress="handleKey(event)" placeholder="Ex: Statut des armures..." class="w-full bg-gray-50 border border-gray-200 p-2.5 text-xs text-gray-800 rounded-l-xl focus:outline-none focus:border-blue-500">
                        <button onclick="sendPrompt()" class="bg-blue-600 hover:bg-blue-700 px-4 text-white rounded-r-xl text-xs font-medium transition">Envoyer</button>
                    </div>
                </div>
            </div>
        </main>

        <!-- Footer / Logs -->
        <footer class="apple-card p-4 flex flex-col h-28 overflow-hidden">
            <div class="text-xs font-semibold text-gray-400 border-b border-gray-100 pb-2 mb-2 flex justify-between">
                <span>ACTIVITÉ EN TEMPS RÉEL</span>
                <span id="log-count">1 entrée</span>
            </div>
            <div id="log-container" class="flex-grow overflow-y-auto space-y-1 text-xs text-gray-600 font-mono">
                <div>[00:00:00] Initialisation du système J.A.R.V.I.S. en mode Apple Premium.</div>
            </div>
        </footer>

        <script>
            let voiceEnabled = false;
            let logCount = 1;

            function updateClock() {
                const now = new Date();
                document.getElementById('clock').innerText = now.toTimeString().split(' ')[0];
            }
            setInterval(updateClock, 1000);

            function addLog(message) {
                const container = document.getElementById('log-container');
                const time = new Date().toTimeString().split(' ')[0];
                const div = document.createElement('div');
                div.innerHTML = `<span class="text-blue-600">[${time}]</span> ${message}`;
                container.appendChild(div);
                container.scrollTop = container.scrollHeight;
                logCount++;
                document.getElementById('log-count').innerText = logCount + ' entrées';
            }

            function speakJarvis(text) {
                document.getElementById('status-text').innerText = `"${text}"`;
                addLog(`JARVIS: ${text}`);
                if (voiceEnabled && 'speechSynthesis' in window) {
                    const utterance = new SpeechSynthesisUtterance(text);
                    utterance.lang = 'fr-FR';
                    utterance.pitch = 0.95;
                    utterance.rate = 1.0;
                    window.speechSynthesis.speak(utterance);
                }
            }

            function toggleVoice() {
                voiceEnabled = !voiceEnabled;
                const btn = document.getElementById('voice-btn');
                btn.innerText = voiceEnabled ? "Voix: ON" : "Voix: OFF";
                btn.classList.toggle('bg-blue-600', voiceEnabled);
                btn.classList.toggle('text-white', voiceEnabled);
                btn.classList.toggle('bg-gray-100', !voiceEnabled);
                btn.classList.toggle('text-gray-800', !voiceEnabled);
                speakJarvis(voiceEnabled ? "Module vocal activé." : "Module vocal désactivé.");
            }

            function runDiagnostics() {
                addLog("Diagnostic Apple/Stark en cours...");
                document.getElementById('cpu-load').innerText = (Math.random() * 15 + 10).toFixed(1) + '%';
                document.getElementById('ram-load').innerText = (Math.random() * 5 + 35).toFixed(1) + '%';
                speakJarvis("Diagnostics terminés. Intégrité du système à 100%.");
            }

            function triggerProtocol(name) {
                fetch('/api/protocol', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({protocol: name})
                })
                .then(res => res.json())
                .then(data => {
                    speakJarvis(data.message);
                });
            }

            function askJarvis(promptText) {
                if (!promptText) return;
                addLog(`Utilisateur: ${promptText}`);
                fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: promptText})
                })
                .then(res => res.json())
                .then(data => {
                    speakJarvis(data.response);
                });
            }

            function sendPrompt() {
                const input = document.getElementById('command-input');
                const val = input.value.trim();
                if (val) {
                    askJarvis(val);
                    input.value = '';
                }
            }

            function handleKey(e) {
                if (e.key === 'Enter') {
                    sendPrompt();
                }
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route("/api/protocol", methods=["POST"])
def api_protocol():
    data = request.get_json() or {}
    proto = data.get("protocol", "").lower()
    msg = PROTOCOLS.get(proto, f"Protocole '{proto}' exécuté avec succès, Monsieur.")
    return jsonify({"status": "success", "message": msg})

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json() or {}
    prompt = data.get("prompt", "").lower()
    
    if "bonjour" in prompt or "salut" in prompt:
        resp = "Bonjour Monsieur. Comment puis-je vous aider dans votre espace de travail ?"
    elif "merci" in prompt:
        resp = "Toujours un plaisir, Monsieur."
    elif "armure" in prompt:
        resp = "Les armures sont stockées et sécurisées dans le vault."
    else:
        resp = random.choice(RESPONSES)
        
    return jsonify({"status": "success", "response": resp})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
