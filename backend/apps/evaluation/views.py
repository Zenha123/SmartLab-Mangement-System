from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.views import APIView
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Q
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from .models import (
    VivaRecord, VivaSession, ExamSession, ExamQuestion,
    StudentExam, Task, TaskSubmission
)
from .serializers import (
    VivaRecordSerializer, VivaSessionSerializer,
    ExamSessionSerializer, ExamQuestionSerializer, StudentExamSerializer,
    TaskSerializer, TaskSubmissionSerializer
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
                pass

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
            pass

        return Response({'status': 'published', 'session_id': session.id})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark session as completed and publish all results to students"""
        session = self.get_object()
        session.status = 'completed'
        session.save()

        published_count = VivaRecord.objects.filter(
            viva_session=session, status='completed'
        ).update(is_published=True)

        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            channel_layer = get_channel_layer()
            records = VivaRecord.objects.filter(
                viva_session=session, is_published=True
            ).select_related('student', 'viva_session')

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
        serializer.save(faculty=self.request.user)

    def perform_update(self, serializer):
        """
        Broadcast Viva evaluation to student when status is updated to completed.
        """
        record = serializer.save()

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
            return Response(
                {'error': 'viva_session, student, and marks are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

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
        return Response({})


class ExamSessionViewSet(viewsets.ModelViewSet):
    """Faculty: Create and manage exam sessions."""
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
    """Faculty: Add / edit / delete questions per session."""
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
    """Faculty: Start an exam session — randomly assigns questions to all students."""
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
            return Response(
                {'error': 'Add at least one question before starting'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from apps.students.models import Student
        students = list(Student.objects.filter(batch=session.batch))
        if not students:
            return Response({'error': 'No students found in batch'}, status=status.HTTP_400_BAD_REQUEST)

        random.shuffle(questions)
        assigned_count = 0
        for i, student in enumerate(students):
            exam_rec, created = StudentExam.objects.get_or_create(
                session=session, student=student
            )
            if created or exam_rec.assigned_questions.count() == 0:
                start = i % len(questions)
                end = start + min(2, len(questions))
                assigned = (questions + questions)[start:end]
                exam_rec.assigned_questions.set(assigned)
                exam_rec.save()
            assigned_count += 1

        session.status = 'active'
        session.save()

        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            channel_layer = get_channel_layer()
            batch_group = f'batch_{session.batch.id}'
            async_to_sync(channel_layer.group_send)(
                batch_group,
                {
                    'type': 'viva_event',
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
    """Faculty: End an exam — marks completed and blocks submissions."""
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
    """Faculty: List all student submissions for an exam session."""
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
    """Faculty: Save marks and feedback for a student's exam submission."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        exam_id = request.data.get('student_exam_id')
        marks = request.data.get('marks')
        feedback = request.data.get('feedback', '')

        if exam_id is None or marks is None:
            return Response(
                {'error': 'student_exam_id and marks are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
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
    """Student: Get their assigned exam questions for the active session."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student = getattr(request.user, 'student_profile', None)
        if not student:
            return Response({'error': 'Not a student'}, status=status.HTTP_403_FORBIDDEN)

        session_id = request.query_params.get('session_id')
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
    """Student: Submit exam file."""
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

        if exam_rec.session.status == 'completed':
            return Response(
                {'error': 'Exam has ended. Submissions are closed.'},
                status=status.HTTP_403_FORBIDDEN
            )

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
        serializer.save(faculty=self.request.user)

    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
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
            pass

        serializer = self.get_serializer(submission)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attendance_report(request):
    """Generate attendance report"""
    from apps.students.models import Attendance
    from django.db.models import Count, Q
    from django.db.models.functions import TruncDate

    batch_id = request.query_params.get('batch', None)
    date_filter = request.query_params.get('date', None)

    queryset = Attendance.objects.all()

    if batch_id:
        queryset = queryset.filter(session__batch_id=batch_id)
    if date_filter:
        queryset = queryset.filter(created_at__date=date_filter)

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
        queryset = queryset.filter(viva_session__batch_id=batch_id)

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


# =========================
# PDF HELPERS
# =========================

def _build_pdf_response(filename, story, pagesize=landscape(A4)):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=pagesize,
        rightMargin=24,
        leftMargin=24,
        topMargin=24,
        bottomMargin=24,
    )
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


def _safe(value, default="N/A"):
    if value is None:
        return default
    value = str(value).strip()
    return value if value else default


def _submission_status_text(submission):
    return (submission.status or "N/A").title()


def _make_styles():
    styles = getSampleStyleSheet()

    title_style = styles['Title']
    title_style.fontName = "Helvetica-Bold"
    title_style.fontSize = 20
    title_style.leading = 24
    title_style.alignment = 1

    section_style = styles['Heading2']
    section_style.fontName = "Helvetica-Bold"
    section_style.fontSize = 13
    section_style.leading = 16
    section_style.spaceBefore = 8
    section_style.spaceAfter = 8
    section_style.textColor = colors.HexColor("#111827")

    normal_style = styles['Normal']
    normal_style.fontName = "Helvetica"
    normal_style.fontSize = 10
    normal_style.leading = 13

    cell_style = styles['BodyText'].clone('pdf_cell_style')
    cell_style.fontName = "Helvetica"
    cell_style.fontSize = 8.5
    cell_style.leading = 10
    cell_style.textColor = colors.black

    header_style = styles['BodyText'].clone('pdf_header_style')
    header_style.fontName = "Helvetica-Bold"
    header_style.fontSize = 8.5
    header_style.leading = 10
    header_style.textColor = colors.white

    return {
        "title": title_style,
        "section": section_style,
        "normal": normal_style,
        "cell": cell_style,
        "header": header_style,
    }


def _styled_table(table_data, col_widths, align_center_from_col=None):
    table = Table(table_data, repeatRows=1, colWidths=col_widths)
    style_commands = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#9ca3af')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor('#f9fafb')]),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]
    if align_center_from_col is not None:
        style_commands.append(('ALIGN', (align_center_from_col, 1), (-1, -1), 'CENTER'))

    table.setStyle(TableStyle(style_commands))
    return table


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_submission_report_pdf(request, student_id):
    from apps.students.models import Student, Attendance

    student = get_object_or_404(
        Student.objects.select_related('batch', 'batch__semester'),
        id=student_id
    )

    submissions = (
        TaskSubmission.objects
        .filter(student=student)
        .select_related('task', 'task__batch')
        .order_by('task__title')
    )

    viva_records = (
        VivaRecord.objects
        .filter(student=student, status='completed')
        .select_related('viva_session')
        .order_by('-conducted_at', '-created_at')
    )

    attendance_records = (
        Attendance.objects
        .filter(student=student)
        .select_related('session')
        .order_by('-session__scheduled_date', '-session__start_time')
    )

    styles = _make_styles()
    story = []

    story.append(Paragraph("Student Performance Report", styles["title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Student Information", styles["section"]))
    story.append(Paragraph(f"<b>Student ID:</b> {_safe(student.student_id)}", styles["normal"]))
    story.append(Paragraph(f"<b>Name:</b> {_safe(student.name)}", styles["normal"]))
    story.append(Paragraph(f"<b>Batch:</b> {_safe(student.batch)}", styles["normal"]))
    story.append(Spacer(1, 12))

    total_tasks = submissions.count()
    submitted_count = submissions.filter(
        Q(status__in=['submitted', 'evaluated']) | Q(submission_file__isnull=False)
    ).count()
    evaluated_qs = submissions.filter(marks__isnull=False)
    evaluated_count = evaluated_qs.count()
    avg_task_marks = evaluated_qs.aggregate(avg=Avg('marks'))['avg']

    total_attendance = attendance_records.count()
    present_count = attendance_records.filter(status='present').count()
    attendance_percentage = (present_count / total_attendance * 100) if total_attendance > 0 else 0

    viva_count = viva_records.count()
    viva_avg = viva_records.aggregate(avg=Avg('marks'))['avg']

    story.append(Paragraph("Performance Summary", styles["section"]))

    summary_table_data = [
        [
            Paragraph("Metric", styles["header"]),
            Paragraph("Value", styles["header"]),
            Paragraph("Metric", styles["header"]),
            Paragraph("Value", styles["header"]),
        ],
        [
            Paragraph("Total Tasks", styles["cell"]),
            Paragraph(str(total_tasks), styles["cell"]),
            Paragraph("Submitted Tasks", styles["cell"]),
            Paragraph(str(submitted_count), styles["cell"]),
        ],
        [
            Paragraph("Evaluated Tasks", styles["cell"]),
            Paragraph(str(evaluated_count), styles["cell"]),
            Paragraph("Average Task Marks", styles["cell"]),
            Paragraph(f"{avg_task_marks:.1f}" if avg_task_marks is not None else "N/A", styles["cell"]),
        ],
        [
            Paragraph("Attendance Sessions", styles["cell"]),
            Paragraph(str(total_attendance), styles["cell"]),
            Paragraph("Attendance %", styles["cell"]),
            Paragraph(f"{attendance_percentage:.1f}%", styles["cell"]),
        ],
        [
            Paragraph("Viva Count", styles["cell"]),
            Paragraph(str(viva_count), styles["cell"]),
            Paragraph("Average Viva Marks", styles["cell"]),
            Paragraph(f"{viva_avg:.1f}" if viva_avg is not None else "N/A", styles["cell"]),
        ],
    ]

    story.append(_styled_table(
        summary_table_data,
        [2.0 * inch, 1.2 * inch, 2.0 * inch, 1.2 * inch]
    ))
    story.append(Spacer(1, 14))

    story.append(Paragraph("Task Submission Details", styles["section"]))

    task_table_data = [[
        Paragraph("Task Title", styles["header"]),
        Paragraph("Subject", styles["header"]),
        Paragraph("Submitted At", styles["header"]),
        Paragraph("Status", styles["header"]),
        Paragraph("Marks", styles["header"]),
        Paragraph("Feedback", styles["header"]),
    ]]

    if submissions.exists():
        for sub in submissions:
            task_table_data.append([
                Paragraph(_safe(sub.task.title if sub.task else None), styles["cell"]),
                Paragraph(_safe(sub.task.subject_name if sub.task else None), styles["cell"]),
                Paragraph(sub.submitted_at.strftime("%Y-%m-%d %H:%M") if sub.submitted_at else "N/A", styles["cell"]),
                Paragraph(_submission_status_text(sub), styles["cell"]),
                Paragraph(str(sub.marks) if sub.marks is not None else "N/A", styles["cell"]),
                Paragraph(_safe(sub.feedback), styles["cell"]),
            ])
    else:
        task_table_data.append([
            Paragraph("No submissions found", styles["cell"]),
            Paragraph("-", styles["cell"]),
            Paragraph("-", styles["cell"]),
            Paragraph("-", styles["cell"]),
            Paragraph("-", styles["cell"]),
            Paragraph("-", styles["cell"]),
        ])

    story.append(_styled_table(
        task_table_data,
        [2.0 * inch, 1.3 * inch, 1.4 * inch, 1.0 * inch, 0.8 * inch, 2.1 * inch],
        align_center_from_col=4
    ))
    story.append(Spacer(1, 14))

    story.append(Paragraph("Viva Details", styles["section"]))

    viva_table_data = [[
        Paragraph("Subject", styles["header"]),
        Paragraph("Date", styles["header"]),
        Paragraph("Status", styles["header"]),
        Paragraph("Marks", styles["header"]),
        Paragraph("Notes", styles["header"]),
    ]]

    if viva_records.exists():
        for record in viva_records:
            viva_subject = record.viva_session.subject if record.viva_session else "Viva"
            viva_date = record.viva_session.date if record.viva_session else None

            viva_table_data.append([
                Paragraph(_safe(viva_subject), styles["cell"]),
                Paragraph(str(viva_date) if viva_date else "N/A", styles["cell"]),
                Paragraph(_safe(record.status.title() if record.status else None), styles["cell"]),
                Paragraph(str(record.marks) if record.marks is not None else "N/A", styles["cell"]),
                Paragraph(_safe(record.notes), styles["cell"]),
            ])
    else:
        viva_table_data.append([
            Paragraph("No viva records found", styles["cell"]),
            Paragraph("-", styles["cell"]),
            Paragraph("-", styles["cell"]),
            Paragraph("-", styles["cell"]),
            Paragraph("-", styles["cell"]),
        ])

    story.append(_styled_table(
        viva_table_data,
        [1.7 * inch, 1.1 * inch, 1.0 * inch, 0.8 * inch, 3.1 * inch],
        align_center_from_col=2
    ))
    story.append(Spacer(1, 14))

    story.append(Paragraph("Attendance Details", styles["section"]))

    attendance_table_data = [[
        Paragraph("Session Date", styles["header"]),
        Paragraph("Subject", styles["header"]),
        Paragraph("Present", styles["header"]),
        Paragraph("Absent", styles["header"]),
        Paragraph("Attendance %", styles["header"]),
    ]]

    if attendance_records.exists():
        for att in attendance_records:
            session = att.session
            is_present = att.status == "present"

            attendance_table_data.append([
                Paragraph(str(session.scheduled_date) if session and session.scheduled_date else "N/A", styles["cell"]),
                Paragraph(_safe(session.subject_name if session else None), styles["cell"]),
                Paragraph("1" if is_present else "0", styles["cell"]),
                Paragraph("0" if is_present else "1", styles["cell"]),
                Paragraph("100%" if is_present else "0%", styles["cell"]),
            ])
    else:
        attendance_table_data.append([
            Paragraph("No attendance records found", styles["cell"]),
            Paragraph("-", styles["cell"]),
            Paragraph("-", styles["cell"]),
            Paragraph("-", styles["cell"]),
            Paragraph("-", styles["cell"]),
        ])

    story.append(_styled_table(
        attendance_table_data,
        [1.5 * inch, 2.0 * inch, 0.8 * inch, 0.8 * inch, 1.1 * inch],
        align_center_from_col=2
    ))

    filename = f"student_performance_report_{student.student_id}.pdf"
    return _build_pdf_response(filename, story)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def batch_submission_report_pdf(request, batch_id):
    from apps.core.models import Batch
    from apps.students.models import Student, Attendance

    batch = get_object_or_404(
        Batch.objects.select_related('semester'),
        id=batch_id
    )

    students = Student.objects.filter(batch_id=batch_id).order_by('name')

    styles = _make_styles()
    story = []

    story.append(Paragraph("Full Batch Performance Report", styles["title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Batch:</b> {_safe(batch)}", styles["normal"]))
    story.append(Paragraph(f"<b>Total Students:</b> {students.count()}", styles["normal"]))
    story.append(Spacer(1, 14))

    table_data = [[
        Paragraph("Student ID", styles["header"]),
        Paragraph("Name", styles["header"]),
        Paragraph("Tasks", styles["header"]),
        Paragraph("Submitted", styles["header"]),
        Paragraph("Evaluated", styles["header"]),
        Paragraph("Avg Task", styles["header"]),
        Paragraph("Attendance %", styles["header"]),
        Paragraph("Viva Count", styles["header"]),
        Paragraph("Avg Viva", styles["header"]),
    ]]

    if students.exists():
        for student in students:
            student_subs = TaskSubmission.objects.filter(
                student=student,
                task__batch_id=batch_id
            )

            total_tasks = student_subs.count()
            submitted_count = student_subs.filter(
                Q(status__in=['submitted', 'evaluated']) | Q(submission_file__isnull=False)
            ).count()
            evaluated_qs = student_subs.filter(marks__isnull=False)
            evaluated_count = evaluated_qs.count()
            avg_task_marks = evaluated_qs.aggregate(avg=Avg('marks'))['avg']

            student_attendance = Attendance.objects.filter(
                student=student,
                session__batch_id=batch_id
            )
            total_attendance = student_attendance.count()
            present_count = student_attendance.filter(status='present').count()
            attendance_pct = (present_count / total_attendance * 100) if total_attendance > 0 else 0

            student_vivas = VivaRecord.objects.filter(
                student=student,
                status='completed',
                viva_session__batch_id=batch_id
            )
            viva_count = student_vivas.count()
            viva_avg = student_vivas.aggregate(avg=Avg('marks'))['avg']

            table_data.append([
                Paragraph(_safe(student.student_id), styles["cell"]),
                Paragraph(_safe(student.name), styles["cell"]),
                Paragraph(str(total_tasks), styles["cell"]),
                Paragraph(str(submitted_count), styles["cell"]),
                Paragraph(str(evaluated_count), styles["cell"]),
                Paragraph(f"{avg_task_marks:.1f}" if avg_task_marks is not None else "N/A", styles["cell"]),
                Paragraph(f"{attendance_pct:.1f}%", styles["cell"]),
                Paragraph(str(viva_count), styles["cell"]),
                Paragraph(f"{viva_avg:.1f}" if viva_avg is not None else "N/A", styles["cell"]),
            ])
    else:
        table_data.append([
            Paragraph("No students", styles["cell"]),
            Paragraph("-", styles["cell"]),
            Paragraph("-", styles["cell"]),
            Paragraph("-", styles["cell"]),
            Paragraph("-", styles["cell"]),
            Paragraph("-", styles["cell"]),
            Paragraph("-", styles["cell"]),
            Paragraph("-", styles["cell"]),
            Paragraph("-", styles["cell"]),
        ])

    batch_table = _styled_table(
        table_data,
        [
            0.95 * inch,
            1.9 * inch,
            0.65 * inch,
            0.8 * inch,
            0.8 * inch,
            0.85 * inch,
            0.9 * inch,
            0.75 * inch,
            0.8 * inch,
        ],
        align_center_from_col=2
    )

    story.append(batch_table)

    filename = f"batch_performance_report_{batch_id}.pdf"
    return _build_pdf_response(filename, story)