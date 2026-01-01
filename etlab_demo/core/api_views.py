from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Student
from .serializers import studentSerializer

@api_view(['GET'])
def student_list(request):
    students = Student.objects.all()
    serializer = studentSerializer(students, many=True)
    return Response(serializer.data)