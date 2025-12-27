"""
Global API client instance
Shared across all screens for consistent authentication
"""
from api.client import APIClient

# Singleton API client instance
api_client = APIClient()
