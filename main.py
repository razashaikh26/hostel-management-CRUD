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

    security_key = os.getenv("SECURITY_KEY")
    algorithm = os.getenv("ALGORITHM")

    cur = connect.cursor()
    cur.execute(
        "SELECT id, name, password, role FROM users WHERE name = %s",
        (username,)
    )
    user = cur.fetchone()

    if user is None:
        raise HTTPException(status_code=401, detail="No user found")
    user_id, db_username, db_password, db_role = user

    if db_password != password:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    token = jwt.encode(
        {"id": user_id, "username": db_username, "role": db_role},
        security_key,
        algorithm=algorithm
    )
    cur.close()
    return {"access_token": token}
    

@app.post("/admin/")
def admin(user = Depends(getuser)):
    if user["role"] != "admin":
        raise HTTPException(status_code=401 , detail="Only admins are allowed here")
    
    return {"message": "Admin access granted"}


@app.post("/student/")
def student(user = Depends(getuser)):
    if user["role"] != "student":
        raise HTTPException(status_code=401 , detail="Only students are allowed here")
    
    return {"message": "student access granted"}


@app.post("/warden/")
def warden(user = Depends(getuser)):
    if user["role"] != "warden":
        raise HTTPException(status_code=401 , detail="Only warden are allowed here")
    
    return {"message": "warden access granted"}



@app.post("/admin/register")
def register(new_user : dict,user = Depends(getuser)):

    if user["role"] != "admin":
        raise HTTPException(status_code=401 , detail="Only admins are allowed to register ")
    
    # Validate required fields
    required_fields = ["name", "email", "password", "role"]
    for field in required_fields:
        if field not in new_user:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    name = new_user["name"]
    email = new_user["email"]
    password = new_user["password"]
    role = new_user["role"]

    valid_roles = ["admin", "student", "warden"]
    if role not in valid_roles:
        raise HTTPException(status_code=400, detail="Invalid role. Must be admin, student, or warden")
    
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
    
@app.post("/admin/rooms")
def add_room(room: dict, user=Depends(getuser)):

    if user["role"] != "admin":
        raise HTTPException(status_code=401, detail="Admin only")
    
    # Validate required fields
    if "room_number" not in room:
        raise HTTPException(status_code=400, detail="Missing required field: room_number")
    if "capacity" not in room:
        raise HTTPException(status_code=400, detail="Missing required field: capacity")

    try:
        capacity = int(room["capacity"])
        if capacity <= 0:
            raise HTTPException(status_code=400, detail="Capacity must be greater than 0")
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Capacity must be a valid number")
    
    cur = connect.cursor()
    
    cur.execute("SELECT * FROM rooms WHERE room_number=%s", (room["room_number"],))
    existing = cur.fetchone()
    if existing:
        cur.close()
        raise HTTPException(status_code=400, detail="Room number already exists")
    
    cur.execute(
        "INSERT INTO rooms (room_number,capacity,status) VALUES (%s,%s,%s)",
        (room["room_number"], capacity, "available")
    )

    connect.commit()
    cur.close()
    return {"message": "Room added"}

@app.get("/admin/rooms/all")
def view_all_rooms(user=Depends(getuser)):

    if user["role"] != "admin":
        raise HTTPException(status_code=401)
    cur = connect.cursor()
    cur.execute("SELECT * FROM rooms")
    rooms = cur.fetchall()
    cur.close()
    return rooms

@app.get("/student/rooms")
def view_rooms(user=Depends(getuser)):

    if user["role"] != "student":
        raise HTTPException(status_code=401)
    cur = connect.cursor()
    cur.execute("SELECT * FROM rooms WHERE status='available'")
    rooms = cur.fetchall()
    cur.close()

    return rooms


@app.post("/student/request-room")
def request_room(data: dict, user=Depends(getuser)):

    if user["role"] != "student":
        raise HTTPException(status_code=401)
    
    if "room_id" not in data:
        raise HTTPException(status_code=400, detail="Missing required field: room_id")
    
    cur = connect.cursor()

    cur.execute("SELECT * FROM rooms WHERE id=%s AND status='available'", (data["room_id"],))
    room = cur.fetchone()
    if not room:
        cur.close()
        raise HTTPException(status_code=400, detail="Room not found or not available")
    
    cur.execute(
        "INSERT INTO room_requests (student_id,room_id,status) VALUES (%s,%s,%s)",
        (user["id"], data["room_id"], "pending")
    )

    connect.commit()
    cur.close()
    return {"message": "Room request sent"}

@app.get("/student/my-request")
def my_request(user=Depends(getuser)):

    if user["role"] != "student":
        raise HTTPException(status_code=401)
    cur = connect.cursor()
    cur.execute(
        "SELECT * FROM room_requests WHERE student_id=%s",
        (user["id"],)
    )

    request = cur.fetchall()
    cur.close()
    return request

@app.get("/warden/room-requests")
def view_requests(user=Depends(getuser)):

    if user["role"] != "warden":
        raise HTTPException(status_code=401)
    cur = connect.cursor()
    cur.execute("SELECT * FROM room_requests WHERE status='pending'")
    requests = cur.fetchall()
    cur.close()
    return requests

@app.put("/warden/approve-request/{req_id}")
def approve_request(req_id: int, user=Depends(getuser)):

    if user["role"] != "warden":
        raise HTTPException(status_code=401)
    cur = connect.cursor()
    cur.execute(
        "UPDATE room_requests SET status='approved' WHERE id=%s",
        (req_id,)
    )

    connect.commit()
    cur.close()

    return {"message": "Request approved"}

@app.put("/warden/reject-request/{req_id}")
def reject_request(req_id: int, user=Depends(getuser)):

    if user["role"] != "warden":
        raise HTTPException(status_code=401)
    cur = connect.cursor()
    cur.execute(
        "UPDATE room_requests SET status='rejected' WHERE id=%s",
        (req_id,)
    )

    connect.commit()
    cur.close()

    return {"message": "Request rejected"}