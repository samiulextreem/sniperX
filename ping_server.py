#!/usr/bin/env python3
"""
Simple ping server to receive text payloads from Android app
"""

from flask import Flask, request, jsonify
import datetime
import threading
import time

# Global storage for ping data
ping_data = {
    'last_ping': None,
    'count': 0,
    'payloads': [],
    'last_text': None
}

app = Flask(__name__)

@app.route('/ping', methods=['GET', 'POST'])
def ping():
    """Receive ping with text payload from Android app"""
    global ping_data
    
    # Accept text via JSON (POST) or query param (GET)
    received_text = None
    if request.method == 'POST':
        text_payload = request.get_json(silent=True) or {}
        if 'text' in text_payload:
            received_text = text_payload['text']
    else:
        received_text = request.args.get('text')
    
    # Display incoming ping
    print(f"\n{'─'*70}")
    print(f"📱 PING RECEIVED from {request.remote_addr}")
    if received_text:
        ping_data['last_text'] = received_text
        print(f"📝 Message: '{received_text}'")
    else:
        received_text = "No text provided"
        print(f"📝 Message: (none)")
    print(f"{'─'*70}\n")
    
    # Update ping data
    ping_data['last_ping'] = datetime.datetime.now()
    ping_data['count'] += 1
    ping_data['payloads'].append({
        'timestamp': ping_data['last_ping'].isoformat(),
        'text': received_text
    })
    
    # Keep only last 50 payloads to avoid memory issues
    if len(ping_data['payloads']) > 50:
        ping_data['payloads'] = ping_data['payloads'][-50:]
    
    # Return response to Android app
    return jsonify({
        'status': 'success',
        'timestamp': ping_data['last_ping'].isoformat(),
        'count': ping_data['count'],
        'message': f'Received: {received_text}'
    })

@app.route('/status')
def status():
    """Check ping status and recent payloads"""
    return jsonify({
        'last_ping': ping_data['last_ping'].isoformat() if ping_data['last_ping'] else None,
        'count': ping_data['count'],
        'last_text': ping_data['last_text'],
        'recent_payloads': ping_data['payloads'][-10:]  # Last 10 payloads
    })

@app.route('/')
def home():
    """Simple home page"""
    return """
    <h1>Ping Server Running</h1>
    <p>Send POST requests to /ping with JSON payload:</p>
    <pre>{"text": "your message here"}</pre>
    <p><a href="/status">Check Status</a></p>
    """

def start_ping_server():
    """Start the ping server"""
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)  # Suppress Flask's request logging
    
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    start_ping_server()
