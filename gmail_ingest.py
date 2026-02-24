import os
import pickle
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import requests
import json
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
HUB_URL = "https://regenesis-hub-v8-510958561702.us-central1.run.app/api/ingest-emails"

def get_gmail_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

def fetch_recent_emails(service, max_results=20):
    results = service.users().messages().list(userId='me', maxResults=max_results, q='after:2026/01/01').execute()
    messages = results.get('messages', [])
    
    emails = []
    for msg in messages[:10]:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
        
        headers = msg_data['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
        
        # Look for payment-related emails
        is_payment = any(k in subject.lower() for k in ['payment', 'receipt', 'invoice', 'sold', 'sale', 'paypal', 'stripe', 'etsy', 'ebay'])
        
        emails.append({
            'id': msg['id'],
            'subject': subject,
            'sender': sender,
            'date': date,
            'is_payment': is_payment,
            'snippet': msg_data['snippet']
        })
    
    return emails

def send_to_hub(emails):
    try:
        response = requests.post(HUB_URL, json={
            'emails': emails,
            'timestamp': datetime.now().isoformat(),
            'source': 'gmail_api'
        })
        return response.json()
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    try:
        print("📧 Connecting to Gmail...")
        service = get_gmail_service()
        
        print("📨 Fetching recent emails...")
        emails = fetch_recent_emails(service)
        
        print(f"✅ Found {len(emails)} emails. Sending to hub...")
        result = send_to_hub(emails)
        
        print(f"📤 Hub response: {result}")
        
        payment_emails = [e for e in emails if e['is_payment']]
        if payment_emails:
            print("\n💰 PAYMENT EMAILS FOUND:")
            for e in payment_emails:
                print(f"  • {e['subject']} - {e['sender']}")
                
    except Exception as e:
        import traceback
        import requests
        error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        print(f"❌ ERROR: {error_msg}")
        
        # Report to hub error endpoint
        try:
            requests.post("http://10.88.0.3:8080/api/log-error", json={
                'script': 'gmail_ingest.py',
                'error': error_msg,
                'context': {
                    'stage': 'main_execution',
                    'error_type': type(e).__name__
                }
            })
            print("📤 Error reported to hub")
        except:
            print("❌ Could not report error to hub")
