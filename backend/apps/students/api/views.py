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
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        Submit code for a task via file upload.
        Expects: multipart/form-data with "file" field
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
            # Fallback for old text-based submission (optional, or return error)
            code_text = request.data.get('code', '')
            if code_text:
                # Handle legacy text submission if needed, or error out
                # For now, let's enforce file upload as per requirements
                pass
            
            return Response(
                {"error": "No file uploaded"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # FileField handles saving automatically via Django's storage backend
        # Create or update submission
        
        try:
            submission, created = TaskSubmission.objects.get_or_create(
                task=task,
                student=student
            )
            
            # Update file and status
            submission.submission_file = uploaded_file
            submission.status = 'submitted'
            # Clear legacy file_path if it exists to avoid confusion, 
            # or keep it as backup? serializer now prefers into submission_file
            # We can leave file_path blank or sync it
            submission.save()
            
            # Force serializer to recognize the file path for response
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
