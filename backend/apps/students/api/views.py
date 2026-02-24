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
        Returns PUBLISHED viva records for the logged-in student.
        Only is_published=True records are returned.
        """
        user = request.user
        if not hasattr(user, 'student_profile'):
            return Response({'error': 'Student profile not found'}, status=400)

        student = user.student_profile
        from apps.evaluation.models import VivaRecord
        records = VivaRecord.objects.filter(
            student=student, status='completed', is_published=True
        ).select_related('viva_session').order_by('-conducted_at')

        data = []
        for r in records:
            data.append({
                'id': r.id,
                'subject': r.viva_session.subject if r.viva_session else 'Viva',
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
        Updated to use the new StudentExam model.
        """
        user = request.user
        if not hasattr(user, 'student_profile'):
            return Response({'error': 'Student profile not found'}, status=400)

        student = user.student_profile
        from apps.evaluation.models import StudentExam
        results = StudentExam.objects.filter(
            student=student,
            is_published=True
        ).select_related('session').order_by('-submitted_at')

        data = []
        for r in results:
            data.append({
                'id': r.id,
                'title': r.session.title,
                'marks': r.marks,
                'status': r.status,
                'feedback': r.feedback,
                'submitted_at': r.submitted_at.isoformat() if r.submitted_at else None,
            })

        return Response({'exam': data})

    @action(detail=False, methods=['get'], url_path='my_live_viva')
    def my_live_viva(self, request):
        """
        GET /api/student/tasks/my_live_viva/
        Returns the CURRENT active online viva session for the student's batch.
        """
        user = request.user
        if not hasattr(user, 'student_profile'):
            return Response({'error': 'Student profile not found'}, status=400)
        
        student = user.student_profile
        from apps.evaluation.models import VivaSession
        session = VivaSession.objects.filter(
            batch=student.batch,
            viva_type='online',
            status='live'
        ).order_by('-created_at').first()
        
        if not session:
            return Response({'session': None})
            
        return Response({
            'session': {
                'id': session.id,
                'subject': session.subject,
                'platform_name': session.platform_name,  # Correct model field name
                'join_code': session.join_code,           # Correct model field name
                'join_link': session.join_link,           # Correct model field name
                'instructions': session.instructions
            }
        })
