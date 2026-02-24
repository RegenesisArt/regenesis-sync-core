from flask import Flask, request, jsonify
from simple_agent import CMHP_Agent

app = Flask(__name__)
agent = CMHP_Agent()

@app.route('/v1/ai-query', methods=['POST'])
def ai_query():
    query = request.json.get('query', '')
    response = agent.process_query(query)
    return jsonify({'response': response})

if __name__ == '__main__':
    print('AI Server: http://localhost:5001/v1/ai-query')
    app.run(port=5001, debug=False)
