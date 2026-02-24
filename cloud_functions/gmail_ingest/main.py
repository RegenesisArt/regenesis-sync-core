import requests
import base64
from google.cloud import firestore
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import json
from datetime import datetime

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

HUB_URL = "https://regenesis-hub-v8-510958561702.us-central1.run.app/api/ingest-emails"

def get_gmail_service():
    """Get Gmail API service"""
    creds = None
    
    # Check if we have token
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If no valid credentials, let's use the one from environment
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # For Cloud Function, we'll need to pass credentials differently
            # This is a placeholder - we'll need to set up OAuth properly
            return None
    
    service = build('gmail', 'v1', credentials=creds)
    return service

def fetch_recent_emails(service, max_results=20):
    """Fetch recent emails"""
    try:
        results = service.users().messages().list(userId='me', maxResults=max_results).execute()
        messages = results.get('messages', [])
        
        emails = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            
            # Extract headers
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Check if it's a payment email
            is_payment = any(keyword in subject.lower() for keyword in 
                           ['payment', 'receipt', 'invoice', 'sold', 'transaction', 'paypal', 'stripe'])
            
            emails.append({
                'id': message['id'],
                'subject': subject,
                'sender': sender,
                'date': date,
                'is_payment': is_payment,
                'snippet': msg['snippet']
            })
        
        return emails
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return []

def send_to_hub(emails):
    """Send emails to hub"""
    try:
        response = requests.post(HUB_URL, json={
            'emails': emails,
            'timestamp': datetime.now().isoformat(),
            'source': 'gmail_cloud_function'
        })
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def gmail_ingest(request):
    """Cloud Function entry point"""
    try:
        print("📧 Connecting to Gmail...")
        service = get_gmail_service()
        
        if not service:
            return {"error": "Could not authenticate with Gmail"}, 500
        
        print("📨 Fetching recent emails...")
        emails = fetch_recent_emails(service)
        
        print(f"✅ Found {len(emails)} emails. Sending to hub...")
        result = send_to_hub(emails)
        
        payment_emails = [e for e in emails if e['is_payment']]
        
        return {
            "status": "success",
            "emails_found": len(emails),
            "payment_emails": len(payment_emails),
            "hub_response": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        import traceback
        error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        print(f"❌ ERROR: {error_msg}")
        
        # Report error
        try:
            requests.post("https://regenesis-hub-v8-510958561702.us-central1.run.app/api/log-error", json={
                'script': 'cloud_function_gmail_ingest',
                'error': error_msg,
                'context': {
                    'function': 'gmail_ingest',
                    'error_type': type(e).__name__
                }
            })
        except:
            pass
        
        return {"error": str(e)}, 500

# Add Flask wrapper for Cloud Run
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    """Handle HTTP requests to Cloud Run"""
    return jsonify(gmail_ingest(request))
