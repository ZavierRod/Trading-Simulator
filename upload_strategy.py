# upload_strategy.py
import requests
import json

with open("TestStrategy.py") as f:
    code = f.read()

payload = {
    "firm_id": 1,
    "code": code
}

r = requests.post("http://localhost:8000/api/strategies", json=payload)
print(r.status_code, r.text)