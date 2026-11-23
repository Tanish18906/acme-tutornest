import os
import random
from datetime import datetime, timezone
from stdnum.verhoeff import calc_check_digit
from stdnum.in_ import aadhaar as aadhaar_tool

from app import db
from app.auth import hash_password

def generate_synthetic_aadhaar(prefix_seed: str) -> str:
    """Generate a 12-digit Aadhaar number starting with 2-9 that passes Verhoeff check."""
    # 11 digits
    partial = prefix_seed
    while len(partial) < 11:
        partial += str(random.randint(0, 9))
    check = calc_check_digit(partial)
    full = partial + check
    assert aadhaar_tool.is_valid(full), f"Generated Aadhaar {full} failed Verhoeff"
    return full

def seed():
    db_path = db.get_db_path()
    if os.path.exists(db_path):
        os.remove(db_path)
    
    db.init_db()

    # 15 synthetic students: 4 minors, 11 adults.
    # 1 admin, 2 known test users
    students_data = [
        # Admin
        {
            "name": "Admin TutorNest",
            "email": "admin@tutornest.test",
            "phone": "9876543210",
            "dob": "1990-05-15",
            "age": 34,
            "aadhaar_prefix": "21345678901",
            "parent_pan": None,
            "password": "AdminPass123!",
            "role": "admin"
        },
        # Known demo normal user 1
        {
            "name": "Aarav Sharma",
            "email": "aarav.sharma@example.test",
            "phone": "9811122233",
            "dob": "2004-03-12",
            "age": 20,
            "aadhaar_prefix": "34567890123",
            "parent_pan": "ABCPS1234A",
            "password": "StudentPass123!",
            "role": "student"
        },
        # Known demo normal user 2
        {
            "name": "Diya Patel",
            "email": "diya.patel@example.test",
            "phone": "8722233344",
            "dob": "2005-08-22",
            "age": 19,
            "aadhaar_prefix": "45678901234",
            "parent_pan": "XYZPP5678B",
            "password": "StudentPass123!",
            "role": "student"
        },
        # Minor 1 (age 14)
        {
            "name": "Kabir Gupta",
            "email": "kabir.gupta@example.test",
            "phone": "7633344455",
            "dob": "2010-11-04",
            "age": 14,
            "aadhaar_prefix": "56789012345",
            "parent_pan": "GUPPK9988C",
            "password": "StudentPass123!",
            "role": "student"
        },
        # Minor 2 (age 15)
        {
            "name": "Ananya Verma",
            "email": "ananya.verma@example.test",
            "phone": "9144455566",
            "dob": "2009-02-18",
            "age": 15,
            "aadhaar_prefix": "67890123456",
            "parent_pan": "VERPV7766D",
            "password": "StudentPass123!",
            "role": "student"
        },
        # Minor 3 (age 16)
        {
            "name": "Rohan Mehra",
            "email": "rohan.mehra@example.test",
            "phone": "8855566677",
            "dob": "2008-07-30",
            "age": 16,
            "aadhaar_prefix": "78901234567",
            "parent_pan": "MEHPR3322E",
            "password": "StudentPass123!",
            "role": "student"
        },
        # Minor 4 (age 17)
        {
            "name": "Isha Singh",
            "email": "isha.singh@example.test",
            "phone": "6966677788",
            "dob": "2007-09-14",
            "age": 17,
            "aadhaar_prefix": "89012345678",
            "parent_pan": "SINPI1100F",
            "password": "StudentPass123!",
            "role": "student"
        },
        # Adult 3
        {
            "name": "Aditya Rao",
            "email": "aditya.rao@example.test",
            "phone": "9877788899",
            "dob": "2003-01-25",
            "age": 21,
            "aadhaar_prefix": "90123456789",
            "parent_pan": "RAOPA4433G",
            "password": "StudentPass123!",
            "role": "student"
        },
        # Adult 4
        {
            "name": "Neha Joshi",
            "email": "neha.joshi@example.test",
            "phone": "7788899900",
            "dob": "2002-12-05",
            "age": 22,
            "aadhaar_prefix": "23456789012",
            "parent_pan": "JOSPN5544H",
            "password": "StudentPass123!",
            "role": "student"
        },
        # Adult 5
        {
            "name": "Vikram Nair",
            "email": "vikram.nair@example.test",
            "phone": "6899900011",
            "dob": "2001-06-19",
            "age": 23,
            "aadhaar_prefix": "34567890124",
            "parent_pan": "NAIPV6655J",
            "password": "StudentPass123!",
            "role": "student"
        },
        # Adult 6
        {
            "name": "Pooja Reddy",
            "email": "pooja.reddy@example.test",
            "phone": "9900011122",
            "dob": "2003-04-10",
            "age": 21,
            "aadhaar_prefix": "45678901235",
            "parent_pan": "REDPP7766K",
            "password": "StudentPass123!",
            "role": "student"
        },
        # Adult 7
        {
            "name": "Siddharth Jain",
            "email": "siddharth.jain@example.test",
            "phone": "8911122244",
            "dob": "2000-10-15",
            "age": 24,
            "aadhaar_prefix": "56789012346",
            "parent_pan": "JAIPS8877L",
            "password": "StudentPass123!",
            "role": "student"
        },
        # Adult 8
        {
            "name": "Meera Iyer",
            "email": "meera.iyer@example.test",
            "phone": "7822233355",
            "dob": "2002-05-28",
            "age": 22,
            "aadhaar_prefix": "67890123457",
            "parent_pan": "IYRPM9988M",
            "password": "StudentPass123!",
            "role": "student"
        },
        # Adult 9
        {
            "name": "Arjun Kapoor",
            "email": "arjun.kapoor@example.test",
            "phone": "6933344466",
            "dob": "2001-09-03",
            "age": 23,
            "aadhaar_prefix": "78901234568",
            "parent_pan": "KAPPA1122N",
            "password": "StudentPass123!",
            "role": "student"
        },
        # Adult 10
        {
            "name": "Kavya Menon",
            "email": "kavya.menon@example.test",
            "phone": "9844455577",
            "dob": "2004-11-20",
            "age": 20,
            "aadhaar_prefix": "89012345679",
            "parent_pan": "MENPK2233P",
            "password": "StudentPass123!",
            "role": "student"
        }
    ]

    for item in students_data:
        val_aadhaar = generate_synthetic_aadhaar(item["aadhaar_prefix"])
        student_row = {
            "name": item["name"],
            "email": item["email"],
            "phone": item["phone"],
            "dob": item["dob"],
            "age": item["age"],
            "aadhaar": val_aadhaar,
            "parent_pan": item["parent_pan"],
            "password_hash": hash_password(item["password"]),
            "role": item["role"],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        db.insert_student(student_row)

    print(f"Successfully seeded {len(students_data)} synthetic students into {db_path}")

if __name__ == "__main__":
    seed()
