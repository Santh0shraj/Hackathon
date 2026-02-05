
import os
import psycopg2
from dotenv import load_dotenv
import socket

load_dotenv()

db_url = os.getenv("DATABASE_URL")
print(f"Testing connection to: {db_url}")

host = db_url.split("@")[1].split(":")[0]
print(f"Extracted host: {host}")

try:
    print(f"Attempting to resolve {host}...")
    addr = socket.gethostbyname(host)
    print(f"Resolved to: {addr}")
except Exception as e:
    print(f"DNS Resolution failed: {e}")

try:
    print("Attempting to connect via psycopg2...")
    conn = psycopg2.connect(db_url)
    print("SUCCESS: Connected to database!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
