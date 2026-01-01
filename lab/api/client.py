"""
API Client for Smart Lab Management System
Handles all HTTP requests to Django backend with JWT authentication
"""
import requests
from typing import Dict, List, Optional, Any
import json


class APIClient:
    """HTTP API client with JWT authentication"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api"):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.faculty_info: Optional[Dict] = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with JWT token"""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    def login(self, faculty_id: str, password: str) -> Dict[str, Any]:
        """
        Login faculty and store JWT tokens
        Returns: {"success": bool, "data": dict, "error": str}
        """
        try:
            response = requests.post(
                f"{self.base_url}/auth/login/",
                json={"faculty_id": faculty_id, "password": password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access")
                self.refresh_token = data.get("refresh")
                self.faculty_info = data.get("faculty")
                return {"success": True, "data": data, "error": None}
            else:
                error_msg = response.json().get("error", "Login failed")
                return {"success": False, "data": None, "error": error_msg}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": None, "error": f"Connection error: {str(e)}"}
    
    def refresh_access_token(self) -> bool:
        """Refresh the access token using refresh token"""
        if not self.refresh_token:
            return False
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/refresh/",
                json={"refresh": self.refresh_token},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access")
                return True
            return False
        except:
            return False
    
    def get_semesters(self) -> Dict[str, Any]:
        """Get list of all semesters"""
        try:
            response = requests.get(
                f"{self.base_url}/semesters/",
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json(), "error": None}
            return {"success": False, "data": None, "error": "Failed to fetch semesters"}
        except Exception as e:
            return {"success": False, "data": None, "error": str(e)}
    
    def get_batches(self, semester_id: Optional[int] = None) -> Dict[str, Any]:
        """Get batches, optionally filtered by semester"""
        try:
            url = f"{self.base_url}/batches/"
            if semester_id:
                url += f"?semester={semester_id}"
            
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                return {"success": True, "data": response.json(), "error": None}
            return {"success": False, "data": None, "error": "Failed to fetch batches"}
        except Exception as e:
            return {"success": False, "data": None, "error": str(e)}
    
    def get_students(self, batch_id: Optional[int] = None, status: Optional[str] = None) -> Dict[str, Any]:
        """Get students, optionally filtered by batch and status"""
        try:
            url = f"{self.base_url}/students/"
            params = []
            if batch_id:
                params.append(f"batch={batch_id}")
            if status:
                params.append(f"status={status}")
            
            if params:
                url += "?" + "&".join(params)
            
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Handle paginated response
                if isinstance(data, dict) and 'results' in data:
                    return {"success": True, "data": data['results'], "error": None}
                return {"success": True, "data": data, "error": None}
            return {"success": False, "data": None, "error": "Failed to fetch students"}
        except Exception as e:
            return {"success": False, "data": None, "error": str(e)}
    
    def start_lab_session(self, batch_id: int, session_type: str = "regular") -> Dict[str, Any]:
        """Start a new lab session"""
        try:
            response = requests.post(
                f"{self.base_url}/sessions/",
                json={"batch": batch_id, "session_type": session_type},
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 201:
                return {"success": True, "data": response.json(), "error": None}
            
            # Get actual error message from backend
            try:
                error_data = response.json()
                error_msg = str(error_data)
            except:
                error_msg = f"Failed to start session (HTTP {response.status_code})"
            
            return {"success": False, "data": None, "error": error_msg}
        except Exception as e:
            return {"success": False, "data": None, "error": str(e)}
    
    def end_lab_session(self, session_id: int) -> Dict[str, Any]:
        """End an active lab session"""
        try:
            response = requests.post(
                f"{self.base_url}/sessions/{session_id}/end_session/",
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json(), "error": None}
            return {"success": False, "data": None, "error": "Failed to end session"}
        except Exception as e:
            return {"success": False, "data": None, "error": str(e)}
    
    def submit_viva_marks(self, student_id: int, session_id: int, marks: int, notes: str = "") -> Dict[str, Any]:
        """Submit viva marks for a student"""
        try:
            response = requests.post(
                f"{self.base_url}/viva/",
                json={
                    "student": student_id,
                    "session": session_id,
                    "marks": marks,
                    "notes": notes,
                    "status": "completed"
                },
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 201:
                return {"success": True, "data": response.json(), "error": None}
            return {"success": False, "data": None, "error": "Failed to submit viva marks"}
        except Exception as e:
            return {"success": False, "data": None, "error": str(e)}
    
    def create_task(self, batch_id: int, title: str, description: str, deadline: Optional[str] = None) -> Dict[str, Any]:
        """Create a new task for a batch"""
        try:
            payload = {
                "batch": batch_id,
                "title": title,
                "description": description
            }
            if deadline:
                payload["deadline"] = deadline
            
            response = requests.post(
                f"{self.base_url}/tasks/",
                json=payload,
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 201:
                return {"success": True, "data": response.json(), "error": None}
            return {"success": False, "data": None, "error": "Failed to create task"}
        except Exception as e:
            return {"success": False, "data": None, "error": str(e)}
    
    def get_attendance_report(self, batch_id: Optional[int] = None, date: Optional[str] = None) -> Dict[str, Any]:
        """Get attendance report"""
        try:
            url = f"{self.base_url}/evaluation/reports/attendance/"
            params = []
            if batch_id:
                params.append(f"batch={batch_id}")
            if date:
                params.append(f"date={date}")
            
            if params:
                url += "?" + "&".join(params)
            
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                return {"success": True, "data": response.json(), "error": None}
            return {"success": False, "data": None, "error": "Failed to fetch report"}
        except Exception as e:
            return {"success": False, "data": None, "error": str(e)}
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.access_token is not None
    
    def logout(self):
        """Clear authentication tokens"""
        self.access_token = None
        self.refresh_token = None
        self.faculty_info = None
