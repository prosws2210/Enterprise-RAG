import requests
import time

BASE_URL = "http://localhost:8000"
FILE_PATH = r"C:\Users\sahus\Desktop\ShaktiSwaroopSahu.pdf"

print("Waiting for server to be ready...")
for _ in range(30):
    try:
        if requests.get(f"{BASE_URL}/healthz", timeout=2).status_code == 200:
            break
    except Exception:
        time.sleep(2)
else:
    print("Server not ready.")
    exit(1)

print("\n1. Registering user...")
res = requests.post(f"{BASE_URL}/api/v1/auth/register", json={"username": "auditor@demo.local", "password": "password123"}, timeout=60)
print(res.status_code, res.text)

print("\n2. Logging in...")
res = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"username": "auditor@demo.local", "password": "password123"}, timeout=60)
print(res.status_code, res.text)
if res.status_code != 200:
    print("Login failed, aborting.")
    exit(1)

token = res.json().get("token")
headers = {"Authorization": f"Bearer {token}"}

print("\n3. Uploading document...")
with open(FILE_PATH, "rb") as f:
    res = requests.post(f"{BASE_URL}/api/v1/documents/upload", headers=headers, files={"file": ("ShaktiSwaroopSahu.pdf", f, "application/pdf")}, timeout=300)
print(res.status_code, res.text)

time.sleep(5) # wait for embedding

print("\n4. Query 1: who is shakti??")
res = requests.post(f"{BASE_URL}/api/v1/query", headers=headers, json={"question": "who is shakti??", "enable_crag": False}, timeout=120)
print(res.status_code, res.text)

print("\n5. Query 2: What all tings he has done in colleg and all??")
res = requests.post(f"{BASE_URL}/api/v1/query", headers=headers, json={"question": "What all tings he has done in colleg and all??", "enable_crag": False}, timeout=120)
print(res.status_code, res.text)

