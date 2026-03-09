"""
API Client for Smart Lab Management System
Handles all HTTP requests to Django backend with JWT authentication
"""
import os
import webbrowser
import subprocess
import requests
from typing import Dict, Optional, Any


class APIClient:
    """HTTP API client with JWT authentication"""

    def __init__(self, base_url: str = "http://localhost:8000/api"):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.faculty_info: Optional[Dict] = None

    def _get_headers(self, json_content: bool = True) -> Dict[str, str]:
        """Get request headers with JWT token"""
        headers = {}
        if json_content:
            headers["Content-Type"] = "application/json"
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Generic request handler with auto-refresh token support"""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = kwargs.pop("headers", self._get_headers())

        response = requests.request(method, url, headers=headers, timeout=20, **kwargs)

        # If 401, try refresh token once
        if response.status_code == 401 and self.refresh_token:
            if self.refresh_access_token():
                headers = self._get_headers()
                response = requests.request(method, url, headers=headers, timeout=20, **kwargs)

        return response

    def get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        return self._request("POST", endpoint, json=data)

    def patch(self, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        return self._request("PATCH", endpoint, json=data)

    def put(self, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        return self._request("PUT", endpoint, json=data)

    def delete(self, endpoint: str) -> requests.Response:
        return self._request("DELETE", endpoint)

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
                try:
                    error_msg = response.json().get("error", "Login failed")
                except Exception:
                    error_msg = f"Login failed (HTTP {response.status_code})"
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
        except Exception:
            return False

    def get_semesters(self) -> Dict[str, Any]:
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

    def get_faculty_weekly_timetable(self) -> Dict[str, Any]:
        try:
            response = requests.get(
                f"{self.base_url}/auth/timetable/weekly/",
                headers=self._get_headers(),
                timeout=10
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json(), "error": None}
            return {"success": False, "data": None, "error": "Failed to fetch faculty timetable"}
        except Exception as e:
            return {"success": False, "data": None, "error": str(e)}

    def get_batches(self, semester_id: Optional[int] = None) -> Dict[str, Any]:
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
                if isinstance(data, dict) and 'results' in data:
                    return {"success": True, "data": data['results'], "error": None}
                return {"success": True, "data": data, "error": None}
            return {"success": False, "data": None, "error": "Failed to fetch students"}
        except Exception as e:
            return {"success": False, "data": None, "error": str(e)}

    def start_lab_session(self, batch_id: int, session_type: str = "regular", subject_name: str = "") -> Dict[str, Any]:
        try:
            response = requests.post(
                f"{self.base_url}/sessions/",
                json={"batch": batch_id, "session_type": session_type, "subject_name": subject_name},
                headers=self._get_headers(),
                timeout=10
            )

            if response.status_code == 201:
                return {"success": True, "data": response.json(), "error": None}

            try:
                error_data = response.json()
                error_msg = str(error_data)
            except Exception:
                error_msg = f"Failed to start session (HTTP {response.status_code})"

            return {"success": False, "data": None, "error": error_msg}
        except Exception as e:
            return {"success": False, "data": None, "error": str(e)}

    def end_lab_session(self, session_id: int) -> Dict[str, Any]:
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

    def create_task(self, batch_id: int, title: str, description: str, subject_name: str = "", deadline: Optional[str] = None) -> Dict[str, Any]:
        try:
            payload = {
                "batch": batch_id,
                "title": title,
                "subject_name": subject_name,
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
        try:
            url = f"{self.base_url}/reports/attendance/"
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

    # -----------------------------
    # PDF REPORT DOWNLOAD METHODS
    # -----------------------------
    def download_pdf_to_path(self, endpoint: str, save_path: str) -> Dict[str, Any]:
        try:
            response = requests.get(
                f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}",
                headers=self._get_headers(json_content=False),
                timeout=30
            )

            if response.status_code != 200:
                try:
                    err = response.json()
                    msg = err.get("detail") or str(err)
                except Exception:
                    msg = f"Failed to download PDF (HTTP {response.status_code})"
                return {"success": False, "path": None, "error": msg}

            with open(save_path, "wb") as f:
                f.write(response.content)

            return {"success": True, "path": save_path, "error": None}
        except Exception as e:
            return {"success": False, "path": None, "error": str(e)}

    def download_student_submission_report_pdf_to_path(self, student_id: int, save_path: str) -> Dict[str, Any]:
        return self.download_pdf_to_path(
            f"reports/submissions/student/{student_id}/pdf/",
            save_path
        )

    def download_batch_submission_report_pdf_to_path(self, batch_id: int, save_path: str) -> Dict[str, Any]:
        return self.download_pdf_to_path(
            f"reports/submissions/batch/{batch_id}/pdf/",
            save_path
        )

    def open_file(self, file_path: str) -> Dict[str, Any]:
        try:
            if os.name == "nt":
                os.startfile(file_path)
            elif os.name == "posix":
                try:
                    subprocess.Popen(["xdg-open", file_path])
                except Exception:
                    webbrowser.open(f"file://{file_path}")
            else:
                webbrowser.open(f"file://{file_path}")

            return {"success": True, "error": None}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def open_pdf_in_browser(self, file_path: str) -> Dict[str, Any]:
        try:
            import pathlib
            file_url = pathlib.Path(file_path).resolve().as_uri()
            webbrowser.open(file_url)
            return {"success": True, "error": None}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def is_authenticated(self) -> bool:
        return self.access_token is not None

    def logout(self):
        self.access_token = None
        self.refresh_token = None
        self.faculty_info = None