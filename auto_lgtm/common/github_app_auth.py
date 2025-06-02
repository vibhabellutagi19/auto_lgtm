import jwt
import time
import requests

def generate_jwt(app_id, private_key_pem):
    now = int(time.time())
    payload = {
        "iat": now - 60,
        "exp": now + (10 * 60),
        "iss": app_id
    }
    encoded_jwt = jwt.encode(payload, private_key_pem, algorithm="RS256")
    return encoded_jwt

def get_installation_access_token(app_id, private_key_pem, installation_id):
    jwt_token = generate_jwt(app_id, private_key_pem)
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json"
    }
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()["token"]