from fastapi import Depends
import jwt
import os
from dotenv import load_dotenv
load_dotenv() 
from fastapi.security import HTTPBearer
httpconnector = HTTPBearer()

def getuser(token = Depends(httpconnector)):
    data = jwt.decode(token.credentials , os.getenv("SECURITY_KEY"), algorithms=[os.getenv("ALGORITHM")])
    return data