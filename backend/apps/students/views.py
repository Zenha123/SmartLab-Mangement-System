from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Student, Attendance
from .serializers import StudentSerializer, AttendanceSerializer


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
