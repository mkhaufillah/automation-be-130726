import os
import requests
import base64
import time
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ed25519, padding
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ED25519_BINANCE_API_KEY_TESTNET")
secret_key = os.getenv("ED25519_BINANCE_SECRET_KEY_TESTNET")

base_url = "https://testnet.binance.vision"

timestamp = int(time.time() * 1000)
query_string = f"timestamp={timestamp}"
payload = query_string.encode("utf-8")

secret = secret_key.replace('\\n', '\n')
private_key = serialization.load_pem_private_key(
    secret.encode("utf-8"),
    password=None
)

if isinstance(private_key, ed25519.Ed25519PrivateKey):
    signature_bytes = private_key.sign(payload)
else:
    signature_bytes = private_key.sign(
        payload,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

signature = base64.b64encode(signature_bytes).decode("utf-8")

# For requests, we might need to urlencode the signature if it contains +, / etc.
import urllib.parse
signature_encoded = urllib.parse.quote(signature)

headers = {
    "X-MBX-APIKEY": api_key
}
response = requests.get(f"{base_url}/api/v3/account?{query_string}&signature={signature_encoded}", headers=headers)
print(f"REST API Response: {response.status_code}")
print(response.json())
