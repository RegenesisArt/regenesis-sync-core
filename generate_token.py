import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            print("\n" + "="*50)
            print("OPEN THIS URL IN YOUR BROWSER:")
            print("="*50)
            print(auth_url)
            print("="*50 + "\n")
            
            code = input("Enter the authorization code from the URL: ")
            flow.fetch_token(code=code)
            creds = flow.credentials
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    print("\n✅ Token generated successfully!")
    print(f"Refresh token: {creds.refresh_token}")

if __name__ == '__main__':
    main()
