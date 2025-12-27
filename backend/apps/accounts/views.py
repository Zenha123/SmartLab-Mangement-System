from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone

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
