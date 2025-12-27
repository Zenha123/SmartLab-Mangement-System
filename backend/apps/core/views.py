from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from .models import Semester, Batch, PCMapping
from .serializers import SemesterSerializer, BatchSerializer, PCMappingSerializer


class SemesterViewSet(viewsets.ModelViewSet):
    """ViewSet for Semester CRUD"""
    queryset = Semester.objects.filter(is_active=True)
    serializer_class = SemesterSerializer
    permission_classes = [IsAuthenticated]


class BatchViewSet(viewsets.ModelViewSet):
    """ViewSet for Batch CRUD with filtering"""
    queryset = Batch.objects.filter(is_active=True)
    serializer_class = BatchSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        semester_id = self.request.query_params.get('semester', None)
        if semester_id:
            queryset = queryset.filter(semester_id=semester_id)
        return queryset


class PCMappingViewSet(viewsets.ModelViewSet):
    """ViewSet for PC Mapping CRUD"""
    queryset = PCMapping.objects.filter(is_active=True)
    serializer_class = PCMappingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        batch_id = self.request.query_params.get('batch', None)
        if batch_id:
            queryset = queryset.filter(batch_id=batch_id)
        return queryset
