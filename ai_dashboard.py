#!/usr/bin/env python3
"""
AI-Powered Dashboard with Hand-off Elimination
"""
import json
import requests
from datetime import datetime
from flask import Flask, render_template_string, request

app = Flask(__name__)

# Your hub URL
HUB_URL = "https://us-central1-regenesis-art-hub.cloudfunctions.net/regenesis-hub-v1"
# Local AI server
AI_URL = "http://localhost:5001/v1/ai-query"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🤖 Regenesis AI Dashboard</title>
    <style>
        body { background: #000; color: #0f0; font-family: monospace; padding: 20px; }
        .dashboard { border: 2px solid #0f0; padding: 20px; margin-bottom: 20px; }
        .ai-section { border: 2px solid #00f; padding: 20px; }
        .chat { background: #111; height: 300px; overflow-y: auto; padding: 10px; }
        .user { color: #0ff; }
        .ai { color: #0f0; }
        input { width: 70%; background: #222; color: #0f0; border: 1px solid #0f0; padding: 10px; }
        button { background: #0a0; color: white; border: none; padding: 10px 20px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>🤖 REGENESIS AI DASHBOARD</h1>
        <p>APV: ${{ apv }}</p>
        <p>Funds: ${{ funds }}/$6000</p>
        <p>Days: {{ days }}</p>
    </div>
    
    <div class="ai-section">
        <h2>🤖 CMHP AI ASSISTANT</h2>
        <div class="chat" id="chat">
            <!-- Messages appear here -->
        </div>
        <input type="text" id="query" placeholder="Ask me anything about your business...">
        <button onclick="askAI()">Ask AI</button>
        <p><small>Hand-off elimination active. No more manual copying.</small></p>
    </div>
    
    <script>
    async function askAI() {
        const query = document.getElementById('query').value;
        if (!query) return;
        
        const chat = document.getElementById('chat');
        chat.innerHTML += `<div class="user"><strong>You:</strong> ${query}</div>`;
        
        const response = await fetch('/ai-query', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query: query})
        });
        
        const data = await response.json();
        chat.innerHTML += `<div class="ai"><strong>AI:</strong> ${data.response}</div>`;
        chat.scrollTop = chat.scrollHeight;
    }
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE, 
        apv=70, 
        funds=0, 
        days=216)

@app.route('/ai-query', methods=['POST'])
def ai_query():
    """Proxy to AI server"""
    try:
        query = request.json.get('query', '')
        response = requests.post(AI_URL, 
            json={'query': query},
            timeout=30)
        return response.json()
    except:
        return {'response': 'AI server not running. Start test_ai_server.py'}

if __name__ == '__main__':
    print("🤖 AI Dashboard: http://localhost:5000")
    print("⚡ Hand-off elimination ACTIVE")
    app.run(port=5000, debug=False)
