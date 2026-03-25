from fastapi import Depends, HTTPException
import jwt
import os
from dotenv import load_dotenv
load_dotenv() 
from fastapi.security import HTTPBearer
httpconnector = HTTPBearer(auto_error=False)

def getuser(token = Depends(httpconnector)):
    if token is None or not token.credentials:
        raise HTTPException(status_code=401, detail="Missing authorization token")

    security_key = os.getenv("SECURITY_KEY")
    algorithm = os.getenv("ALGORITHM")

    if not security_key or not algorithm:
        raise HTTPException(status_code=500, detail="JWT configuration missing")

    try:
        data = jwt.decode(token.credentials, security_key, algorithms=[algorithm])
        return data
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")