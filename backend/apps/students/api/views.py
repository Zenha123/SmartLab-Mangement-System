from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.evaluation.models import Task, TaskSubmission
from apps.evaluation.serializers import TaskSerializer, TaskSubmissionSerializer


class StudentTaskViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API for students to fetch their batch's tasks.
    ReadOnly: Students cannot create tasks via this API.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'student_profile'):
            batch = user.student_profile.batch
            return Task.objects.filter(batch=batch).order_by('-created_at')
        return Task.objects.none()

    # ──────────────────────────────────────────────
    # SUBMIT (file upload)
    # ──────────────────────────────────────────────
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        Submit a task solution file.
        POST /api/student/tasks/<id>/submit/
        Expects multipart/form-data with "file" field.
        """
        task = self.get_object()
        user = request.user

        if not hasattr(user, 'student_profile'):
            return Response(
                {"error": "Student profile not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        student = user.student_profile
        uploaded_file = request.FILES.get('file')

        if not uploaded_file:
            return Response(
                {"error": "No file uploaded"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            submission, created = TaskSubmission.objects.get_or_create(
                task=task,
                student=student
            )
            submission.submission_file = uploaded_file
            submission.status = 'submitted'
            submission.save()

            serializer = TaskSubmissionSerializer(submission)
            return Response({
                "success": True,
                "message": "File submitted successfully",
                "submission_id": submission.id,
                "file_url": serializer.data.get('file_path')
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Submission failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # ──────────────────────────────────────────────
    # RESULTS ENDPOINTS (student-facing)
    # ──────────────────────────────────────────────
    @action(detail=False, methods=['get'], url_path='my_results')
    def my_results(self, request):
        """
        GET /api/student/tasks/my_results/
        Returns all PUBLISHED task submissions for the logged-in student.
        Only is_published=True submissions are returned.
        """
        user = request.user
        if not hasattr(user, 'student_profile'):
            return Response({'error': 'Student profile not found'}, status=400)

        student = user.student_profile
        submissions = TaskSubmission.objects.filter(
            student=student,
            is_published=True
        ).select_related('task').order_by('-submitted_at')

        data = []
        for s in submissions:
            data.append({
                'submission_id': s.id,
                'task_id': s.task.id,
                'task_title': s.task.title,
                'marks': s.marks,
                'feedback': s.feedback,
                'submitted_at': s.submitted_at.isoformat() if s.submitted_at else None,
                'status': s.status,
            })

        return Response({'results': data})

    @action(detail=False, methods=['get'], url_path='my_viva')
    def my_viva(self, request):
        """
        GET /api/student/tasks/my_viva/
        Returns completed viva records for the logged-in student.
        """
        user = request.user
        if not hasattr(user, 'student_profile'):
            return Response({'error': 'Student profile not found'}, status=400)

        student = user.student_profile
        from apps.evaluation.models import VivaRecord
        records = VivaRecord.objects.filter(
            student=student, status='completed'
        ).order_by('-conducted_at')

        data = []
        for r in records:
            data.append({
                'id': r.id,
                'marks': r.marks,
                'notes': r.notes,
                'conducted_at': r.conducted_at.isoformat() if r.conducted_at else None,
            })

        return Response({'viva': data})

    @action(detail=False, methods=['get'], url_path='my_exam')
    def my_exam(self, request):
        """
        GET /api/student/tasks/my_exam/
        Returns exam results for the logged-in student.
        """
        user = request.user
        if not hasattr(user, 'student_profile'):
            return Response({'error': 'Student profile not found'}, status=400)

        student = user.student_profile
        from apps.evaluation.models import ExamResult
        results = ExamResult.objects.filter(
            student=student
        ).select_related('exam_session').order_by('-submitted_at')

        data = []
        for r in results:
            data.append({
                'id': r.id,
                'exam_type': r.exam_session.exam_type,
                'marks': r.marks,
                'duration_minutes': r.duration_minutes,
                'submitted_at': r.submitted_at.isoformat() if r.submitted_at else None,
            })

        return Response({'exam': data})
