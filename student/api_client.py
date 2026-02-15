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

        #pass real backkend error to ui
        try:
            error_msg = response.json().get("error", "Login failed")
        except Exception:
            error_msg = response.text
        
        return {
            "success": False,
            "error": error_msg
        }

    except requests.exceptions.RequestException:
        return {
            "success": False,
            "error": "Cannot connect to server"
        }
    '''try:
        payload = {
            "student_id": student_id,
            "password": password
        }

        print("DEBUG payload:", payload)

        response = requests.post(
            BASE_URL,
            json=payload,
            timeout=5
        )

        print("DEBUG status code:", response.status_code)
        print("DEBUG response:", response.text)

        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "access": data["access"],
                "refresh": data["refresh"],
                "student": data["student"]
            }

        return {
            "success": False,
            "error": response.text
        }

    except requests.exceptions.RequestException as e:
        print("DEBUG exception:", e)
        return {
            "success": False,
            "error": "Cannot connect to server"
        }'''


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
