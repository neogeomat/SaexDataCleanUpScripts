# -*- coding: utf-8 -*-

import requests
import subprocess
encoded_token = 'NzcwMjcxMDUwNTpBQUY2MGxydkE1ZHN1azZTbk1ldk5VcFBWWlRMMS1IdnBOYw=='
encoded_chat_id = 'LTEwMDI2MDExMzI0NjU='
# encoded_chat_id = 'NjU5ODcwMzk4'   #for test

import subprocess
from shared_data import VERSION

version = VERSION
socket_available = True
base64_available = True
urllib2_available = True
json_available = True

try:
    import socket
except ImportError:
    print("socket module not found.")
    socket_available = False

try:
    import base64
except ImportError:
    print("base64 module not found.")
    base64_available = False

try:
    import urllib2
except ImportError:
    print("urllib2 module not found.")
    urllib2_available = False

try:
    import json
except ImportError:
    print("json module not found.")
    json_available = False

# Print results or act based on availability
if not socket_available:
    print("socket is required but not available. Exiting or disabling related functionality.")
if not base64_available:
    print("base64 is required but not available.")
if not urllib2_available:
    print("urllib2 is required but not available.")
if not json_available:
    print("json is required but not available.")
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
    # app_version = "2.1.2"
    app_version = version
    icon = u"📱"  # Mobile phone emoji as an icon
    ip_address = get_ip_address()
    location = get_location()
    comp_name = get_computer_name()

    if not check_internet():
        return
    if not socket_available:
        return

    try:
        TOKEN = base64.b64decode(encoded_token).decode('utf-8')
        CHAT_ID = base64.b64decode(encoded_chat_id).decode('utf-8')
        icon = u"\U0001F4F1"  # 📱
        monitor_emoji = u"\U0001F5A5"  # 🖥️
        pin_emoji = u"\U0001F4CD"  # 📍
        laptop_emoji = u"\U0001F4BB"  # 💻

        # Ensure the input message is Unicode (decode if it's bytes)
        if isinstance(message, bytes):
            message = message.decode('utf-8')

        message_with_version = u"{}\n{} App version = {}\n{} IP = {}\n{} Location = {}\n{} Computer = {}".format(
            message, icon, app_version, monitor_emoji, ip_address, pin_emoji, location, laptop_emoji, comp_name
        )

        url = 'https://api.telegram.org/bot{}/sendMessage'.format(TOKEN)
        payload = {
            'chat_id': CHAT_ID,
            'text': message_with_version  # requests will handle encoding
        }
        response = requests.post(url, data=payload)
    except Exception as e:
        print("Error during tele: {}".format(str(e)))
def get_location():
    try:
        response = urllib2.urlopen('http://ip-api.com/json/')
        data = json.load(response)
        if data['status'] == 'success':
            return data.get('city', 'not found')
        else:
            return 'not found'
    except:
        return 'not found'

def get_computer_name():
    try:
        return socket.gethostname()
    except:
        return 'not found'
