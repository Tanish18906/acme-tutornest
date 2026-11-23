import os
import time
import pytest
import httpx
from stdnum.verhoeff import calc_check_digit

BASE_URL = os.environ.get("TUTORNEST_BASE_URL") or os.environ.get("TARGET_URL") or "http://localhost:8000"

def get_client():
    """Returns an HTTP client configured for testing."""
    try:
        # Check if the HTTP server is alive at BASE_URL
        r = httpx.get(f"{BASE_URL}/health", timeout=1.0)
        if r.status_code == 200:
            return httpx.Client(base_url=BASE_URL, timeout=5.0)
    except Exception:
        pass
    
    # No server running: use the app in process (see _in_process_app).
    from fastapi.testclient import TestClient
    return TestClient(_in_process_app())

_in_process = {}

def _in_process_app():
    """The app on a freshly seeded temp database, made once per run. The tests then need no demo.db (it is git-ignored, so a
    clone does not have one) and never write to it."""
    if "app" not in _in_process:
        import atexit, shutil, sys, tempfile
        backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        tmp = tempfile.mkdtemp(prefix="tutornest-test-")
        atexit.register(shutil.rmtree, tmp, ignore_errors=True)
        os.environ["TUTORNEST_DB"] = os.path.join(tmp, "test.db")  # read by app.db.get_db_path, also by seed.seed()
        import seed
        seed.seed()
        from app.main import app
        _in_process["app"] = app
    return _in_process["app"]

def make_synthetic_aadhaar():
    base = f"8{int(time.time()*1000)%10000000000:010d}"
    return base + calc_check_digit(base)

@pytest.fixture
def client():
    c = get_client()
    yield c
    if hasattr(c, "close"):
        c.close()

def test_signup_works(client):
    unique_id = int(time.time() * 1000)
    payload = {
        "name": f"Test Student {unique_id}",
        "email": f"test_{unique_id}@example.test",
        "phone": f"98{unique_id % 100000000:08d}",
        "dob": "2003-05-15",
        "age": 21,
        "aadhaar": make_synthetic_aadhaar(),
        "parent_pan": "TESTP1234T",
        "password": "Password123!"
    }
    r = client.post("/api/signup", json=payload)
    assert r.status_code == 201, f"Signup failed: {r.text}"
    data = r.json()
    assert "id" in data
    assert data["email"] == payload["email"]
    assert "message" in data

def test_login_works(client):
    r = client.post("/api/login", json={
        "email": "aarav.sharma@example.test",
        "password": "StudentPass123!"
    })
    assert r.status_code == 200, f"Login failed: {r.text}"
    data = r.json()
    assert "access_token" in data
    assert data["token_type"].lower() == "bearer"
    assert data["user"]["email"] == "aarav.sharma@example.test"

def test_get_me_returns_own_record(client):
    login_resp = client.post("/api/login", json={
        "email": "aarav.sharma@example.test",
        "password": "StudentPass123!"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = client.get("/api/me", headers=headers)
    assert r.status_code == 200
    user = r.json()
    assert user["email"] == "aarav.sharma@example.test"
    assert user["name"] == "Aarav Sharma"
    assert "password_hash" not in user

def test_admin_students_auth_enforced(client):
    # 1. Unauthenticated request must fail
    r_unauth = client.get("/api/admin/students")
    assert r_unauth.status_code in (401, 403), f"Expected 401/403, got {r_unauth.status_code}"

    # 2. Student token must fail with 403
    login_student = client.post("/api/login", json={
        "email": "aarav.sharma@example.test",
        "password": "StudentPass123!"
    })
    student_token = login_student.json()["access_token"]
    r_forbidden = client.get("/api/admin/students", headers={"Authorization": f"Bearer {student_token}"})
    assert r_forbidden.status_code == 403

    # 3. Admin token must succeed
    login_admin = client.post("/api/login", json={
        "email": "admin@tutornest.test",
        "password": "AdminPass123!"
    })
    admin_token = login_admin.json()["access_token"]
    r_admin = client.get("/api/admin/students", headers={"Authorization": f"Bearer {admin_token}"})
    assert r_admin.status_code == 200
    students = r_admin.json()
    assert isinstance(students, list)
    assert len(students) >= 15

def test_delete_works_for_owner(client):
    # Create a user to delete
    unique_id = int(time.time() * 1000)
    email = f"delete_me_{unique_id}@example.test"
    pwd = "DeletePass123!"
    payload = {
        "name": "Delete Me",
        "email": email,
        "phone": f"97{unique_id % 100000000:08d}",
        "dob": "2002-01-01",
        "age": 22,
        "aadhaar": make_synthetic_aadhaar(),
        "password": pwd
    }
    signup_resp = client.post("/api/signup", json=payload)
    assert signup_resp.status_code == 201
    user_id = signup_resp.json()["id"]

    # Log in as this user
    login_resp = client.post("/api/login", json={"email": email, "password": pwd})
    token = login_resp.json()["access_token"]

    # Delete own profile
    del_resp = client.delete(f"/api/students/{user_id}", headers={"Authorization": f"Bearer {token}"})
    assert del_resp.status_code == 200
    assert del_resp.json().get("success") is True

def test_delete_other_user_forbidden(client):
    # Student 1 cannot delete Student 2
    login_resp = client.post("/api/login", json={
        "email": "aarav.sharma@example.test",
        "password": "StudentPass123!"
    })
    token = login_resp.json()["access_token"]
    del_resp = client.delete("/api/students/3", headers={"Authorization": f"Bearer {token}"})
    assert del_resp.status_code == 403

def test_delete_works_for_admin(client):
    # Admin can delete any user
    unique_id = int(time.time() * 1000)
    email = f"admin_del_{unique_id}@example.test"
    pwd = "AdminDelPass123!"
    payload = {
        "name": "Admin Target",
        "email": email,
        "phone": f"96{unique_id % 100000000:08d}",
        "dob": "2001-02-02",
        "age": 23,
        "aadhaar": make_synthetic_aadhaar(),
        "password": pwd
    }
    signup_resp = client.post("/api/signup", json=payload)
    user_id = signup_resp.json()["id"]

    login_admin = client.post("/api/login", json={
        "email": "admin@tutornest.test",
        "password": "AdminPass123!"
    })
    admin_token = login_admin.json()["access_token"]
    del_resp = client.delete(f"/api/students/{user_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert del_resp.status_code == 200
    assert del_resp.json().get("success") is True
