from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'semesters', views.SemesterViewSet, basename='semester')
router.register(r'batches', views.BatchViewSet, basename='batch')
router.register(r'pc-mappings', views.PCMappingViewSet, basename='pc-mapping')

urlpatterns = [
    path('', include(router.urls)),
]
