from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class FacultyManager(BaseUserManager):
    """Custom manager for Faculty user model"""
    
    def create_user(self, faculty_id, email, password=None, **extra_fields):
        if not faculty_id:
            raise ValueError('Faculty must have a faculty ID')
        if not email:
            raise ValueError('Faculty must have an email address')
        
        email = self.normalize_email(email)
        user = self.model(faculty_id=faculty_id, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, faculty_id, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(faculty_id, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for Faculty authentication.
    Uses faculty_id as the unique identifier instead of username.
    """
    faculty_id = models.CharField(max_length=50, unique=True, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    name = models.CharField(max_length=200)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    objects = FacultyManager()
    
    USERNAME_FIELD = 'faculty_id'
    REQUIRED_FIELDS = ['email', 'name']
    
    class Meta:
        db_table = 'faculty'
        verbose_name = 'Faculty'
        verbose_name_plural = 'Faculty'
    
    def __str__(self):
        return f"{self.name} ({self.faculty_id})"
    
    def get_full_name(self):
        return self.name
    
    def get_short_name(self):
        return self.faculty_id
