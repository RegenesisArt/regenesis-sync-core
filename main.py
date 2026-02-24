from flask import Flask, render_template, jsonify, request
from datetime import datetime
from google.cloud import firestore
from email_notifier import EmailNotifier
import os
import json

# Initialize Flask
application = Flask(__name__)

# Initialize Firestore with explicit project and error handling
try:
    # Initialize Firestore with explicit project ID
    print("Attempting to connect to Firestore...")
    db = firestore.Client(project='regenesis-art-hub')
    # Test connection by trying to list collections
    collections = list(db.collections())
    print(f"✅ Firestore connected successfully. Found {len(collections)} collections.")
except Exception as e:
    print(f"⚠️ Firestore connection failed: {e}")
    print("Using in-memory fallback - some features may not work")
    db = None

# Collection names
COLLECTION_EMAIL = 'email_ingestion'
COLLECTION_PAYMENT = 'payment_history'
COLLECTION_INSTAGRAM = 'instagram_data'
COLLECTION_EBAY = 'ebay_data'
COLLECTION_ARTWORKS = 'artworks'
COLLECTION_GENESIS = 'genesis_quest'

# ========== HELPER FUNCTIONS ==========
def save_to_firestore(collection, data):
    """Save data to Firestore with auto-ID"""
    doc_ref = db.collection(collection).document()
    doc_ref.set({
        **data,
        'stored_at': datetime.now().isoformat()
    })
    return doc_ref.id

def get_latest_state():
    """Aggregate latest state from all collections"""
    state = {
        'timestamp': datetime.now().isoformat(),
        'email_ingestion': {'total_processed': 0, 'last_batch': []},
        'financial': {
            'the_key': {'current': 0, 'target': 6000},
            'freedom_fuel': {'current': 0, 'target': 10000},
            'apv_total': 0
        },
        'genesis_quest': {
            'status': 'selection_pending',
            'phase': 1,
            'hours_logged': 0,
            'apv_accrued': 0
        },
        'artworks': {'total': 0, 'in_progress': 0, 'completed': 0}
    }
    
    # Get latest 5 emails
    emails = db.collection(COLLECTION_EMAIL).order_by('stored_at', direction=firestore.Query.DESCENDING).limit(5).stream()
    state['email_ingestion']['last_batch'] = []
    for e in emails:
        data = e.to_dict()
        # Remove internal fields for display
        if 'stored_at' in data:
            del data['stored_at']
        state['email_ingestion']['last_batch'].append(data)
    
    # Count total emails
    email_count = len(list(db.collection(COLLECTION_EMAIL).stream()))
    state['email_ingestion']['total_processed'] = email_count
    
    # Calculate total payments (The Key)
    payments = db.collection(COLLECTION_PAYMENT).stream()
    total_key = 0
    for p in payments:
        total_key += p.to_dict().get('amount', 0)
    state['financial']['the_key']['current'] = total_key
    
    # Get genesis quest status (if any)
    genesis_docs = db.collection(COLLECTION_GENESIS).order_by('stored_at', direction=firestore.Query.DESCENDING).limit(1).stream()
    for g in genesis_docs:
        state['genesis_quest'] = g.to_dict()
        if 'stored_at' in state['genesis_quest']:
            del state['genesis_quest']['stored_at']

    # Get eBay research summary
    try:
        ebay_items = db.collection('ebay_research').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(10).stream()
        state['ebay_research'] = []
        for item in ebay_items:
            data = item.to_dict()
            state['ebay_research'].append({
                'title': data.get('title', 'Unknown'),
                'sold_price': data.get('sold_price', 0),
                'timestamp': data.get('timestamp', '')
            })
    except Exception as e:
        print(f"⚠️ Could not fetch eBay data: {e}")
        state['ebay_research'] = []

    return state
# ========== ROUTES ==========

@application.route('/')
@application.route('/health')
def health_check():
    return jsonify({
        "system": "Regenesis Hub V8.0",
        "status": "operational",
        "api": "available at /api/dashboard",
        "instagram_api": "available at /api/instagram/media and /api/instagram/insights",
        "timestamp": datetime.now().isoformat()
    })

@application.route('/api/ingest-emails', methods=['POST'])
def api_ingest_emails():
    try:
        data = request.get_json()
        emails = data.get('emails', [])
        for email in emails:
            save_to_firestore(COLLECTION_EMAIL, email)
        return jsonify({
            "status": "success",
            "received": len(emails),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@application.route('/api/update-key', methods=['POST'])
def api_update_key():
    try:
        data = request.get_json()
        amount = data.get('amount', 0)
        
        payment_record = {
            'amount': amount,
            'platform': data.get('platform', 'unknown'),
            'subject': data.get('subject', ''),
            'source': data.get('source', 'api')
        }
        save_to_firestore(COLLECTION_PAYMENT, payment_record)
        
        # Recalculate current total
        payments = db.collection(COLLECTION_PAYMENT).stream()
        total = sum(p.to_dict().get('amount', 0) for p in payments)
        
        return jsonify({
            "status": "success",
            "the_key_current": total,
            "the_key_remaining": 6000 - total,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@application.route('/api/instagram-data', methods=['POST'])
def api_instagram_data():
    try:
        data = request.get_json()
        save_to_firestore(COLLECTION_INSTAGRAM, data.get('data', {}))
        return jsonify({
            "status": "success",
            "received": True,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@application.route('/api/instagram/media', methods=['GET'])
def get_instagram_media():
    """Get recent Instagram media"""
    try:
        media = db.collection(COLLECTION_INSTAGRAM).order_by('stored_at', direction=firestore.Query.DESCENDING).limit(10).stream()
        results = []
        for item in media:
            data = item.to_dict()
            if 'stored_at' in data:
                del data['stored_at']
            results.append(data)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@application.route('/api/instagram/insights', methods=['GET'])
def get_instagram_insights():
    """Get Instagram insights/aggregates"""
    try:
        all_posts = list(db.collection(COLLECTION_INSTAGRAM).stream())
        insights = {
            "total_posts": len(all_posts),
            "latest": []
        }
        if all_posts:
            latest = all_posts[0].to_dict()
            if 'stored_at' in latest:
                del latest['stored_at']
            insights['latest'] = latest
        return jsonify(insights)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@application.route('/api/ebay-data', methods=['POST'])
def api_ebay_data():
    try:
        data = request.get_json()
        save_to_firestore(COLLECTION_EBAY, data.get('data', {}))
        return jsonify({
            "status": "success",
            "received": True,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@application.route('/api/ebay/research', methods=['GET'])
def get_ebay_research():
    """Get eBay research data"""
    try:
        # Query eBay research collection
        research = db.collection('ebay_research').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(20).stream()
        results = []
        for item in research:
            data = item.to_dict()
            # Convert timestamp to string if it exists
            if 'timestamp' in data and hasattr(data['timestamp'], 'isoformat'):
                data['timestamp'] = data['timestamp'].isoformat()
            results.append(data)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e), "details": "Check if 'ebay_research' collection exists"}), 500

@application.route('/api/command', methods=['POST'])
def api_command():
    data = request.get_json() or {}
    command = data.get('command', '').lower()
    
    responses = {
        'cycle subjects': {
            "response": """Generating 3 UNFILTERED COMMERCIAL suggestions...
            
1. 🐕 Custom Pet Portrait (Golden Retriever)
   • Tier: 1 | Target: $75-100
   • Market: High demand on eBay
   • ETC: 2-3 hours
            
2. 🏔️ Mountain Landscape at Sunset
   • Tier: 2 | Target: $450-600  
   • Market: Consistent collector interest
   • ETC: 8-10 hours
            
3. 🔺 Abstract Geometric Pattern
   • Tier: 1 | Target: $60-80
   • Market: Modern decor trend
   • ETC: 3-4 hours
            
Command: 'Accept subject #[1-3]'"""
        }
    }
    
    if command in responses:
        return jsonify(responses[command])
    else:
        return jsonify({
            "response": f"Processing: '{command}'"
        })

@application.route('/state/latest')
def state_latest():
    """Get latest system state from Firestore"""
    try:
        state = get_latest_state()
        return jsonify(state)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@application.route('/api/dashboard')
def api_dashboard():
    """Dashboard API endpoint"""
    try:
        state = get_latest_state()
        return jsonify({
            "dashboard": {
                "status": "live",
                "timestamp": datetime.now().isoformat(),
                "metrics": {
                    "hub": "online",
                    "emails_processed": state['email_ingestion']['total_processed'],
                    "the_key_current": state['financial']['the_key']['current'],
                    "genesis_status": state['genesis_quest']['status']
                }
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@application.route('/dashboard')
def dashboard():
    """Serve the web dashboard"""
    return render_template('dashboard.html')


# ========== WEEKLY SUMMARY ENDPOINT ==========
from datetime import timedelta

@application.route('/api/summary/weekly')
def weekly_summary():
    """Generate a summary of the last 7 days"""
    try:
        # Calculate date 7 days ago
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        
        # Query emails from last 7 days
        emails_ref = db.collection('email_ingestion').where('stored_at', '>=', week_ago.isoformat())
        emails = list(emails_ref.stream())
        
        # Query payments from last 7 days
        payments_ref = db.collection('payment_history').where('stored_at', '>=', week_ago.isoformat())
        payments = list(payments_ref.stream())
        total_payments = sum(p.to_dict().get('amount', 0) for p in payments)
        
        # Get latest state for The Key total
        state = get_latest_state()
        the_key_current = state['financial']['the_key']['current']
        
        summary = {
            'week_start': week_ago.isoformat(),
            'week_end': now.isoformat(),
            'email_count': len(emails),
            'payments': {
                'count': len(payments),
                'total_amount': total_payments,
                'the_key_current': the_key_current,
                'the_key_remaining': 6000 - the_key_current
            },
            'genesis_quest': state['genesis_quest'],
            'timestamp': now.isoformat()
        }
        
        # Add Instagram summary if data exists
        insta_ref = db.collection('instagram_data').where('stored_at', '>=', week_ago.isoformat())
        insta_posts = list(insta_ref.stream())
        if insta_posts:
            summary['instagram'] = {'posts_count': len(insta_posts)}
        
        # Add eBay summary if data exists
        ebay_ref = db.collection('ebay_data').where('stored_at', '>=', week_ago.isoformat())
        ebay_data = list(ebay_ref.stream())
        if ebay_data:
            summary['ebay'] = {'research_runs': len(ebay_data)}
        
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ========== ERROR LOGGING ENDPOINT ==========
@application.route('/api/log-error', methods=['POST'])
def log_error():
    """Receive error reports from cron jobs and send email alert"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        script = data.get('script', 'unknown')
        error = data.get('error', 'No error message')
        context = data.get('context', {})
        
        # Log to console
        print(f"ERROR REPORT: {script} - {error}")
        # Send email alert
        emailer = EmailNotifier()
        emailer.send_email(
            to_email="contact.regenesis.art@gmail.com",
            subject=f"⚠️ CRON ERROR: {script}",
            body=f"""
Script: {script}
Error: {error}
Context: {context}
Time: {datetime.now().isoformat()}
            """
        )

        # Store in Firestore for history
        error_record = {
            'script': script,
            'error': error,
            'context': context,
            'timestamp': datetime.now().isoformat()
        }

        # Store in Firestore if available
        if db:
            error_record = {
                'script': script,
                'error': error,
                'context': context,
                'timestamp': datetime.now().isoformat()
            }
            db.collection('error_logs').add(error_record)
            print(f"📝 Error logged to Firestore")
        else:
            print(f"⚠️ Firestore unavailable - error not persisted")

        return jsonify({
            "status": "logged",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ========== RUN ==========

app = application

if __name__ == "__main__":
    application.run(debug=True, host="0.0.0.0", port=8080)
