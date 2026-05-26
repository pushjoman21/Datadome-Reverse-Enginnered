#!/usr/bin/env python3
"""
Datadome Solver Service for OpenBullet2

Simple Flask microservice that handles fingerprint generation,
encryption, and challenge submission in a single endpoint.

Usage:
    python solver_service.py
    
Then in OpenBullet2, add "Datadome Solver" block with:
    ServiceUrl = "http://localhost:5000"
"""

import sys
import os
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from builder import build_payload
    from crypto import encrypt
    import tls_client
    import urllib.parse
except ImportError as e:
    print(f"[!] Missing dependency: {e}")
    print("[!] Install with: pip install -r openbullet2/requirements.txt")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

# Global session cache
_session_cache = {}


def get_session():
    """Get or create TLS session"""
    global _session_cache
    now = time.time()
    
    # Recreate session every 5 minutes
    if 'session' not in _session_cache or (now - _session_cache.get('created', 0)) > 300:
        _session_cache['session'] = tls_client.Session(client_identifier="chrome")
        _session_cache['created'] = now
    
    return _session_cache['session']


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'Datadome Solver',
        'version': '1.0'
    })


@app.route('/solve', methods=['POST'])
def solve():
    """
    Main solve endpoint - builds fingerprint, encrypts, and submits challenge
    
    Request JSON:
    {
        "url": "https://www.etsy.com/",
        "ddjskey": "D013AA612AB2224D03B2318D0F5B19",
        "cid": "challenge_id",
        "profile": "chrome_win10"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['url', 'ddjskey']
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({
                'success': False,
                'cookie': None,
                'error': f'Missing fields: {", ".join(missing)}'
            }), 400
        
        url = data.get('url', 'https://www.etsy.com/')
        ddjskey = data['ddjskey']
        cid = data.get('cid', '')
        profile = data.get('profile', 'chrome_win10')
        
        print(f"[*] Solving Datadome challenge for {url}")
        print(f"[*] Profile: {profile}, CID: {cid}")
        
        # Step 1: Build fingerprint payload
        print("[*] Step 1: Building fingerprint...")
        payload_json = build_payload(
            profile=profile,
            url=url,
            tags_js_url=None,
            server_hash=None,
            bpc=1
        )
        print(f"[*] Built payload with {len(payload_json)} signals")
        
        # Step 2: Encrypt payload
        print("[*] Step 2: Encrypting payload...")
        encrypted_payload = encrypt(payload_json, ddjskey=ddjskey, cid=cid)
        print(f"[*] Encrypted payload: {len(encrypted_payload)} characters")
        
        # Step 3: Submit challenge
        print("[*] Step 3: Submitting challenge...")
        session = get_session()
        
        # Extract domain
        domain = url.rstrip('/').split('//')[-1].split('/')[0]
        referer_encoded = urllib.parse.quote(url, safe='')
        
        # Build headers
        headers = {
            'accept': '*/*',
            'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': f'https://{domain}',
            'referer': url,
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
        }
        
        # Build form data
        form_data = {
            'jspl': encrypted_payload,
            'eventCounters': '[]',
            'jsType': 'ch',
            'cid': cid,
            'ddk': ddjskey,
            'Referer': referer_encoded,
            'request': '%2F',
            'responsePage': 'origin',
            'ddv': '5.6.6',
        }
        
        # Submit to target
        tags_url = f'https://{domain}/include/tags.js'
        print(f"[*] Submitting to: {tags_url}")
        
        response = session.post(tags_url, headers=headers, data=form_data)
        print(f"[*] Response status: {response.status_code}")
        
        try:
            response_json = response.json()
        except:
            print(f"[!] Invalid JSON response")
            return jsonify({
                'success': False,
                'cookie': None,
                'error': 'Server returned invalid response'
            }), 500
        
        # Check response
        if response_json.get('status') == 200:
            cookie = response_json.get('cookie')
            print(f"[+] Success! Cookie: {cookie}")
            return jsonify({
                'success': True,
                'cookie': cookie,
                'error': None
            })
        else:
            error = f"Status {response_json.get('status', 'unknown')}"
            print(f"[!] Failed: {error}")
            return jsonify({
                'success': False,
                'cookie': None,
                'error': error
            }), 403
    
    except Exception as e:
        print(f"[!] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'cookie': None,
            'error': str(e)
        }), 500


@app.route('/build', methods=['POST'])
def build():
    """
    Build fingerprint endpoint (debug)
    
    Request JSON:
    {
        "url": "https://www.etsy.com/",
        "profile": "chrome_win10"
    }
    """
    try:
        data = request.get_json()
        url = data.get('url', 'https://www.etsy.com/')
        profile = data.get('profile', 'chrome_win10')
        
        payload = build_payload(profile=profile, url=url)
        
        return jsonify({
            'success': True,
            'payload': {k: str(v) for k, v in payload.items()},
            'signal_count': len(payload)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/encrypt', methods=['POST'])
def encrypt_endpoint():
    """
    Encrypt payload endpoint (debug)
    
    Request JSON:
    {
        "payload": {...},
        "ddjskey": "...",
        "cid": "..."
    }
    """
    try:
        data = request.get_json()
        payload = data.get('payload')
        ddjskey = data.get('ddjskey')
        cid = data.get('cid', '')
        
        if not payload or not ddjskey:
            return jsonify({
                'success': False,
                'error': 'Missing payload or ddjskey'
            }), 400
        
        encrypted = encrypt(payload, ddjskey=ddjskey, cid=cid)
        
        return jsonify({
            'success': True,
            'encrypted': encrypted,
            'length': len(encrypted)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            'GET /health',
            'POST /solve',
            'POST /build',
            'POST /encrypt'
        ]
    }), 404


if __name__ == '__main__':
    print("\n" + "="*60)
    print(" Datadome Solver Service for OpenBullet2")
    print("="*60)
    print("\n[*] Starting service...")
    print("[*] Available endpoints:")
    print("    GET  /health          - Health check")
    print("    POST /solve           - Solve Datadome challenge")
    print("    POST /build           - Build fingerprint (debug)")
    print("    POST /encrypt         - Encrypt payload (debug)")
    print("\n[*] Listening on http://localhost:5000")
    print("[*] Press CTRL+C to stop\n")
    
    try:
        app.run(host='127.0.0.1', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n[*] Service stopped.")
