#!/usr/bin/env python3
"""
CMHP AI Agent - Eliminates manual hand-offs
"""
import json
import sqlite3
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class CMHP_Agent:
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.memory_db = "agent_memory.db"
        self.init_memory()
        
    def init_memory(self):
        conn = sqlite3.connect(self.memory_db)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS conversations 
            (id INTEGER PRIMARY KEY, timestamp TEXT, query TEXT, 
             response TEXT, agent_used TEXT)
        ''')
        conn.close()
        
    def call_deepseek(self, query):
        if not self.api_key:
            return "API key not set."
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Force English + business context
        prompt = f"""You are the CMHP AI Agent managing an art business for Daniel Felder.
        Context: Art business, $6,000 goal, APV tracking, eBay sales.
        Always respond in English.
        
        Query: {query}"""
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        
        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            return f"Error: {str(e)[:50]}"
    
    def process_query(self, query):
        print(f"Agent processing: {query}")
        response = self.call_deepseek(query)
        
        conn = sqlite3.connect(self.memory_db)
        conn.execute('''
            INSERT INTO conversations (timestamp, query, response, agent_used)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now().isoformat(), query, response, "deepseek"))
        conn.commit()
        conn.close()
        
        return response

if __name__ == "__main__":
    agent = CMHP_Agent()
    print("🤖 Agent test:", agent.process_query("What is APV?"))
