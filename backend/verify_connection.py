
import os
import requests
import logging
from dotenv import load_dotenv

# Configure logging to see detailed requests info
logging.basicConfig(level=logging.DEBUG)

load_dotenv()

API_KEY = os.environ.get("UNBOUND_API_KEY")
API_URL = os.environ.get("UNBOUND_API_URL", "https://api.getunbound.ai/v1/chat/completions")

print(f"Testing connection to: {API_URL}")
print(f"Using Model: kimi-k2p5")

payload = {
    "model": "kimi-k2p5",
    "messages": [
        {"role": "user", "content": "Hello, are you there?"}
    ]
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

try:
    print("\nSending request...")
    response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 200:
        print("\n✅ SUCCESS! Connection working.")
    else:
        print("\n❌ FAILED. Server returned error.")

except Exception as e:
    print(f"\n❌ CONNECTION ERROR: {e}")
