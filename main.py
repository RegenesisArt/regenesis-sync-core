cat > main.py << 'EOF'
from flask import Flask, request, jsonify, render_template_string
import json
import os
from datetime import datetime

app = Flask(__name__)

# In-memory database
ARTWORK_DB = {}

def load_existing_logs():
    try:
        with open('session_log.txt', 'r') as f:
            for line in f:
                log_entry = json.loads(line.strip())
                if log_entry.get('system') == 'CMHP':
                    if log_entry.get('event') == 'artwork_record_created':
                        art_id = log_entry.get('artwork_id')
                        if art_id:
                            ARTWORK_DB[art_id] = log_entry
                    elif log_entry.get('event') == 'artwork_status_update':
                        art_id = log_entry.get('artwork_id')
                        if art_id and art_id in ARTWORK_DB:
                            ARTWORK_DB[art_id].setdefault('updates', []).append(log_entry.get('update', {}))
    except FileNotFoundError:
        pass

load_existing_logs()

@app.route('/')
def home():
    return 'Sovereign Hub Online'

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

@app.route('/log', methods=['POST'])
def log_session():
    log_data = request.get_json()
    if not log_data:
        return jsonify({'error': 'No data provided'}), 400
    print(f"[CMHP LOG] {log_data}")
    if log_data.get('system') == 'CMHP' and log_data.get('event') == 'artwork_record_created':
        art_id = log_data.get('artwork_id')
        if art_id:
            ARTWORK_DB[art_id] = log_data
    with open('session_log.txt', 'a') as f:
        f.write(json.dumps(log_data) + '\n')
    return jsonify({'status': 'success', 'message': 'Session logged'}), 200

@app.route('/logs')
def get_logs():
    try:
        with open('session_log.txt', 'r') as f:
            logs = [json.loads(line.strip()) for line in f]
        return jsonify({'logs': logs, 'count': len(logs)})
    except FileNotFoundError:
        return jsonify({'logs': [], 'count': 0})

@app.route('/latest-session')
def latest_session():
    try:
        with open('session_log.txt', 'r') as f:
            lines = f.readlines()
            if lines:
                latest = json.loads(lines[-1].strip())
                return jsonify({'latest_session': latest, 'timestamp': datetime.utcnow().isoformat(), 'status': 'success'})
    except FileNotFoundError:
        pass
    return jsonify({'latest_session': None, 'status': 'no sessions found'})

@app.route('/dashboard')
def dashboard():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Regenesis Art - Sovereign Dashboard</title>
        <style>
            body { font-family: sans-serif; margin: 20px; background: #f5f5f5; }
            .artwork { background: white; padding: 15px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .artwork-id { font-weight: bold; color: #333; }
            .artwork-title { color: #666; margin: 5px 0; }
            .artwork-status { display: inline-block; padding: 3px 8px; border-radius: 3px; font-size: 0.9em; }
            .status-prep { background: #fff3cd; color: #856404; }
            .status-painting { background: #d1ecf1; color: #0c5460; }
            .status-done { background: #d4edda; color: #155724; }
            button { background: #007bff; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; margin: 5px; }
            button:hover { background: #0056b3; }
            button:disabled { background: #ccc; cursor: not-allowed; }
            .apv { font-size: 1.2em; color: #28a745; font-weight: bold; }
            .timestamp { font-size: 0.8em; color: #999; }
        </style>
    </head>
    <body>
        <h1>🕹️ Sovereign Dashboard</h1>
        <p>Manage your artworks and log work sessions.</p>
        
        <div id="artworks-list">
            <p>Loading artworks...</p>
        </div>
        
        <div id="log-result" style="margin-top:20px; padding:10px; background:#e9ecef; border-radius:5px; display:none;"></div>
        
        <script>
            async function loadArtworks() {
                const response = await fetch('/api/artworks');
                const data = await response.json();
                const container = document.getElementById('artworks-list');
                
                if (data.artworks.length === 0) {
                    container.innerHTML = '<p>No artworks found. Log one first.</p>';
                    return;
                }
                
                container.innerHTML = '';
                data.artworks.forEach(art => {
                    const statusClass = 'status-' + (art.status || 'prep').replace('_', '-');
                    const div = document.createElement('div');
                    div.className = 'artwork';
                    div.innerHTML = `
                        <div class="artwork-id">${art.artwork_id}</div>
                        <div class="artwork-title">${art.title || 'Untitled'}</div>
                        <div>Status: <span class="artwork-status ${statusClass}">${art.status || 'prep'}</span></div>
                        <div>APV: <span class="apv">$${art.current_apv || 0}</span></div>
                        <div>
                            <button onclick="startWork('${art.artwork_id}')" ${art.status === 'painting' ? 'disabled' : ''}>Start Painting</button>
                            <button onclick="stopWork('${art.artwork_id}')" ${art.status !== 'painting' ? 'disabled' : ''}>Stop Painting</button>
                            <button onclick="logAPV('${art.artwork_id}')">Log $20 APV</button>
                        </div>
                        <div class="timestamp">Last updated: ${new Date().toLocaleTimeString()}</div>
                    `;
                    container.appendChild(div);
                });
            }
            
            function showMessage(msg, isError = false) {
                const div = document.getElementById('log-result');
                div.innerHTML = msg;
                div.style.display = 'block';
                div.style.background = isError ? '#f8d7da' : '#d1ecf1';
                setTimeout(() => div.style.display = 'none', 5000);
            }
            
            async function startWork(artworkId) {
                const response = await fetch('/api/start-work', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({artwork_id: artworkId})
                });
                const result = await response.json();
                showMessage(result.message);
                loadArtworks();
            }
            
            async function stopWork(artworkId) {
                const response = await fetch('/api/stop-work', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({artwork_id: artworkId})
                });
                const result = await response.json();
                showMessage(result.message);
                loadArtworks();
            }
            
            async function logAPV(artworkId) {
                const response = await fetch('/log', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        system: 'CMHP',
                        event: 'artwork_status_update',
                        artwork_id: artworkId,
                        update: {
                            status: 'work_logged',
                            apv_addition: 20.00,
                            hours_addition: 0.1,
                            note: 'Manual APV log from dashboard'
                        }
                    })
                });
                const result = await response.json();
                showMessage('APV $20 logged: ' + result.status);
                loadArtworks();
            }
            
            // Load artworks on page load
            loadArtworks();
            // Refresh every 30 seconds
            setInterval(loadArtworks, 30000);
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/api/artworks')
def list_artworks():
    artworks = []
    for art_id, art_data in ARTWORK_DB.items():
        artworks.append({
            'artwork_id': art_id,
            'title': art_data.get('title', ''),
            'status': art_data.get('status', 'prep'),
            'current_apv': art_data.get('current_apv', 0)
        })
    return jsonify({'artworks': artworks})

@app.route('/api/start-work', methods=['POST'])
def start_work():
    data = request.get_json()
    artwork_id = data.get('artwork_id')
    if not artwork_id or artwork_id not in ARTWORK_DB:
        return jsonify({'error': 'Artwork not found'}), 404
    ARTWORK_DB[artwork_id]['status'] = 'painting'
    log_entry = {
        'system': 'CMHP',
        'event': 'work_session_started',
        'artwork_id': artwork_id,
        'timestamp': datetime.utcnow().isoformat()
    }
    with open('session_log.txt', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    return jsonify({'status': 'success', 'message': f'Started work on {artwork_id}'})

@app.route('/api/stop-work', methods=['POST'])
def stop_work():
    data = request.get_json()
    artwork_id = data.get('artwork_id')
    if not artwork_id or artwork_id not in ARTWORK_DB:
        return jsonify({'error': 'Artwork not found'}), 404
    ARTWORK_DB[artwork_id]['status'] = 'underpainting_completed'
    log_entry = {
        'system': 'CMHP',
        'event': 'work_session_stopped',
        'artwork_id': artwork_id,
        'timestamp': datetime.utcnow().isoformat()
    }
    with open('session_log.txt', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    return jsonify({'status': 'success', 'message': f'Stopped work on {artwork_id}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
EOF
