from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import VivaRecord, ExamSession, ExamResult, Task, TaskSubmission
from .serializers import (
    VivaRecordSerializer, ExamSessionSerializer, ExamResultSerializer,
    TaskSerializer, TaskSubmissionSerializer
)


class VivaRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for Viva Record management"""
    queryset = VivaRecord.objects.all()
    serializer_class = VivaRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        session_id = self.request.query_params.get('session', None)
        student_id = self.request.query_params.get('student', None)
        
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        return queryset
    
    def perform_create(self, serializer):
        """Auto-assign faculty when creating viva record"""
        serializer.save(faculty=self.request.user)


class ExamSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for Exam Session management"""
    queryset = ExamSession.objects.all()
    serializer_class = ExamSessionSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Get all results for this exam session"""
        exam_session = self.get_object()
        results = exam_session.results.all()
        serializer = ExamResultSerializer(results, many=True)
        return Response(serializer.data)


class ExamResultViewSet(viewsets.ModelViewSet):
    """ViewSet for Exam Result management"""
    queryset = ExamResult.objects.all()
    serializer_class = ExamResultSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        exam_session_id = self.request.query_params.get('exam_session', None)
        student_id = self.request.query_params.get('student', None)
        
        if exam_session_id:
            queryset = queryset.filter(exam_session_id=exam_session_id)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        return queryset


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for Task management"""
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        batch_id = self.request.query_params.get('batch', None)
        
        if batch_id:
            queryset = queryset.filter(batch_id=batch_id)
        
        return queryset
    
    def perform_create(self, serializer):
        """Auto-assign faculty when creating task"""
        serializer.save(faculty=self.request.user)
    
    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        """Get all submissions for this task"""
        task = self.get_object()
        submissions = task.submissions.all()
        serializer = TaskSubmissionSerializer(submissions, many=True)
        return Response(serializer.data)


class TaskSubmissionViewSet(viewsets.ModelViewSet):
    """ViewSet for Task Submission management"""
    queryset = TaskSubmission.objects.all()
    serializer_class = TaskSubmissionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        task_id = self.request.query_params.get('task', None)
        student_id = self.request.query_params.get('student', None)
        
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        return queryset


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attendance_report(request):
    """Generate attendance report"""
    from apps.students.models import Attendance
    from apps.students.serializers import AttendanceSerializer
    
    batch_id = request.query_params.get('batch', None)
    date_filter = request.query_params.get('date', None)
    
    queryset = Attendance.objects.all()
    
    if batch_id:
        queryset = queryset.filter(session__batch_id=batch_id)
    if date_filter:
        queryset = queryset.filter(created_at__date=date_filter)
    
    # Group by date and calculate stats
    from django.db.models import Count, Q
    from django.db.models.functions import TruncDate
    
    stats = queryset.annotate(date=TruncDate('created_at')).values('date').annotate(
        present=Count('id', filter=Q(status='present')),
        absent=Count('id', filter=Q(status='absent')),
        late=Count('id', filter=Q(status='late'))
    ).order_by('-date')
    
    return Response(list(stats))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def viva_report(request):
    """Generate viva marks report"""
    batch_id = request.query_params.get('batch', None)
    
    queryset = VivaRecord.objects.filter(status='completed')
    
    if batch_id:
        queryset = queryset.filter(session__batch_id=batch_id)
    
    serializer = VivaRecordSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def submission_report(request):
    """Generate task submission report"""
    batch_id = request.query_params.get('batch', None)
    
    queryset = TaskSubmission.objects.all()
    
    if batch_id:
        queryset = queryset.filter(task__batch_id=batch_id)
    
    serializer = TaskSubmissionSerializer(queryset, many=True)
    return Response(serializer.data)
