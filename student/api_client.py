import requests

BASE_URL = "http://127.0.0.1:8001/api/student/login/"

ACCESS_TOKEN = None
REFRESH_TOKEN = None

def login_student(student_id, password):
    global ACCESS_TOKEN, REFRESH_TOKEN
    try:
        response = requests.post(
            BASE_URL,
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

def logout_student():
    global ACCESS_TOKEN, REFRESH_TOKEN
    ACCESS_TOKEN = None
    REFRESH_TOKEN = None
