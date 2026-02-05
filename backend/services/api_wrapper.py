
import sys
import json
import ssl
import http.client
import urllib.parse
from dotenv import load_dotenv

def make_request():
    try:
        # Load env vars
        load_dotenv()
        
        # Read input from stdin
        input_data = sys.stdin.read()
        if not input_data:
            print(json.dumps({"error": "No input provided"}))
            return

        data = json.loads(input_data)
        
        api_key = data.get("api_key")
        payload = data.get("payload")
        url_str = data.get("url", "https://api.getunbound.ai/v1/chat/completions")
        
        parsed_url = urllib.parse.urlparse(url_str)
        host = parsed_url.netloc
        path = parsed_url.path
        
        # Create connection with TCP Keep-Alive
        context = ssl.create_default_context()
        conn = http.client.HTTPSConnection(host, context=context, timeout=120) # Increased timeout
        
        # Access the underlying socket to set Keep-Alive
        conn.connect()
        sock = conn.sock
        if sock:
            import socket
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            # Set keepalive params if available (Windows/Linux specific, but simple enable helps)
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0", # Simple UA
            "Connection": "keep-alive"   # Try to keep it open
        }
        
        # Force STREAMING to prevent idle timeouts
        payload["stream"] = True
        
        json_body = json.dumps(payload).encode('utf-8')
        
        # Log for debugging
        sys.stderr.write(f"Wrapper (http.client + Stream) connecting to: {host}\n")
        
        # Standard Request
        conn.request("POST", path, body=json_body, headers=headers)
        
        # Get Response
        response = conn.getresponse()
        
        if response.status >= 400:
             resp_body = response.read().decode('utf-8')
             print(json.dumps({"error": f"HTTP {response.status}", "body": resp_body}))
             conn.close()
             return

        # Process Streaming Response (SSE)
        full_content = ""
        prompt_tokens = 0
        completion_tokens = 0
        
        while True:
            line = response.readline()
            if not line:
                break
            
            line = line.decode('utf-8').strip()
            if line.startswith("data: ") and line != "data: [DONE]":
                try:
                    data_str = line[6:] # Strip "data: "
                    chunk = json.loads(data_str)
                    
                    # Accumulate content
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            full_content += content
                            
                    # Track usage if available (some APIs send it in last chunk)
                    if "usage" in chunk:
                         prompt_tokens = chunk["usage"].get("prompt_tokens", 0)
                         completion_tokens = chunk["usage"].get("completion_tokens", 0)
                except:
                    pass
        
        conn.close()
        
        # Construct final JSON response compatible with non-streaming expectation
        final_response = {
            "choices": [
                {
                    "message": {
                        "content": full_content,
                        "role": "assistant"
                    }
                }
            ],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens or len(full_content)//4, # Estimate if missing
                "total_tokens": prompt_tokens + (completion_tokens or len(full_content)//4)
            }
        }
        
        print(json.dumps(final_response))
        
    except Exception as e:
        print(json.dumps({"error": f"Request failed: {str(e)}"}))

if __name__ == "__main__":
    make_request()
