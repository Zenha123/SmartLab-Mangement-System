import requests
import os

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

def submit_task(task_id, file_path):
    """Submit a task solution file"""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": "File not found"
            }
        
        # Prepare multipart upload
        with open(file_path, 'rb') as f:
            # Use 'file' as the key, consistent with backend view
            files = {'file': (os.path.basename(file_path), f)}
            
            # Note: Do NOT set Content-Type header manually when using 'files'
            headers = auth_headers()
            
            response = requests.post(
                f"{API_BASE}/student/tasks/{task_id}/submit/",
                headers=headers, 
                files=files,
                timeout=20
            )
        
        if response.status_code in (200, 201):
            return {
                "success": True,
                "data": response.json()
            }
        else:
            try:
                error_data = response.json()
                error_msg = error_data.get('error', f"Status {response.status_code}")
            except:
                error_msg = response.text
                
            return {
                "success": False,
                "error": f"Submission failed: {error_msg}"
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
