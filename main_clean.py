import functions_framework
from flask import jsonify, request
import json
from datetime import datetime

artworks_db = {}
financial_db = {
    "the_key": {"target": 6000, "current": 0},
    "freedom_fuel": {"target": 10000, "current": 0},
    "apv_total": 0,
    "micro_investments": 50
}

@functions_framework.http
def regenesis_hub(request):
    path = request.path
    method = request.method
    
    if path in ['/', '']:
        return jsonify({
            "system": "CMHP Agent",
            "protocol_memory": "active",
            "handoff_elimination": "complete",
            "timestamp": datetime.now().isoformat()
        })
    
    elif path == '/v1/dashboard':
        return jsonify({
            "dashboard": {
                "status": "live",
                "apv": 70,
                "target": 6000,
                "days": 216
            }
        })
    
    elif path == '/v1/ai-query' and method == 'POST':
        try:
            data = request.get_json()
            query = data.get('query', '')
            from simple_agent import CMHP_Agent
            agent = CMHP_Agent()
            response = agent.process_query(query)
            return jsonify({'response': response})
        except Exception as e:
            return jsonify({'response': f'Error: {str(e)}'})
    
    else:
        return jsonify({"error": "Endpoint not found"}), 404

if __name__ == "__main__":
    print("CMHP Agent ready")
