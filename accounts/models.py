from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model for multi-platform support."""
    
    # Identification
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    username = None
    email = models.EmailField(_('email address'), unique=True)
    
    # Personal Info
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # User Type
    is_host = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    # Platform Settings
    preferred_platform = models.CharField(
        max_length=20,
        choices=[
            ('web', 'Web'),
            ('desktop', 'Desktop'),
            ('mobile', 'Mobile')
        ],
        default='web'
    )
    
    # Notification Preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    desktop_notifications = models.BooleanField(default=False)
    
    # Multi-Platform Tracking
    last_platform = models.CharField(max_length=20, blank=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    device_token = models.CharField(max_length=255, blank=True)  # For push notifications
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    last_seen = models.DateTimeField(auto_now=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()
    
    class Meta:
        indexes = [
            models.Index(fields=['uuid']),
            models.Index(fields=['email']),
            models.Index(fields=['is_host', 'is_verified']),
        ]
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def platform_agnostic_id(self):
        """ID that can be used across all platforms"""
        return str(self.uuid)


class UserProfile(models.Model):
    """Extended profile information for multi-platform support."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Contact Information
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Host-specific Information
    host_description = models.TextField(blank=True)
    host_since = models.DateTimeField(null=True, blank=True)
    response_rate = models.IntegerField(default=100)
    response_time = models.CharField(max_length=50, default='within an hour')
    
    # Verification
    identity_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    
    # Payment Information (encrypted in production)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    stripe_account_id = models.CharField(max_length=100, blank=True)  # For hosts
    
    # Social Links
    website = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    
    # Platform Preferences
    theme = models.CharField(
        max_length=20,
        choices=[
            ('light', 'Light'),
            ('dark', 'Dark'),
            ('auto', 'Auto')
        ],
        default='light'
    )
    language = models.CharField(max_length=10, default='en')
    
    # Desktop App Specific
    desktop_sync_enabled = models.BooleanField(default=False)
    last_desktop_sync = models.DateTimeField(null=True, blank=True)
    
    # Analytics/Telemetry Consent
    allow_analytics = models.BooleanField(default=True)
    allow_crash_reports = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return f"{self.user.email}'s Profile"
