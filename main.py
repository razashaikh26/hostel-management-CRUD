from fastapi import FastAPI,Depends,HTTPException
from dbconnector import connect
from pydanticccreate import Login
from decoder import getuser
import os
import jwt
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

@app.post("/login")
def login( data : Login):
    username = data.username
    password = data.password
    cur = connect.cursor()
    cur.execute(
        "SELECT name, password, role FROM users WHERE name = %s",
        (username,)
    )
    user = cur.fetchone()
    if user is None:
        raise HTTPException(status_code=401, detail="No user found")
    db_username, db_password, db_role = user
    if db_password != password:
        raise HTTPException(status_code=401, detail="Invalid password")
    token = jwt.encode(
        {"username": db_username, "role": db_role},
        os.getenv("SECURITY_KEY"),
        algorithm=os.getenv("ALGORITHM")
    )
    cur.close()
    return {"access_token": token}
    

@app.post("/admin")
def admin(user = Depends(getuser)):
    if user["role"] != "admin":
        raise HTTPException(status_code=401 , detail="Only admins are allowed here")
    
    return {"message": "Admin access granted"}


@app.post("/student")
def admin(user = Depends(getuser)):
    if user["role"] != "student":
        raise HTTPException(status_code=401 , detail="Only students are allowed here")
    
    return {"message": "student access granted"}


@app.post("/warden")
def admin(user = Depends(getuser)):
    if user["role"] != "warden":
        raise HTTPException(status_code=401 , detail="Only warden are allowed here")
    
    return {"message": "warden access granted"}



@app.post("/admin/Register")
def register(new_user : dict,user = Depends(getuser)):

    if user["role"] != "admin":
        raise HTTPException(status_code=401 , detail="Only admins are allowed to register ")
    
    name = new_user["name"]
    email = new_user["email"]
    password = new_user["password"]
    role = new_user["role"]
    cur = connect.cursor()

    cur.execute("SELECT * FROM users WHERE name=%s",(name,))
    existing = cur.fetchone()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    

    cur.execute(
        "INSERT INTO users (name,email,password,role) VALUES (%s,%s,%s,%s)",
        (name,email,password,role)
    )
    connect.commit()
    cur.close()
    return {"message":"User registered successfully"}
    
