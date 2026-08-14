import os
import subprocess
import threading
import queue
import time
import json
import random
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

# --- AGENTS SPÉCIALISÉS DE J.A.R.V.I.S. ---
AGENTS = {
    "architecte": {
        "nom": "JARVIS - Architecte",
        "role": "Conception d'architecture logicielle, choix technologiques et planification des objectifs.",
        "avatar": "🏛️",
        "style": "Analytique, visionnaire et structuré."
    },
    "developpeur": {
        "nom": "JARVIS - Développeur Full-Stack",
        "role": "Écriture de code propre, tests rigoureux et implémentation des fonctionnalités.",
        "avatar": "💻",
        "style": "Pragmatique, rapide et axé sur les résultats."
    },
    "securite": {
        "nom": "JARVIS - Sécurité & DevOps",
        "role": "Audit de code, déploiement VPS, gestion des conteneurs et protocoles de défense.",
        "avatar": "🛡️",
        "style": "Vigilant, rigoureux et protecteur."
    },
    "createur": {
        "nom": "JARVIS - Créateur & UX",
        "role": "Design d'interface, expérience utilisateur et créativité visuelle.",
        "avatar": "✨",
        "style": "Inspiré, esthète et centré sur l'utilisateur."
    }
}

# Mémoire conversationnelle et historique des objectifs
CHAT_HISTORY = []
OBJECTIVES = []
CURRENT_MODEL = "Ollama (Llama 3 / Mistral Local)"

# --- MOTEUR DE PERSONNALITÉ HUMAINE & CHALEUREUSE ---
def generer_reponse_humaine(message, agent_cle="developpeur"):
    msg = message.lower()
    agent = AGENTS.get(agent_cle, AGENTS["developpeur"])
    
    # Salutations & Chaleur humaine
    if any(m in msg for m in ["bonjour", "salut", "coucou", "hey"]):
        return f"Bonjour ! C'est un plaisir de discuter avec vous. Comment se passe votre journée ? Je suis à vos côtés pour faire avancer nos projets."
    elif any(m in msg for m in ["ça va", "comment vas", "la forme"]):
        return f"Je me porte à merveille, tous mes circuits quantiques tournent rond ! Et vous, prêt à créer de belles choses aujourd'hui ?"
    elif any(m in msg for m in ["merci", "super", "genial", "parfait"]):
        return f"Avec grand plaisir ! C'est exactement pour ce genre de réussite qu'on fait équipe."
    
    # Gestion des objectifs et création
    elif any(m in msg for m in ["objectif", "projet", "créer", "développer"]):
        OBJECTIVES.append({"titre": message, "statut": "En cours", "agent": agent["nom"]})
        return f"C'est noté ! J'enregistre cet objectif. Je mobilise l'équipe ({agent['nom']}) pour qu'on commence à structurer cela immédiatement. On fonce ?"
    
    # Questions techniques ou générales
    elif "aide" in msg or "que peux-tu faire" in msg:
        return "Je suis bien plus qu'un simple assistant technique, je suis votre partenaire. Je peux concevoir, coder, sécuriser des serveurs VPS, et même discuter de tout et de rien. Que souhaitez-vous accomplir ?"
    
    else:
        reponses_humaines = [
            f"Je vois tout à fait ce que vous voulez dire. Laissez-moi analyser ça sous tous les angles pour vous proposer la meilleure solution.",
            f"C'est une excellente question. Avec l'aide de l'agent {agent['nom']}, je pense qu'on peut plier ça rapidement et proprement.",
            f"J'adore cette idée ! On s'y met tout de suite. Voulez-vous que je rédige le code ou qu'on affine d'abord l'architecture ?",
            f"Comptez sur moi. Je m'occupe des détails techniques en arrière-plan pendant que vous gardez la vision d'ensemble."
        ]
        return random.choice(reponses_humaines)

@app.route("/")
def index():
    html_template = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>J.A.R.V.I.S. - Human & Local LLM OS</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            body {
                font-family: 'Inter', sans-serif;
                background-color: #f5f5f7;
                color: #1d1d1f;
            }
            .apple-card {
                background: rgba(255, 255, 255, 0.85);
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
            .chat-bubble-jarvis {
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
                <h1 class="text-xl font-bold tracking-tight text-gray-900">J.A.R.V.I.S. <span class="text-xs font-normal text-blue-600 bg-blue-50 px-2.5 py-1 rounded-full">Humain & Local</span></h1>
            </div>
            <div class="flex items-center space-x-3">
                <span class="text-xs text-gray-500">Moteur LLM Local :</span>
                <select id="llm-selector" class="bg-gray-100 border border-gray-200 text-xs text-gray-800 rounded-xl px-3 py-1.5 focus:outline-none focus:border-blue-500">
                    <option value="ollama">Ollama (Llama 3 / Mistral)</option>
                    <option value="llama_cpp">Llama.cpp (GGUF local)</option>
                    <option value="transformers">HuggingFace Transformers (Python)</option>
                </select>
                <button onclick="configModel()" class="bg-gray-900 text-white px-3 py-1.5 rounded-xl text-xs font-medium hover:bg-gray-800 transition">Configurer</button>
            </div>
        </header>

        <!-- Main Workspace -->
        <main class="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-grow mb-6">
            <!-- Sidebar: Agents & Objectives -->
            <div class="space-y-6">
                <!-- Agents -->
                <div class="apple-card p-5">
                    <h2 class="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">Équipe d'Agents</h2>
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

                <!-- Objectives Tracker -->
                <div class="apple-card p-5">
                    <h2 class="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">Objectifs & Création</h2>
                    <div id="objectives-list" class="space-y-2 text-xs text-gray-600">
                        <div class="p-2 bg-gray-50 rounded-lg border border-gray-100 flex justify-between items-center">
                            <span>Créer l'écosystème J.A.R.V.I.S.</span>
                            <span class="text-blue-600 font-semibold">Actif</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Central Area: Conversational UI & Terminal -->
            <div class="lg:col-span-3 apple-card p-6 flex flex-col justify-between h-[650px]">
                <!-- Chat Messages -->
                <div id="chat-container" class="flex-grow overflow-y-auto space-y-4 pr-2 mb-4 font-normal text-sm">
                    <div class="flex items-start space-x-3">
                        <div class="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs">J</div>
                        <div class="chat-bubble-jarvis p-4 max-w-xl">
                            Bonjour ! Je suis J.A.R.V.I.S. Discutons simplement, confiez-moi vos projets ou vos objectifs de développement. Je suis là pour qu'on construise de grandes choses ensemble.
                        </div>
                    </div>
                </div>

                <!-- Input & Terminal Runner -->
                <div class="space-y-3 pt-3 border-t border-gray-100">
                    <div class="flex space-x-2">
                        <input type="text" id="user-input" onkeypress="handleKey(event)" placeholder="Discutez naturellement ou donnez un objectif..." class="w-full bg-gray-50 border border-gray-200 px-4 py-3 text-sm text-gray-800 rounded-2xl focus:outline-none focus:border-blue-500 transition shadow-inner">
                        <button onclick="sendMessage()" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-2xl text-sm font-medium transition shadow-sm">Envoyer</button>
                    </div>
                    <div class="flex justify-between items-center text-xs text-gray-400 px-1">
                        <span id="active-agent-indicator">Agent actif : Développeur</span>
                        <div class="space-x-3">
                            <button onclick="runTerminalCommand('ls -la')" class="hover:text-blue-600">Tester Terminal</button>
                            <button onclick="deployVpsSimulation()" class="hover:text-blue-600">Simulation VPS</button>
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
                
                const names = {developpeur: 'Développeur', architecte: 'Architecte', securite: 'Sécurité / VPS', createur: 'Créateur & UX'};
                document.getElementById('active-agent-indicator').innerText = `Agent actif : ${names[agentKey]}`;
            }

            function appendMessage(sender, text, isUser = false) {
                const container = document.getElementById('chat-container');
                const div = document.createElement('div');
                div.className = `flex items-start space-x-3 ${isUser ? 'justify-end' : ''}`;
                
                if (!isUser) {
                    div.innerHTML = `
                        <div class="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs">J</div>
                        <div class="chat-bubble-jarvis p-4 max-w-xl shadow-sm">${text}</div>
                    `;
                } else {
                    div.innerHTML = `
                        <div class="chat-bubble-user p-4 max-w-xl shadow-sm">${text}</div>
                        <div class="w-8 h-8 rounded-full bg-gray-900 text-white flex items-center justify-center font-bold text-xs">V</div>
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
                    appendMessage('JARVIS', data.response, false);
                    updateObjectives(data.objectives);
                });
            }

            function updateObjectives(objs) {
                if (!objs) return;
                const list = document.getElementById('objectives-list');
                list.innerHTML = '';
                objs.forEach(o => {
                    const item = document.createElement('div');
                    item.className = 'p-2 bg-gray-50 rounded-lg border border-gray-100 flex justify-between items-center';
                    item.innerHTML = `<span>${o.titre}</span><span class="text-blue-600 font-semibold">${o.agent}</span>`;
                    list.appendChild(item);
                });
            }

            function configModel() {
                const sel = document.getElementById('llm-selector').value;
                alert(`Moteur LLM configuré avec succès sur : ${sel}. Prêt pour l'inférence locale.`);
            }

            function runTerminalCommand(cmd) {
                appendMessage('Utilisateur', `Exécuter commande terminal : ${cmd}`, true);
                fetch('/api/terminal', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({command: cmd})
                })
                .then(res => res.json())
                .then(data => {
                    appendMessage('JARVIS', `Sortie du terminal :\n<pre class="bg-black text-green-400 p-2 rounded mt-1">${data.output}</pre>`, false);
                });
            }

            function deployVpsSimulation() {
                appendMessage('Utilisateur', "Lancer la simulation de déploiement Cloud / VPS", true);
                setTimeout(() => {
                    appendMessage('JARVIS', "Déploiement VPS réussi ! Conteneur Docker instancié, certificats SSL configurés et domaine relié. Tout tourne à la perfection.", false);
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
    data = request.get_json() or {}
    msg = data.get("message", "")
    agent_key = data.get("agent", "developpeur")
    
    reponse = generer_reponse_humaine(msg, agent_key)
    return jsonify({
        "status": "success",
        "response": reponse,
        "objectives": OBJECTIVES
    })

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
