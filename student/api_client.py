import requests

API_BASE = "http://127.0.0.1:8000/api"

ACCESS_TOKEN = None
REFRESH_TOKEN = None

def login_student(student_id, password):
    global ACCESS_TOKEN, REFRESH_TOKEN
    try:
        response = requests.post(
            f"{API_BASE}/student/login/",
            json={
                "student_id": student_id,
                "password": password
            },
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            ACCESS_TOKEN = data["access"]
            REFRESH_TOKEN = data["refresh"]
            return {
                "success": True,
                "student": data["student"]
            }

        return {
            "success": False,
            "error": "Invalid credentials from server"
        }

    except requests.exceptions.RequestException:
        return {
            "success": False,
            "error": "Cannot connect to server"
        }

def auth_headers():
    if not ACCESS_TOKEN:
        return {}
    return {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

def get_student_tasks():
    """Fetch tasks for the logged-in student"""
    try:
        response = requests.get(
            f"{API_BASE}/student/tasks/",
            headers=auth_headers(),
            timeout=5
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "tasks": response.json()
            }
        return {
            "success": False,
            "error": f"Failed to fetch tasks: {response.status_code}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def logout_student():
    global ACCESS_TOKEN, REFRESH_TOKEN
    ACCESS_TOKEN = None
    REFRESH_TOKEN = None
