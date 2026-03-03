from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from apps.students.models import Student


class StudentLoginView(APIView):
    permission_classes = []  # Allow unauthenticated

    def post(self, request):
        student_id = request.data.get("student_id")
        password = request.data.get("password")

        if not student_id or not password:
            return Response(
                {"error": "Student ID and password required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(
            request,
            faculty_id=student_id,
            password=password
        )

        if not user:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            return Response(
                {"error": "Not a student account"},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "student": {
                "student_id": student.student_id,
                "name": student.name,
                "batch": str(student.batch),
            }
        })


