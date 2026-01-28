from flask import Flask, request, jsonify, render_template_string
import json
from datetime import datetime

app = Flask(__name__)

# Simple in-memory store
ARTWORK_DB = {}

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
    # Store artwork if it's a creation event
    if log_data.get('system') == 'CMHP' and log_data.get('event') == 'artwork_record_created':
        art_id = log_data.get('artwork_id')
        if art_id:
            ARTWORK_DB[art_id] = log_data
    # Append to log file
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
    # Load GQ-001 from logs if not in memory
    if 'GQ-001' not in ARTWORK_DB:
        try:
            with open('session_log.txt', 'r') as f:
                for line in f:
                    log = json.loads(line.strip())
                    if log.get('artwork_id') == 'GQ-001' and log.get('event') == 'artwork_record_created':
                        ARTWORK_DB['GQ-001'] = log
                        break
        except:
            pass
    
    # Default data
    artwork = ARTWORK_DB.get('GQ-001', {})
    title = artwork.get('title', 'Custom Pet Portrait (Dog)')
    status = artwork.get('status', 'canvas_prep')
    apv = artwork.get('current_apv', 20.0)
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Regenesis Art - Sovereign Dashboard</title>
        <style>
            body {{ font-family: sans-serif; margin: 20px; background: #f5f5f5; }}
            .artwork {{ background: white; padding: 20px; margin: 15px 0; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
            .artwork-id {{ font-weight: bold; color: #333; font-size: 1.2em; }}
            .artwork-title {{ color: #666; margin: 8px 0; }}
            .artwork-status {{ display: inline-block; padding: 4px 10px; border-radius: 4px; font-size: 0.9em; }}
            .status-prep {{ background: #fff3cd; color: #856404; }}
            .status-painting {{ background: #d1ecf1; color: #0c5460; }}
            .status-done {{ background: #d4edda; color: #155724; }}
            button {{ background: #007bff; color: white; border: none; padding: 10px 18px; border-radius: 5px; cursor: pointer; margin: 8px; font-size: 1em; }}
            button:hover {{ background: #0056b3; }}
            button:disabled {{ background: #ccc; cursor: not-allowed; }}
            .apv {{ font-size: 1.5em; color: #28a745; font-weight: bold; }}
            .timestamp {{ font-size: 0.9em; color: #999; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <h1>🕹️ Sovereign Dashboard</h1>
        <p>Manage your Genesis Quest and log work sessions.</p>
        
        <div class="artwork">
            <div class="artwork-id">GQ-001</div>
            <div class="artwork-title">{title}</div>
            <div>Status: <span class="artwork-status status-{status}">{status}</span></div>
            <div>APV: <span class="apv">${apv}</span></div>
            <div>
                <button onclick="startWork('GQ-001')" { 'disabled' if status == 'painting' else '' }>Start Painting</button>
                <button onclick="stopWork('GQ-001')" { 'disabled' if status != 'painting' else '' }>Stop Painting</button>
                <button onclick="logAPV('GQ-001')">Log $20 APV</button>
            </div>
            <div class="timestamp">Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</div>
        </div>
        
        <div id="message" style="margin-top:20px; padding:12px; border-radius:5px; display:none;"></div>
        
        <script>
            function showMessage(msg, isError = false) {{
                const div = document.getElementById('message');
                div.innerHTML = msg;
                div.style.display = 'block';
                div.style.background = isError ? '#f8d7da' : '#d1ecf1';
                setTimeout(() => div.style.display = 'none', 4000);
            }}
            
            async function startWork(artworkId) {{
                const response = await fetch('/api/start-work', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{artwork_id: artworkId}})
                }});
                const result = await response.json();
                showMessage(result.message);
                setTimeout(() => location.reload(), 1500);
            }}
            
            async function stopWork(artworkId) {{
                const response = await fetch('/api/stop-work', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{artwork_id: artworkId}})
                }});
                const result = await response.json();
                showMessage(result.message);
                setTimeout(() => location.reload(), 1500);
            }}
            
            async function logAPV(artworkId) {{
                const response = await fetch('/log', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        system: 'CMHP',
                        event: 'artwork_status_update',
                        artwork_id: artworkId,
                        update: {{
                            status: 'work_logged',
                            apv_addition: 20.00,
                            hours_addition: 0.1,
                            note: 'APV logged from dashboard'
                        }}
                    }})
                }});
                const result = await response.json();
                showMessage('APV $20 logged: ' + result.status);
                setTimeout(() => location.reload(), 1500);
            }}
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/api/start-work', methods=['POST'])
def start_work():
    data = request.get_json()
    artwork_id = data.get('artwork_id')
    if not artwork_id:
        return jsonify({'error': 'No artwork ID'}), 400
    ARTWORK_DB[artwork_id] = ARTWORK_DB.get(artwork_id, {})
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
    if not artwork_id:
        return jsonify({'error': 'No artwork ID'}), 400
    ARTWORK_DB[artwork_id] = ARTWORK_DB.get(artwork_id, {})
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
