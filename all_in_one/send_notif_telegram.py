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
        s = socket.create_connection(("8.8.8.8", 53), timeout=5)
        s.close()
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

    # Always send to Discord first
    send_discord_message(message)

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


def send_discord_message(message):
    # -*- coding: utf-8 -*-
    import urllib2
    import json

    DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1397458172054208622/f5sTLzFM7r5erkFXN17RmVVj1b1gAdbF167E1ZvjJmLzp8lNvjtRodnk5lVqVv4xhZUn'

    try:
        payload = {"content": "Test message"}
        data = json.dumps(payload).encode('utf-8')
        req = urllib2.Request(DISCORD_WEBHOOK_URL, data, {'Content-Type': 'application/json'})
        response = urllib2.urlopen(req)
        print("Message sent, status:", response.getcode())

    except urllib2.HTTPError as e:
        print("HTTPError code:", e.code)
        print("HTTPError reason:", e.reason)
        print("HTTPError body:", e.read())

    except urllib2.URLError as e:
        print("URLError reason:", e.reason)

    except Exception as e:
        print("Unexpected error:", str(e))
    try:
        message = u"""📢 **Test Notification**
    📱 App version: 2.4.1
    🖥️ IP: 192.168.71.155
    📍 Location: Kathmandu
    💻 Computer: DESKTOP-4FIHCOV
    📝 Message: ✅ Compacting process completed successfully.
    🗂 Path: 
    📄 Script: compactDb
    ⏱ Duration: 0.00 seconds"""

        payload = {"content": message}
        data = json.dumps(payload).encode('utf-8')
        req = urllib2.Request(DISCORD_WEBHOOK_URL, data, {'Content-Type': 'application/json'})
        response = urllib2.urlopen(req)

        print("✅ Discord message sent! Status Code:", response.getcode())

    except Exception as e:
        print("❌ Error during Discord notification:", str(e))
