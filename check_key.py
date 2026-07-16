import os
import requests
import hmac
import hashlib
import time
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("BINANCE_API_KEY_TESTNET")
secret_key = os.getenv("BINANCE_SECRET_KEY_TESTNET")

base_url = "https://testnet.binance.vision"

timestamp = int(time.time() * 1000)
query_string = f"timestamp={timestamp}"
signature = hmac.new(
    secret_key.encode("utf-8"),
    query_string.encode("utf-8"),
    hashlib.sha256
).hexdigest()

headers = {
    "X-MBX-APIKEY": api_key
}
response = requests.get(f"{base_url}/api/v3/account?{query_string}&signature={signature}", headers=headers)
print(f"REST API Response: {response.status_code}")
print(response.json())
