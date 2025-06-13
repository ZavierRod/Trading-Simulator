# upload_strategy.py
import requests
import json

with open("tmp_strategy.py") as f:
    code = f.read()

payload = {
    "firm_id": 3,
    "code": code
}

r = requests.post("http://localhost:8000/api/strategies", json=payload)
print(r.status_code, r.text)