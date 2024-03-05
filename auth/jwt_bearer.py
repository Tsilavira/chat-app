from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .jwt_handles import decodeJWT

class jwtBearer(HTTPBearer):
    def __init__(self, auto_Error : bool = True):
        super(jwtBearer, self).__init__(auto_error=auto_Error)

    async def __call__(self, request: Request):
        credentials : HTTPAuthorizationCredentials = await super(jwtBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code= 403, detail="Invalid or expired token")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code= 403, detail="Invalid or expired token")
            return credentials.credentials
        else:
            raise HTTPException(status_code= 403, detail="Invalid or expired token")
        
    def verify_jwt(self, jwttoken: str):
        isTokenValid: bool = False
        payload = decodeJWT(jwttoken)
        if payload and "userID" in payload:
            isTokenValid = True
        return isTokenValid