from django.urls import path
from .views import login_view, semester_list, semester_detail

urlpatterns = [
    path('', login_view, name='login'),
    path('etlab-admin/semesters/', semester_list, name='semester_list'),
    path('etlab-admin/semester/<int:sem>/', semester_detail, name='semester_detail'),
]
