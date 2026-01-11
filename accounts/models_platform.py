from django.db import models
from django.conf import settings
import uuid

class PlatformSession(models.Model):
    """Track user sessions across different platforms."""
    
    PLATFORM_CHOICES = [
        ('web', 'Web Browser'),
        ('desktop_windows', 'Desktop Windows'),
        ('desktop_mac', 'Desktop Mac'),
        ('desktop_linux', 'Desktop Linux'),
        ('mobile_ios', 'Mobile iOS'),
        ('mobile_android', 'Mobile Android'),
        ('api', 'API Client'),
    ]
    
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sessions')
    
    # Platform Information
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    platform_version = models.CharField(max_length=50, blank=True)
    app_version = models.CharField(max_length=20, blank=True)  # For desktop/mobile apps
    user_agent = models.TextField(blank=True)
    
    # Device Information
    device_id = models.CharField(max_length=255, blank=True)  # Unique device identifier
    device_name = models.CharField(max_length=100, blank=True)
    device_model = models.CharField(max_length=100, blank=True)
    os_version = models.CharField(max_length=50, blank=True)
    
    # Location
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Session Data
    is_active = models.BooleanField(default=True)
    auth_token = models.CharField(max_length=500, blank=True)  # JWT or session token
    refresh_token = models.CharField(max_length=500, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    logged_out_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['platform', 'created_at']),
            models.Index(fields=['device_id']),
            models.Index(fields=['expires_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.platform} - {self.created_at}"
    
    @property
    def duration(self):
        if self.logged_out_at:
            return self.logged_out_at - self.created_at
        return None


class PlatformSettings(models.Model):
    """Platform-specific settings for each user."""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='platform_settings')
    platform = models.CharField(max_length=20, choices=PlatformSession.PLATFORM_CHOICES)
    
    # Notification Settings per platform
    enable_notifications = models.BooleanField(default=True)
    notification_sound = models.BooleanField(default=True)
    notification_vibrate = models.BooleanField(default=False)  # For mobile
    
    # UI/UX Preferences
    compact_view = models.BooleanField(default=False)
    font_size = models.CharField(max_length=20, default='medium')
    reduce_animations = models.BooleanField(default=False)
    
    # Data Usage
    sync_on_wifi_only = models.BooleanField(default=False)
    image_quality = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('original', 'Original')
        ],
        default='medium'
    )
    
    # Desktop App Specific
    auto_start = models.BooleanField(default=False)
    minimize_to_tray = models.BooleanField(default=True)
    check_for_updates = models.BooleanField(default=True)
    
    # Mobile App Specific
    background_refresh = models.BooleanField(default=True)
    save_to_gallery = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'platform']
        verbose_name_plural = 'Platform Settings'
    
    def __str__(self):
        return f"{self.user.email} - {self.platform} Settings"
