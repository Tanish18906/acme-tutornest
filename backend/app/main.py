import os
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from . import db
from .auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    get_admin_user,
)

# Configure logging to write to tutornest.log
log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tutornest.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("tutornest")

app = FastAPI(title="TutorNest API", version="1.0.0")

app.add_middleware(  # PLANTED V11: synthetic, planted for the scanner demo (wildcard origin with credentials)
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    db.init_db()

class SignupRequest(BaseModel):
    name: str
    email: str
    phone: str
    dob: str
    age: int
    aadhaar: str
    parent_pan: Optional[str] = None
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "TutorNest API"}

# PLANTED V1
@app.get("/api/students")
def list_students_public():
    rows = db.all_students()   # returns name, phone, dob, aadhaar, parent_pan
    return rows

# PLANTED V2
@app.get("/api/students/{student_id}")
def get_student(student_id: int, user=Depends(get_current_user)):
    student = db.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.post("/api/signup", status_code=201)
def signup(req: SignupRequest):
    # PLANTED V8  (no parental consent check)
    # The application accepts minor signup without verifying identifiable parental consent

    existing = db.get_student_by_email(req.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # PLANTED V3
    logger.info("signup email=%s aadhaar=%s", req.email, req.aadhaar)

    student_data = {
        "name": req.name,
        "email": req.email,
        "phone": req.phone,
        "dob": req.dob,
        "age": req.age,
        "aadhaar": req.aadhaar,
        "parent_pan": req.parent_pan,
        "password_hash": hash_password(req.password),
        "role": "student",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    student_id = db.insert_student(student_data)
    return {
        "id": student_id,
        "name": req.name,
        "email": req.email,
        "message": "Student created successfully"
    }

@app.post("/api/login")
def login(req: LoginRequest):
    user = db.get_student_by_email(req.email)
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    token = create_access_token(data={"sub": user["email"], "role": user["role"], "id": user["id"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    }

@app.get("/api/me")
def get_me(current_user: dict = Depends(get_current_user)):
    safe_profile = {k: v for k, v in current_user.items() if k != "password_hash"}
    return safe_profile

@app.get("/api/admin/students")
def get_admin_students(admin_user: dict = Depends(get_admin_user)):
    return db.all_students()

@app.delete("/api/students/{student_id}")
def delete_student(student_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin" and current_user["id"] != student_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete other student")
    
    deleted = db.delete_student(student_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"success": True, "message": f"Student {student_id} deleted"}

@app.get("/notice")
def get_notice():
    notice_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "notice.html")
    if not os.path.exists(notice_path):
        raise HTTPException(status_code=404, detail="Notice file not found")
    return FileResponse(notice_path, media_type="text/html")
