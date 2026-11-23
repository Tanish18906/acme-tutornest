import os
import sqlite3
from typing import Any, Dict, List, Optional

def get_db_path() -> str:
    db_env = os.environ.get("TUTORNEST_DB")
    if db_env:
        return db_env
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "demo.db")

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

# PLANTED V4: Aadhaar and parent_pan stored in plaintext columns without column-level encryption or tokens
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT NOT NULL,
        dob TEXT NOT NULL,
        age INTEGER NOT NULL,
        aadhaar TEXT NOT NULL,
        parent_pan TEXT,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'student',
        is_deleted INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students_backup (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        dob TEXT NOT NULL,
        age INTEGER NOT NULL,
        aadhaar TEXT NOT NULL,
        parent_pan TEXT,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'student',
        is_deleted INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def all_students() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, email, phone, dob, age, aadhaar, parent_pan, role, is_deleted, created_at 
        FROM students 
        WHERE is_deleted = 0
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_student(student_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, email, phone, dob, age, aadhaar, parent_pan, role, is_deleted, created_at 
        FROM students 
        WHERE id = ? AND is_deleted = 0
    """, (student_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_student_by_email(email: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE email = ? AND is_deleted = 0", (email,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def insert_student(data: Dict[str, Any]) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO students (name, email, phone, dob, age, aadhaar, parent_pan, password_hash, role, is_deleted, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
    """, (
        data["name"],
        data["email"],
        data["phone"],
        data["dob"],
        data["age"],
        data["aadhaar"],
        data.get("parent_pan"),
        data["password_hash"],
        data.get("role", "student"),
        data["created_at"]
    ))
    student_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return student_id

def delete_student(student_id: int) -> bool:
    # PLANTED V7
    # Soft-delete: only sets is_deleted=1 and duplicates the full row into students_backup
    # Leaves PII in both tables indefinitely in violation of DPDP s8(7)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    row_dict = dict(row)
    cursor.execute("""
        INSERT INTO students_backup (name, email, phone, dob, age, aadhaar, parent_pan, password_hash, role, is_deleted, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
    """, (
        row_dict["name"], row_dict["email"], row_dict["phone"], row_dict["dob"],
        row_dict["age"], row_dict["aadhaar"], row_dict["parent_pan"],
        row_dict["password_hash"], row_dict["role"], row_dict["created_at"]
    ))
    cursor.execute("UPDATE students SET is_deleted=1 WHERE id=?", (student_id,))
    conn.commit()
    conn.close()
    return True
