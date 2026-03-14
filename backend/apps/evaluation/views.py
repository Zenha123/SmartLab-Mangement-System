from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.views import APIView
from .models import VivaRecord, VivaSession, ExamSession, ExamQuestion, StudentExam, Task, TaskSubmission
from .serializers import (
    VivaRecordSerializer, VivaSessionSerializer,
    ExamSessionSerializer, ExamQuestionSerializer, StudentExamSerializer,
    TaskSerializer, TaskSubmissionSerializer
)
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

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


# ===========================================================================
# EXAM MODULE — Clean, simplified implementation
# ===========================================================================

class ExamSessionViewSet(viewsets.ModelViewSet):
    """Faculty: Create and manage exam sessions.
    GET  /api/exam-sessions/?batch=<id>
    POST /api/exam-sessions/
    """
    queryset = ExamSession.objects.all()
    serializer_class = ExamSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        batch_id = self.request.query_params.get('batch')
        if batch_id:
            qs = qs.filter(batch_id=batch_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(faculty=self.request.user)


class ExamQuestionViewSet(viewsets.ModelViewSet):
    """Faculty: Add / edit / delete questions per session.
    GET  /api/exam-questions/?session=<id>
    POST /api/exam-questions/
    """
    queryset = ExamQuestion.objects.all()
    serializer_class = ExamQuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        session_id = self.request.query_params.get('session')
        if session_id:
            qs = qs.filter(session_id=session_id)
        return qs


class ExamStartView(APIView):
    """Faculty: Start an exam session — randomly assigns questions to all students.
    POST /api/exam-start/  body: { session_id: <id> }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        import random
        session_id = request.data.get('session_id')
        if not session_id:
            return Response({'error': 'session_id required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = ExamSession.objects.get(id=session_id)
        except ExamSession.DoesNotExist:
            return Response({'error': 'Exam session not found'}, status=status.HTTP_404_NOT_FOUND)

        if session.status == 'active':
            return Response({'error': 'Exam already active'}, status=status.HTTP_400_BAD_REQUEST)

        questions = list(session.questions.all())
        if not questions:
            return Response({'error': 'Add at least one question before starting'}, status=status.HTTP_400_BAD_REQUEST)

        from apps.students.models import Student
        students = list(Student.objects.filter(batch=session.batch))
        if not students:
            return Response({'error': 'No students found in batch'}, status=status.HTTP_400_BAD_REQUEST)

        # Random assignment — each student gets 1 or 2 questions
        random.shuffle(questions)
        assigned_count = 0
        for i, student in enumerate(students):
            exam_rec, created = StudentExam.objects.get_or_create(
                session=session, student=student
            )
            if created or exam_rec.assigned_questions.count() == 0:
                # Cycle through questions list
                start = i % len(questions)
                end = start + min(2, len(questions))
                assigned = (questions + questions)[start:end]  # wrap-around
                exam_rec.assigned_questions.set(assigned)
                exam_rec.save()
            assigned_count += 1

        # Mark session active
        session.status = 'active'
        session.save()

        # Notify all students via WebSocket
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            channel_layer = get_channel_layer()
            batch_group = f'batch_{session.batch.id}'
            async_to_sync(channel_layer.group_send)(
                batch_group,
                {
                    'type': 'viva_event',  # reuse channel handler
                    'event': 'exam_started',
                    'session_id': session.id,
                    'title': session.title,
                    'duration_minutes': session.duration_minutes,
                }
            )
        except Exception:
            pass

        return Response({
            'status': 'active',
            'session_id': session.id,
            'students_assigned': assigned_count,
        }, status=status.HTTP_200_OK)


class ExamEndView(APIView):
    """Faculty: End an exam — marks completed and blocks submissions.
    POST /api/exam-end/  body: { session_id: <id> }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.data.get('session_id')
        if not session_id:
            return Response({'error': 'session_id required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            session = ExamSession.objects.get(id=session_id)
        except ExamSession.DoesNotExist:
            return Response({'error': 'Exam session not found'}, status=status.HTTP_404_NOT_FOUND)

        session.status = 'completed'
        session.save()

        # Notify all students — time is over
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            channel_layer = get_channel_layer()
            batch_group = f'batch_{session.batch.id}'
            async_to_sync(channel_layer.group_send)(
                batch_group,
                {
                    'type': 'viva_event',
                    'event': 'exam_ended',
                    'session_id': session.id,
                    'title': session.title,
                }
            )
        except Exception:
            pass

        return Response({'status': 'completed', 'session_id': session.id})


class ExamSubmissionsView(APIView):
    """Faculty: List all student submissions for an exam session.
    GET /api/exam-submissions/?session_id=<id>
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({'error': 'session_id required'}, status=status.HTTP_400_BAD_REQUEST)
        submissions = StudentExam.objects.filter(
            session_id=session_id
        ).select_related('student', 'session').prefetch_related('assigned_questions')
        serializer = StudentExamSerializer(submissions, many=True, context={'request': request})
        return Response(serializer.data)


class ExamEvaluateView(APIView):
    """Faculty: Save marks and feedback for a student's exam submission.
    POST /api/exam-evaluate/  body: { student_exam_id, marks, feedback }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        exam_id = request.data.get('student_exam_id')
        marks = request.data.get('marks')
        feedback = request.data.get('feedback', '')

        if exam_id is None or marks is None:
            return Response({'error': 'student_exam_id and marks are required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            marks = int(marks)
        except (ValueError, TypeError):
            return Response({'error': 'marks must be an integer'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            exam_rec = StudentExam.objects.get(id=exam_id)
        except StudentExam.DoesNotExist:
            return Response({'error': 'StudentExam not found'}, status=status.HTTP_404_NOT_FOUND)

        exam_rec.marks = marks
        exam_rec.feedback = feedback
        exam_rec.status = 'evaluated'
        exam_rec.is_published = True
        exam_rec.save()

        # Notify student
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            channel_layer = get_channel_layer()
            student_group = f'student_{exam_rec.student.id}'
            async_to_sync(channel_layer.group_send)(
                student_group,
                {
                    'type': 'viva_event',
                    'event': 'exam_evaluated',
                    'exam_id': exam_rec.id,
                    'session_title': exam_rec.session.title,
                    'subject_name': exam_rec.session.subject_name,
                    'marks': marks,
                    'feedback': feedback,
                }
            )
        except Exception:
            pass

        return Response({'status': 'evaluated', 'marks': marks})


class MyExamView(APIView):
    """Student: Get their assigned exam questions for the active session.
    GET /api/my-exam/?session_id=<id>
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student = getattr(request.user, 'student_profile', None)
        if not student:
            return Response({'error': 'Not a student'}, status=status.HTTP_403_FORBIDDEN)

        session_id = request.query_params.get('session_id')
        # If no session_id, return all active exam sessions for their batch
        if not session_id:
            sessions = ExamSession.objects.filter(
                batch=student.batch, status='active'
            ).order_by('-created_at')
            data = []
            for s in sessions:
                try:
                    exam_rec = StudentExam.objects.get(session=s, student=student)
                    data.append({
                        'session_id': s.id,
                        'title': s.title,
                        'duration_minutes': s.duration_minutes,
                        'status': exam_rec.status,
                        'exam_rec_id': exam_rec.id,
                    })
                except StudentExam.DoesNotExist:
                    pass
            return Response({'sessions': data})

        try:
            exam_rec = StudentExam.objects.get(
                session_id=session_id, student=student
            )
        except StudentExam.DoesNotExist:
            return Response({'error': 'No exam record found'}, status=status.HTTP_404_NOT_FOUND)

        questions = ExamQuestionSerializer(exam_rec.assigned_questions.all(), many=True).data
        return Response({
            'exam_rec_id': exam_rec.id,
            'session_id': exam_rec.session.id,
            'title': exam_rec.session.title,
            'duration_minutes': exam_rec.session.duration_minutes,
            'session_status': exam_rec.session.status,
            'status': exam_rec.status,
            'marks': exam_rec.marks,
            'feedback': exam_rec.feedback,
            'questions': questions,
        })


class SubmitExamView(APIView):
    """Student: Submit exam file.
    POST /api/submit-exam/  multipart: { exam_rec_id, file }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        student = getattr(request.user, 'student_profile', None)
        if not student:
            return Response({'error': 'Not a student'}, status=status.HTTP_403_FORBIDDEN)

        exam_rec_id = request.data.get('exam_rec_id')
        if not exam_rec_id:
            return Response({'error': 'exam_rec_id required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            exam_rec = StudentExam.objects.get(id=exam_rec_id, student=student)
        except StudentExam.DoesNotExist:
            return Response({'error': 'Exam record not found'}, status=status.HTTP_404_NOT_FOUND)

        # Block if exam ended
        if exam_rec.session.status == 'completed':
            return Response({'error': 'Exam has ended. Submissions are closed.'}, status=status.HTTP_403_FORBIDDEN)

        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        exam_rec.submission_file = uploaded_file
        exam_rec.submitted_at = timezone.now()
        exam_rec.status = 'submitted'
        exam_rec.save()

        return Response({'status': 'submitted', 'exam_rec_id': exam_rec.id}, status=status.HTTP_200_OK)


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
                    'subject_name': submission.task.subject_name,
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
def _build_pdf_response(filename, story, pagesize=landscape(A4)):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=pagesize,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,
    )
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


def _submission_status_text(submission):
    return (submission.status or "N/A").title()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_submission_report_pdf(request, student_id):
    from apps.students.models import Student

    student = get_object_or_404(Student.objects.select_related('batch'), id=student_id)

    submissions = (
        TaskSubmission.objects
        .filter(student=student)
        .select_related('task', 'student', 'task__batch')
        .order_by('task__title')
    )

    styles = getSampleStyleSheet()
    story = []

    title_style = styles['Title']
    normal_style = styles['Normal']

    cell_style = styles['BodyText'].clone('student_cell_style')
    cell_style.fontName = "Helvetica"
    cell_style.fontSize = 9
    cell_style.leading = 11
    cell_style.textColor = colors.black

    header_style = styles['BodyText'].clone('student_header_style')
    header_style.fontName = "Helvetica-Bold"
    header_style.fontSize = 9
    header_style.leading = 11
    header_style.textColor = colors.white

    story.append(Paragraph("Student Submission Report", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Student ID:</b> {student.student_id}", normal_style))
    story.append(Paragraph(f"<b>Name:</b> {student.name}", normal_style))
    story.append(Paragraph(f"<b>Batch:</b> {student.batch}", normal_style))
    story.append(Spacer(1, 16))

    table_data = [[
        Paragraph("Task Title", header_style),
        Paragraph("Subject", header_style),
        Paragraph("Submitted At", header_style),
        Paragraph("Status", header_style),
        Paragraph("Marks", header_style),
        Paragraph("Feedback", header_style),
    ]]

    if submissions.exists():
        for sub in submissions:
            table_data.append([
                Paragraph(sub.task.title if sub.task else "N/A", cell_style),
                Paragraph(sub.task.subject_name if sub.task and sub.task.subject_name else "N/A", cell_style),
                Paragraph(sub.submitted_at.strftime("%Y-%m-%d %H:%M") if sub.submitted_at else "N/A", cell_style),
                Paragraph(_submission_status_text(sub), cell_style),
                Paragraph(str(sub.marks) if sub.marks is not None else "N/A", cell_style),
                Paragraph(sub.feedback if sub.feedback else "N/A", cell_style),
            ])
    else:
        table_data.append([
            Paragraph("No submissions found", cell_style),
            Paragraph("-", cell_style),
            Paragraph("-", cell_style),
            Paragraph("-", cell_style),
            Paragraph("-", cell_style),
            Paragraph("-", cell_style),
        ])

    table = Table(
        table_data,
        repeatRows=1,
        colWidths=[2.2 * inch, 1.4 * inch, 1.5 * inch, 1.0 * inch, 0.8 * inch, 2.1 * inch]
    )

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (4, 1), (4, -1), 'CENTER'),   # Marks center
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor('#f9fafb')]),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    story.append(table)

    filename = f"student_submission_report_{student.student_id}.pdf"
    return _build_pdf_response(filename, story)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def batch_submission_report_pdf(request, batch_id):
    from apps.core.models import Batch
    from apps.students.models import Student

    batch = get_object_or_404(Batch, id=batch_id)

    students = (
        Student.objects
        .filter(batch_id=batch_id)
        .order_by('name')
    )

    styles = getSampleStyleSheet()
    story = []

    title_style = styles['Title']
    normal_style = styles['Normal']

    cell_style = styles['BodyText'].clone('batch_cell_style')
    cell_style.fontName = "Helvetica"
    cell_style.fontSize = 9
    cell_style.leading = 11
    cell_style.textColor = colors.black

    header_style = styles['BodyText'].clone('batch_header_style')
    header_style.fontName = "Helvetica-Bold"
    header_style.fontSize = 9
    header_style.leading = 11
    header_style.textColor = colors.white

    story.append(Paragraph("Full Batch Submission Report", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Batch:</b> {batch}", normal_style))
    story.append(Spacer(1, 16))

    table_data = [[
        Paragraph("Student ID", header_style),
        Paragraph("Name", header_style),
        Paragraph("Tasks", header_style),
        Paragraph("Submitted", header_style),
        Paragraph("Evaluated", header_style),
        Paragraph("Average Marks", header_style),
    ]]

    if students.exists():
        for student in students:
            student_subs = TaskSubmission.objects.filter(
                student=student,
                task__batch_id=batch_id
            )

            total_tasks = student_subs.count()
            submitted_count = student_subs.exclude(submission_file='').count()
            evaluated_subs = student_subs.filter(marks__isnull=False)
            evaluated_count = evaluated_subs.count()

            avg_marks = "N/A"
            if evaluated_count > 0:
                total_marks = sum(sub.marks for sub in evaluated_subs if sub.marks is not None)
                avg_marks = f"{total_marks / evaluated_count:.1f}"

            table_data.append([
                Paragraph(student.student_id, cell_style),
                Paragraph(student.name, cell_style),
                Paragraph(str(total_tasks), cell_style),
                Paragraph(str(submitted_count), cell_style),
                Paragraph(str(evaluated_count), cell_style),
                Paragraph(avg_marks, cell_style),
            ])
    else:
        table_data.append([
            Paragraph("No students", cell_style),
            Paragraph("-", cell_style),
            Paragraph("-", cell_style),
            Paragraph("-", cell_style),
            Paragraph("-", cell_style),
            Paragraph("-", cell_style),
        ])

    table = Table(
        table_data,
        repeatRows=1,
        colWidths=[1.2 * inch, 2.4 * inch, 0.9 * inch, 1.0 * inch, 1.0 * inch, 1.1 * inch]
    )

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor('#f9fafb')]),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    story.append(table)

    filename = f"batch_submission_report_{batch_id}.pdf"
    return _build_pdf_response(filename, story)