from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from apps.core.models import Batch, FacultyTimetableSlot

from .models import User
from .serializers import UserSerializer, LoginSerializer, RegisterSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Faculty login endpoint.
    Accepts faculty_id or email + password.
    Returns JWT tokens and user info.
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    faculty_id_or_email = serializer.validated_data['faculty_id']
    password = serializer.validated_data['password']
    
    # Try to find user by faculty_id or email
    user = None
    try:
        # Try faculty_id first
        user = User.objects.get(faculty_id=faculty_id_or_email)
    except User.DoesNotExist:
        try:
            # Try email
            user = User.objects.get(email=faculty_id_or_email)
        except User.DoesNotExist:
            pass
    
    if user is None or not user.check_password(password):
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        return Response(
            {'error': 'Account is inactive'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Update last login
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'faculty': UserSerializer(user).data
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Faculty registration endpoint"""
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    
    return Response(
        UserSerializer(user).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """Get current faculty profile"""
    return Response(UserSerializer(request.user).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def faculty_weekly_timetable_view(request):
    """Return weekly timetable slots for logged-in faculty and batches per semester."""
    day_order = {
        'Monday': 1,
        'Tuesday': 2,
        'Wednesday': 3,
        'Thursday': 4,
        'Friday': 5,
    }

    slots_qs = (
        FacultyTimetableSlot.objects
        .filter(faculty=request.user)
        .select_related('semester')
    )
    slots = sorted(
        slots_qs,
        key=lambda s: (s.semester.number, day_order.get(s.day_of_week, 99), s.hour_slot)
    )

    semester_ids = sorted({slot.semester_id for slot in slots})
    batches_by_semester = {}
    for batch in Batch.objects.filter(semester_id__in=semester_ids, is_active=True).select_related('semester'):
        batches_by_semester.setdefault(batch.semester_id, []).append({
            "id": batch.id,
            "name": batch.name,
            "year": batch.year,
        })

    semesters = []
    seen_semesters = set()
    for slot in slots:
        if slot.semester_id in seen_semesters:
            continue
        seen_semesters.add(slot.semester_id)
        semesters.append({
            "id": slot.semester.id,
            "name": slot.semester.name,
            "number": slot.semester.number,
            "batches": sorted(
                batches_by_semester.get(slot.semester_id, []),
                key=lambda b: b["name"]
            ),
        })

    payload_slots = [{
        "id": slot.id,
        "day_of_week": slot.day_of_week,
        "hour_slot": slot.hour_slot,
        "subject_name": slot.subject_name,
        "semester": {
            "id": slot.semester.id,
            "name": slot.semester.name,
            "number": slot.semester.number,
        },
    } for slot in slots]

    return Response({
        "faculty": {
            "id": request.user.id,
            "faculty_id": request.user.faculty_id,
            "name": request.user.name,
        },
        "weekdays": ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
        "hours": [1, 2, 3, 4, 5, 6],
        "slots": payload_slots,
        "semesters": semesters,
    })
