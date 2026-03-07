from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.decorators import authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Student, Attendance
from .serializers import StudentSerializer, AttendanceSerializer
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from .services.etlab_sync import (
    sync_faculty_from_etlab,
    sync_students_from_etlab,
    sync_timetable_from_etlab,
)


def _is_valid_service_token(request):
    expected = (settings.ETLAB_SERVICE_TOKEN or "").strip()

    auth_header = request.headers.get("Authorization", "")
    parts = auth_header.strip().split()
    if len(parts) == 2:
        scheme, token = parts
        if scheme.lower() == "bearer" and token.strip() == expected:
            return True, None

    fallback = (request.headers.get("X-Service-Token", "") or "").strip()
    if fallback and fallback == expected:
        return True, None

    if not auth_header and not fallback:
        return False, "Missing service token"
    return False, "Invalid service token"



class StudentViewSet(viewsets.ModelViewSet):
    """ViewSet for Student CRUD with real-time status"""
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        batch_id = self.request.query_params.get('batch', None)
        status_filter = self.request.query_params.get('status', None)
        
        if batch_id:
            queryset = queryset.filter(batch_id=batch_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def mark_online(self, request, pk=None):
        """Mark student as online"""
        student = self.get_object()
        student.mark_online()
        return Response({'status': 'Student marked online'})
    
    @action(detail=True, methods=['post'])
    def mark_offline(self, request, pk=None):
        """Mark student as offline"""
        student = self.get_object()
        student.mark_offline()
        return Response({'status': 'Student marked offline'})
    
    @action(detail=True, methods=['post'])
    def set_mode(self, request, pk=None):
        """Change student mode"""
        student = self.get_object()
        mode = request.data.get('mode')
        if mode:
            student.set_mode(mode)
            return Response({'status': f'Mode changed to {mode}'})
        return Response({'error': 'Mode not provided'}, status=status.HTTP_400_BAD_REQUEST)


class AttendanceViewSet(viewsets.ModelViewSet):
    """ViewSet for Attendance records"""
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        student_id = self.request.query_params.get('student', None)
        session_id = self.request.query_params.get('session', None)
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        
        return queryset
    
class StudentLoginView(APIView):
    def post(self, request):
        student_id = request.data.get("student_id")
        password = request.data.get("password")

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
            student = user.student_profile
        except Student.DoesNotExist:
            return Response(
                {"error": "Student profile not found"},
                status=status.HTTP_404_NOT_FOUND
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


class studentMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student = Student.objects.get(user=request.user)
        return Response({
            "student_id": student.student_id,
            "name": student.name,
            "batch": str(student.batch),
        })
    
'''@api_view(['GET'])
@permission_classes([IsAuthenticated])  # faculty only later
def online_students_count(request):
    count = Student.objects.filter(status='online').count()
    return Response({
        "online_count": count
    })'''


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def sync_faculty_now(request):
    ok, reason = _is_valid_service_token(request)
    if not ok:
        return Response({"detail": reason}, status=status.HTTP_401_UNAUTHORIZED)

    result = sync_faculty_from_etlab()
    return Response(result, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def sync_students_now(request):
    ok, reason = _is_valid_service_token(request)
    if not ok:
        return Response({"detail": reason}, status=status.HTTP_401_UNAUTHORIZED)

    result = sync_students_from_etlab()
    return Response(result, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def sync_timetable_now(request):
    ok, reason = _is_valid_service_token(request)
    if not ok:
        return Response({"detail": reason}, status=status.HTTP_401_UNAUTHORIZED)

    result = sync_timetable_from_etlab()
    return Response(result, status=status.HTTP_200_OK)
