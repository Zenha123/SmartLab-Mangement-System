from rest_framework import viewsets, permissions
from apps.evaluation.models import Task
from apps.evaluation.serializers import TaskSerializer

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
