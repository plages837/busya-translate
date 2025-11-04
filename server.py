from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import webbrowser
import threading
import time
import socket
import sys
import platform
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='.')
CORS(app)

PORT = int(os.getenv('PORT', 8000))


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/favicon.ico')
def favicon():
    try:
        return send_from_directory('.', 'favicon.ico')
    except:
        return '', 204  # No content if file doesn't exist


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)


@app.route('/api/translate', methods=['POST'])
def translate():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        source_lang = data.get('sourceLang', 'auto')
        target_lang = data.get('targetLang', 'en')

        if not text:
            return jsonify({'error': 'Text is required'}), 400

        # Always use Yandex Translator API
        return translate_with_yandex(text, source_lang, target_lang)

    except Exception as e:
        print(f'Translation error: {str(e)}')
        return jsonify({
            'error': 'Translation failed',
            'message': str(e)
        }), 500


def translate_with_yandex(text, source_lang, target_lang):
    """Translate using Yandex Translator API"""
    try:
        yandex_api_key = os.getenv('YANDEX_API_KEY')
        yandex_folder_id = os.getenv('YANDEX_FOLDER_ID')
        yandex_iam_token = os.getenv('YANDEX_IAM_TOKEN')
        
        if not yandex_api_key and not yandex_iam_token:
            return jsonify({'error': 'Yandex API key or IAM token not configured'}), 500
        
        if not yandex_folder_id:
            print('⚠️  Warning: YANDEX_FOLDER_ID not set. Some features may not work.')

        # Yandex Translator API v2
        api_url = 'https://translate.api.cloud.yandex.net/translate/v2/translate'
        
        # Map language codes for Yandex
        lang_map = {
            'auto': '',
            'en': 'en',
            'ru': 'ru',
            'es': 'es',
            'fr': 'fr',
            'de': 'de',
            'it': 'it',
            'pt': 'pt',
            'zh': 'zh',
            'ja': 'ja',
            'ko': 'ko',
            'ar': 'ar'
        }
        
        source = lang_map.get(source_lang, '')
        target = lang_map.get(target_lang, 'en')
        
        if not target:
            target = 'en'  # Default target
        
        # Prepare headers - try IAM token first, then Api-Key
        if yandex_iam_token:
            headers = {
                'Authorization': f'Bearer {yandex_iam_token}',
                'Content-Type': 'application/json'
            }
        else:
            headers = {
                'Authorization': f'Api-Key {yandex_api_key}',
                'Content-Type': 'application/json'
            }
        
        payload = {
            'texts': [text],
            'targetLanguageCode': target
        }
        
        if source and source != 'auto':
            payload['sourceLanguageCode'] = source
        
        # Add folderId if provided
        if yandex_folder_id:
            payload['folderId'] = yandex_folder_id
        
        print(f"Using Yandex Translator API: {source if source else 'auto'} -> {target}")
        
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        
        translated_text = response_data['translations'][0]['text']
        
        return jsonify({
            'success': True,
            'originalText': text,
            'translatedText': translated_text,
            'sourceLang': source if source else 'auto',
            'targetLang': target,
            'model': 'yandex'
        })
    
    except requests.exceptions.RequestException as e:
        error_message = 'Unknown error'
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_message = error_data.get('message', error_data.get('code', str(e)))
            except:
                error_message = str(e)
            # Log full error for debugging
            print(f'Yandex API error response: {e.response.text}')
        else:
            error_message = str(e)
        
        print(f'Yandex Translation error: {error_message}')
        return jsonify({
            'error': 'Translation failed',
            'message': error_message
        }), 500




@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'Busya Translate'})


def is_port_in_use(port):
    """Check if port is in use by trying to bind to it"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return False  # Port is free
        except OSError:
            return True  # Port is in use


def kill_process_on_port(port):
    """Kill process using specified port"""
    try:
        if platform.system() == 'Windows':
            # Find process using the port - look for LISTENING state
            cmd = f'netstat -ano | findstr ":{port}" | findstr "LISTENING"'
            result = os.popen(cmd).read()
            if result:
                lines = result.strip().split('\n')
                pids = set()
                for line in lines:
                    # Parse netstat output: TCP    0.0.0.0:8080    0.0.0.0:0    LISTENING    12345
                    parts = line.split()
                    if len(parts) >= 5:
                        # PID is usually the last element
                        try:
                            pid = parts[-1]
                            if pid.isdigit():
                                pids.add(pid)
                        except:
                            continue
                
                killed = False
                for pid in pids:
                    print(f"🔄 Found process {pid} using port {port}")
                    # Try to get process name
                    try:
                        proc_name = os.popen(f'tasklist /FI "PID eq {pid}" /FO LIST | findstr "Image Name"').read()
                        if proc_name:
                            name = proc_name.split(':')[-1].strip()
                            print(f"   Process: {name}")
                    except:
                        pass
                    
                    # Kill the process
                    result = os.system(f'taskkill /F /PID {pid} >nul 2>&1')
                    if result == 0:
                        print(f"✅ Process {pid} terminated")
                        killed = True
                    else:
                        print(f"⚠️  Could not terminate process {pid} (may require admin rights)")
                
                if killed:
                    time.sleep(2)  # Wait for port to be freed
                    return True
        else:
            # Linux/Mac
            result = os.popen(f'lsof -ti:{port}').read().strip()
            if result:
                pids = result.split('\n')
                killed = False
                for pid in pids:
                    if pid and pid.isdigit():
                        result = os.system(f'kill -9 {pid} >/dev/null 2>&1')
                        if result == 0:
                            print(f"✅ Process {pid} terminated")
                            killed = True
                if killed:
                    time.sleep(1)
                    return True
    except Exception as e:
        print(f"⚠️  Error killing process: {e}")
    return False


def get_available_localhosts():
    """Get list of available localhost addresses"""
    hosts = []
    try:
        # Get hostname
        hostname = socket.gethostname()
        
        # Get local IP addresses
        local_ips = []
        try:
            # Connect to external server to get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ips.append(s.getsockname()[0])
            s.close()
        except:
            pass
        
        # Standard localhost addresses
        hosts.append({
            'name': 'localhost',
            'url': f'http://localhost:{PORT}',
            'description': 'Standard localhost'
        })
        
        hosts.append({
            'name': '127.0.0.1',
            'url': f'http://127.0.0.1:{PORT}',
            'description': 'IPv4 localhost'
        })
        
        # Add local network IPs
        for ip in local_ips:
            if ip:
                hosts.append({
                    'name': ip,
                    'url': f'http://{ip}:{PORT}',
                    'description': f'Network IP ({hostname})'
                })
        
        return hosts
    except Exception as e:
        print(f"⚠️  Error getting localhost info: {e}")
        return [{
            'name': 'localhost',
            'url': f'http://localhost:{PORT}',
            'description': 'Standard localhost'
        }]


def open_browser():
    """Open browser after a short delay"""
    time.sleep(2)  # Wait for server to start
    url = f"http://localhost:{PORT}"
    webbrowser.open(url)
    print(f"🌐 Browser opened at {url}")


if __name__ == '__main__':
    print("=" * 60)
    print("🌍 Busya Translate - Neural Network Translation")
    print("=" * 60)
    print()
    
    # Check if port is in use
    if is_port_in_use(PORT):
        print(f"⚠️  Port {PORT} is already in use!")
        response = input(f"🔄 Kill process on port {PORT} and start new server? (y/n): ").lower().strip()
        if response == 'y' or response == 'yes' or response == '':
            if kill_process_on_port(PORT):
                print(f"✅ Port {PORT} is now free")
                time.sleep(1)
            else:
                print(f"❌ Could not free port {PORT}")
                print("   Please close the application using the port manually")
                sys.exit(1)
        else:
            print("❌ Server startup cancelled")
            sys.exit(0)
    
    # Show available localhost addresses
    print()
    print("📡 Available localhost addresses:")
    print("-" * 60)
    hosts = get_available_localhosts()
    for host in hosts:
        print(f"  • {host['name']:20} - {host['url']}")
        print(f"    {host['description']}")
    print("-" * 60)
    print()
    
    print(f"🚀 Starting server on http://localhost:{PORT}")
    print(f"📝 Using Yandex API for translation")
    print(f"🤖 Using Puter.js with OpenRouter for AI chat")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    # Open browser in a separate thread
    if os.getenv('AUTO_OPEN_BROWSER', 'true').lower() == 'true':
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
    
    try:
        app.run(host='0.0.0.0', port=PORT, debug=False)
    except OSError as e:
        if "Address already in use" in str(e) or "Only one usage of each socket address" in str(e):
            print(f"❌ Port {PORT} is still in use!")
            print("   Please close the application using the port manually")
            sys.exit(1)
        else:
            raise
