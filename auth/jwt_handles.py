import time
import jwt
from decouple import config
import os

JWT_SECRET = str(config("secret")) #errors if not string
JWT_ALGORITHM = str(config("algorithm"))

def token_response(token: str):
    return {
        "access_token" : token
    }

def signJWT(userID: str):
    try:
        payload = {
            "userID": userID,
            "exp": int(time.time()) + 3600  # Make sure to convert to int + vgm is dit in sec
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token_response(token)
    except Exception as e:
        print(f"Error in signJWT: {e}")
        return None


def decodeJWT(token: str):
    try:
        decode_token = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        return decode_token if decode_token.get("exp", 0) >= time.time() else None
    except jwt.ExpiredSignatureError:
        return None  # Token has expired        
    except jwt.InvalidTokenError:
        return None  # Invalid token
    
