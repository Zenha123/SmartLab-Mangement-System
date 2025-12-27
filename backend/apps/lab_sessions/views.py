from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import LabSession
from .serializers import LabSessionSerializer
from apps.students.models import Attendance


class LabSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for Lab Session management"""
    queryset = LabSession.objects.all()
    serializer_class = LabSessionSerializer
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
    
    def perform_create(self, serializer):
        """Auto-assign faculty when creating session"""
        serializer.save(faculty=self.request.user)
    
    @action(detail=True, methods=['post'])
    def end_session(self, request, pk=None):
        """End the lab session"""
        session = self.get_object()
        session.end_session()
        return Response({
            'status': 'Session ended',
            'duration_minutes': session.duration_minutes
        })
    
    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        """Get attendance for this session"""
        session = self.get_object()
        attendance_records = session.attendance_records.all()
        
        from apps.students.serializers import AttendanceSerializer
        serializer = AttendanceSerializer(attendance_records, many=True)
        return Response(serializer.data)
