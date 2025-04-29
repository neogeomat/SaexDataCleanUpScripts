# -*- coding: utf-8 -*-
import base64
import requests
import socket
import subprocess

encoded_token = 'NzcwMjcxMDUwNTpBQUY2MGxydkE1ZHN1azZTbk1ldk5VcFBWWlRMMS1IdnBOYw=='
encoded_chat_id = 'LTEwMDI2MDExMzI0NjU='
#encoded_chat_id = 'NjU5ODcwMzk4'

socket_available = True
try:
    import socket
    import base64

except ImportError:
    print("socket not found. Trying to install...")
    try:
        subprocess.call(["python", "-m", "pip", "install", "socket"])
        subprocess.call(["python", "-m", "pip", "install", "base64"])
        import socket  # Try importing again after installation
        import base64
    except ImportError:
        socket_available = False  # If installation fails, disable the button

def check_internet():
    try:
        # Try to reach Google's DNS server to check for internet connection
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False

def get_ip_address():
    try:
        # Connect to a public DNS server (Google's) to get the external IP (in LAN)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "IP not available"

def send_telegram_message(message):
    app_version = "2.0.1"
    icon = "📱"  # Mobile phone emoji as an icon
    ip_address = get_ip_address()

    message_with_version = "{}\n{} App version = {}\n🖥️ IP = {}".format(message, icon, app_version, ip_address)

    if not check_internet():
        return
    if not socket_available:
        return

    TOKEN = base64.b64decode(encoded_token).decode('utf-8')
    CHAT_ID = base64.b64decode(encoded_chat_id).decode('utf-8')
    url = 'https://api.telegram.org/bot{}/sendMessage'.format(TOKEN)
    payload = {
        'chat_id': CHAT_ID,
        'text': message_with_version
    }
    try:
        response = requests.post(url, data=payload)
    except Exception as e:
        return
        #print 'Error sending message:', str(e)
