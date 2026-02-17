import requests
import json

r = requests.get('http://127.0.0.1:8000/api/layouts/')
print('Status:', r.status_code)
print('Response:')
print(json.dumps(r.json(), ensure_ascii=False, indent=2))
