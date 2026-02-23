from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.views import APIView
from .models import VivaRecord, VivaSession, ExamSession, ExamResult, Task, TaskSubmission
from .serializers import (
    VivaRecordSerializer, VivaSessionSerializer, ExamSessionSerializer,
    ExamResultSerializer, TaskSerializer, TaskSubmissionSerializer
)


class VivaSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for Viva Session management"""
    queryset = VivaSession.objects.all()
    serializer_class = VivaSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        batch_id = self.request.query_params.get('batch', None)
        viva_type = self.request.query_params.get('viva_type', None)
        status_param = self.request.query_params.get('status', None)
        
        if batch_id:
            queryset = queryset.filter(batch_id=batch_id)
        if viva_type:
            queryset = queryset.filter(viva_type=viva_type)
        if status_param:
            queryset = queryset.filter(status=status_param)
            
        return queryset

    def perform_create(self, serializer):
        """
        Create session and auto-create VivaRecord placeholders for offline viva.
        Broadcast immediately for online viva if status is 'live'.
        """
        session = serializer.save(faculty=self.request.user)
        
        # If offline, auto-create placeholders for all students in batch
        if session.viva_type == 'offline':
            from apps.students.models import Student
            students = Student.objects.filter(batch=session.batch)
            for student in students:
                VivaRecord.objects.get_or_create(
                    viva_session=session,
                    student=student,
                    defaults={'faculty': self.request.user, 'status': 'waiting'}
                )
        elif session.viva_type == 'online' and session.status == 'live':
            # Broadcast to batch WebSocket group
            try:
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync
                channel_layer = get_channel_layer()
                batch_group = f'batch_{session.batch.id}'
                
                async_to_sync(channel_layer.group_send)(
                    batch_group,
                    {
                        'type': 'viva_event',
                        'event': 'viva_online_published',
                        'session_id': session.id,
                        'subject': session.subject,
                        'platform': session.platform_name,
                        'join_code': session.join_code,
                        'join_link': session.join_link,
                        'instructions': session.instructions,
                    }
                )
            except Exception:
                pass  # WebSocket failure is non-fatal

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """
        Publish online viva session — mark as Live and broadcast to batch via WebSocket.
        """
        session = self.get_object()
        if session.viva_type != 'online':
            return Response({'error': 'Only online sessions can be published'}, status=400)
        
        session.status = 'live'
        session.save()
        
        # Broadcast to batch WebSocket group
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            channel_layer = get_channel_layer()
            batch_group = f'batch_{session.batch.id}'
            
            async_to_sync(channel_layer.group_send)(
                batch_group,
                {
                    'type': 'viva_event',
                    'event': 'viva_online_published',
                    'session_id': session.id,
                    'subject': session.subject,
                    'platform': session.platform_name,
                    'join_code': session.join_code,
                    'join_link': session.join_link,
                    'instructions': session.instructions,
                }
            )
        except Exception:
            pass  # WebSocket failure is non-fatal
            
        return Response({'status': 'published', 'session_id': session.id})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark session as completed and publish all results to students"""
        session = self.get_object()
        session.status = 'completed'
        session.save()
        
        # Publish all viva records for this session so students can see them
        published_count = VivaRecord.objects.filter(
            viva_session=session, status='completed'
        ).update(is_published=True)
        
        # Broadcast to each student in batch via WebSocket
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            channel_layer = get_channel_layer()
            records = VivaRecord.objects.filter(viva_session=session, is_published=True).select_related('student', 'viva_session')
            for record in records:
                student_group = f'student_{record.student.id}'
                async_to_sync(channel_layer.group_send)(
                    student_group,
                    {
                        'type': 'viva_event',
                        'event': 'viva_evaluated',
                        'record_id': record.id,
                        'subject': record.viva_session.subject if record.viva_session else 'Viva',
                        'marks': record.marks,
                        'notes': record.notes
                    }
                )
        except Exception:
            pass
        
        return Response({'status': 'completed', 'published_count': published_count})


class VivaRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for Viva Record management"""
    queryset = VivaRecord.objects.all()
    serializer_class = VivaRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        session_id = self.request.query_params.get('session', None)
        viva_session_id = self.request.query_params.get('viva_session', None)
        student_id = self.request.query_params.get('student', None)
        
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        if viva_session_id:
            queryset = queryset.filter(viva_session_id=viva_session_id)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        return queryset
    
    def perform_create(self, serializer):
        """Auto-assign faculty when creating viva record"""
        serializer.save(faculty=self.request.user)

    def perform_update(self, serializer):
        """
        Broadcast Viva evaluation to student when status is updated to completed.
        """
        record = serializer.save()
        
        # If marked completed, notify the student
        if record.status == 'completed':
            try:
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync
                
                channel_layer = get_channel_layer()
                student_group = f'student_{record.student.id}'
                
                async_to_sync(channel_layer.group_send)(
                    student_group,
                    {
                        'type': 'viva_event',
                        'event': 'viva_evaluated',
                        'record_id': record.id,
                        'subject': record.viva_session.subject if record.viva_session else "Viva",
                        'marks': record.marks,
                        'notes': record.notes
                    }
                )
            except Exception:
                pass


class VivaResultView(APIView):
    """Custom view for saving viva result as per user requirement POST /api/viva-results/"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        viva_session_id = request.data.get('viva_session')
        student_id = request.data.get('student')
        marks = request.data.get('marks')
        notes = request.data.get('notes', '')

        if not viva_session_id or not student_id or marks is None:
            return Response({'error': 'viva_session, student, and marks are required'}, status=status.HTTP_400_BAD_REQUEST)

        record, created = VivaRecord.objects.get_or_create(
            viva_session_id=viva_session_id,
            student_id=student_id,
            defaults={'faculty': request.user}
        )
        record.marks = marks
        record.notes = notes
        record.status = 'completed'
        record.conducted_at = timezone.now()
        record.save()

        # Broadcast via WebSocket
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            channel_layer = get_channel_layer()
            student_group = f'student_{record.student.id}'
            async_to_sync(channel_layer.group_send)(
                student_group,
                {
                    'type': 'viva_event',
                    'event': 'viva_evaluated',
                    'record_id': record.id,
                    'subject': record.viva_session.subject if record.viva_session else "Viva",
                    'marks': record.marks,
                    'notes': record.notes
                }
            )
        except Exception:
            pass
            
        return Response({'status': 'Evaluated', 'record_id': record.id})


class LiveVivaView(APIView):
    """Custom view for getting live viva as per user requirement GET /api/live-viva/"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student = getattr(request.user, 'student_profile', None)
        if not student:
            return Response({'error': 'User is not a student'}, status=status.HTTP_400_BAD_REQUEST)
            
        session = VivaSession.objects.filter(
            batch=student.batch, 
            viva_type='online', 
            status='live'
        ).order_by('-created_at').first()
        
        if session:
            return Response(VivaSessionSerializer(session).data)
        return Response({}) # Return empty if no live viva


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

    @action(detail=True, methods=['post'])
    def evaluate(self, request, pk=None):
        """
        Faculty publishes marks + feedback for a submission.
        POST /api/submissions/<id>/evaluate/
        Body: { "marks": 85, "feedback": "Good work." }
        Sets is_published=True and fires WebSocket event to the student.
        """
        submission = self.get_object()
        marks = request.data.get('marks')
        feedback = request.data.get('feedback', '')

        if marks is None:
            return Response(
                {'error': 'marks is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            marks = int(marks)
            if not (0 <= marks <= 100):
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {'error': 'marks must be an integer between 0 and 100'},
                status=status.HTTP_400_BAD_REQUEST
            )

        submission.marks = marks
        submission.feedback = feedback
        submission.status = 'evaluated'
        submission.is_published = True
        submission.save()

        # Fire WebSocket event to student's personal group
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync

            channel_layer = get_channel_layer()
            student_group = f'student_{submission.student.id}'
            async_to_sync(channel_layer.group_send)(
                student_group,
                {
                    'type': 'submission_event',
                    'event': 'evaluation_published',
                    'submission_id': submission.id,
                    'task_title': submission.task.title,
                    'marks': marks,
                    'feedback': feedback,
                }
            )
        except Exception:
            # Non-fatal: WebSocket broadcast failure shouldn't break the API response
            pass

        serializer = self.get_serializer(submission)
        return Response(serializer.data, status=status.HTTP_200_OK)



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
