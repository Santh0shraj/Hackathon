"""
Script to test which models are available with your Unbound API key.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("UNBOUND_API_KEY")
API_URL = os.environ.get("UNBOUND_API_URL", "https://api.getunbound.ai/v1/chat/completions")

# Common models to test
MODELS_TO_TEST = [
    "gpt-4o",
    "gpt-4-turbo",
    "gpt-4",
    "gpt-3.5-turbo",
    "claude-3-5-sonnet-20241022",
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
]

def test_model(model_name):
    """Test if a model is available by making a simple API call."""
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "Say 'test'"}],
        "max_tokens": 10
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return "[OK] AVAILABLE"
        elif response.status_code == 400:
            error_data = response.json()
            if "model_not_supported" in str(error_data):
                return "[NO] Not enabled"
            else:
                return f"[ERR] {error_data.get('error', {}).get('message', 'Unknown')}"
        else:
            return f"[ERR] HTTP {response.status_code}"
    except Exception as e:
        return f"[ERR] {str(e)}"

if __name__ == "__main__":
    print("=" * 70)
    print("Testing Unbound API Models")
    print("=" * 70)
    print(f"API URL: {API_URL}")
    print(f"API Key: {API_KEY[:20]}..." if API_KEY else "API Key: NOT SET")
    print("=" * 70)
    print()
    
    if not API_KEY:
        print("[ERROR] UNBOUND_API_KEY not found in .env file")
        exit(1)
    
    available_models = []
    
    for model in MODELS_TO_TEST:
        print(f"Testing {model:40} ... ", end="", flush=True)
        result = test_model(model)
        print(result)
        
        if "AVAILABLE" in result:
            available_models.append(model)
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if available_models:
        print(f"\n[SUCCESS] {len(available_models)} model(s) available:")
        for model in available_models:
            print(f"   - {model}")
        print(f"\n[TIP] Use one of these models in your workflow!")
    else:
        print("\n[ERROR] No models are available.")
        print("   Please check your Unbound application settings at:")
        print("   https://gateway.getunbound.ai/ai-gateway-applications")
