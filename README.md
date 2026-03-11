# 🏠 Hostel Management System

A comprehensive REST API for managing hostel operations built with FastAPI, featuring role-based authentication and room management workflows.

## 🌐 Live API

**📚 Interactive Docs**: http://13.204.77.154:8000/docs  
**📋 OpenAPI Schema**: http://13.204.77.154:8000/openapi.json

admin Credentials :

raza
123456789

{
  "username": "raza",
  "password": "123456789"
}
## ✨ Features

- **Role-Based Authentication**: Admin, Student, and Warden roles with JWT tokens
- **User Management**: Admin can register users with different roles  
- **Room Management**: Add rooms, track capacity and availability
- **Request Workflow**: Students request rooms → Wardens approve/reject
- **Real-time Status**: Track room occupancy and request status
- **Input Validation**: Comprehensive error handling and data validation

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (Neon Cloud)
- **Authentication**: JWT (JSON Web Tokens)
- **Deployment**: Docker + AWS EC2
- **Documentation**: Auto-generated Swagger UI

## 📡 API Endpoints

### 🔐 Authentication
- `POST /login` - User login (returns JWT token)

### 👨‍💼 Admin Endpoints (`/admin/`)
- `POST /admin/` - Admin access check
- `POST /admin/register` - Register new users (admin, student, warden)
- `POST /admin/rooms` - Add new rooms
- `GET /admin/rooms/all` - View all rooms

### 🎓 Student Endpoints (`/student/`)
- `POST /student/` - Student access check
- `GET /student/rooms` - View available rooms
- `POST /student/request-room` - Request a room
- `GET /student/my-request` - View own requests

### 👮‍♂️ Warden Endpoints (`/warden/`)
- `POST /warden/` - Warden access check
- `GET /warden/room-requests` - View pending requests
- `PUT /warden/approve-request/{req_id}` - Approve room request
- `PUT /warden/reject-request/{req_id}` - Reject room request

## 🚀 Quick Start

### Using the Live API

1. **Access API Documentation**: http://13.204.77.154:8000/docs
2. **Test Login Endpoint**:
   ```bash
   curl -X POST "http://13.204.77.154:8000/login" \
   -H "Content-Type: application/json" \
   -d '{"username": "your_username", "password": "your_password"}'
   ```

### Local Development Setup

1. **Clone Repository**:
   ```bash
   git clone <your-repo-url>
   cd hostel-management-system
   ```

2. **Environment Setup**:
   ```bash
   cp .env.example .env
   # Edit .env with your database URL and JWT secrets
   ```

3. **Run with Docker**:
   ```bash
   docker-compose up --build
   ```

4. **Access Locally**:
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs

## 🔧 Environment Variables

Create a `.env` file with:

```env
ALGORITHM=HS256
SECURITY_KEY=your_jwt_secret_key_here
dburl=postgresql://username:password@host:port/database
```

## 🏗️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(100),
    role VARCHAR(20)  -- 'admin', 'student', 'warden'
);
```

### Rooms Table
```sql
CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    room_number INT UNIQUE,
    capacity INT,
    occupied INT DEFAULT 0,
    status VARCHAR(20)  -- 'available', 'full'
);
```

### Room Requests Table
```sql
CREATE TABLE room_requests (
    id SERIAL PRIMARY KEY,
    student_id INT REFERENCES users(id),
    room_id INT REFERENCES rooms(id),
    status VARCHAR(20) DEFAULT 'pending'  -- 'pending', 'approved', 'rejected'
);
```

## 📱 Usage Examples

### 1. Admin Registration Workflow
```bash
# 1. Login as admin
curl -X POST "http://13.204.77.154:8000/login" \
-H "Content-Type: application/json" \
-d '{"username": "admin", "password": "admin_password"}'

# 2. Register a student (use token from step 1)
curl -X POST "http://13.204.77.154:8000/admin/register" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_JWT_TOKEN" \
-d '{
  "name": "John Doe",
  "email": "john@example.com", 
  "password": "student123",
  "role": "student"
}'
```

### 2. Room Management
```bash
# Add a room (admin only)
curl -X POST "http://13.204.77.154:8000/admin/rooms" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_JWT_TOKEN" \
-d '{
  "room_number": 101,
  "capacity": 2
}'
```

### 3. Student Request Flow
```bash
# 1. Student views available rooms
curl -H "Authorization: Bearer STUDENT_TOKEN" \
"http://13.204.77.154:8000/student/rooms"

# 2. Student requests a room
curl -X POST "http://13.204.77.154:8000/student/request-room" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer STUDENT_TOKEN" \
-d '{"room_id": 1}'
```

### 4. Warden Approval
```bash
# 1. View pending requests
curl -H "Authorization: Bearer WARDEN_TOKEN" \
"http://13.204.77.154:8000/warden/room-requests"

# 2. Approve a request
curl -X PUT "http://13.204.77.154:8000/warden/approve-request/1" \
-H "Authorization: Bearer WARDEN_TOKEN"
```

## 🚢 Deployment

### AWS EC2 Deployment
The application is deployed on AWS EC2 using Docker:

1. **EC2 Instance**: Ubuntu 22.04 LTS
2. **Docker**: Containerized FastAPI application
3. **Database**: External PostgreSQL (Neon Cloud)
4. **Security**: AWS Security Groups configured for port 8000

### Deployment Commands
```bash
# On EC2 instance
git clone <your-repo>
cd hostel-management-system
nano .env  # Add your environment variables
docker-compose up --build -d
```

## 📊 API Response Examples

### Successful Login
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Error Response
```json
{
  "detail": "Invalid credentials"
}
```

### Room List
```json
[
  {
    "id": 1,
    "room_number": 101,
    "capacity": 2,
    "occupied": 0,
    "status": "available"
  }
]
```

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Different permissions for admin, student, warden
- **Input Validation**: Comprehensive request validation
- **Password Security**: Environment-based JWT secrets
- **HTTPS Ready**: Can be configured with SSL certificates

## 🛡️ Error Handling

The API provides detailed error responses:
- `400 Bad Request` - Invalid input data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server-side errors

## 📚 Documentation

- **Interactive API Docs**: http://13.204.77.154:8000/docs
- **ReDoc Format**: http://13.204.77.154:8000/redoc
- **OpenAPI JSON**: http://13.204.77.154:8000/openapi.json

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Raza Shaikh**  
- 🌐 Live API: http://13.204.77.154:8000
- 📧 Contact: [Your Email]
- 🔗 GitHub: [Your GitHub Profile]

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Neon for cloud PostgreSQL hosting
- AWS for reliable cloud infrastructure
- Docker for containerization

---

⭐ **Star this repository if you found it helpful!**

🚀 **API Status**: Live and Running at http://13.204.77.154:8000/docs