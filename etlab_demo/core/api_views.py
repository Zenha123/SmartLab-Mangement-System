from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Student
from .serializers import studentSerializer
from django.conf import settings

def check_service_token(request):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return False

    try:
        scheme, token = auth_header.split()
        return scheme == "Bearer" and token == settings.ETLAB_SERVICE_TOKEN
    except ValueError:
        return False


@api_view(['GET'])
def student_list(request):
    if not check_service_token(request):
        return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
    students = Student.objects.all()
    serializer = studentSerializer(students, many=True)
    return Response(serializer.data)