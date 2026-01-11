from django.db import models
from django.conf import settings
import uuid

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('booking', 'Booking'),
        ('message', 'Message'),
        ('review', 'Review'),
        ('system', 'System'),
        ('promotion', 'Promotion'),
    ]
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    
    # Link to related object
    related_object_type = models.CharField(max_length=50, blank=True)
    related_object_id = models.CharField(max_length=100, blank=True)
    
    # Additional data
    data = models.JSONField(default=dict, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    
    # Platform delivery
    sent_to_email = models.BooleanField(default=False)
    sent_to_push = models.BooleanField(default=False)
    sent_to_web = models.BooleanField(default=False)
    sent_to_desktop = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
            models.Index(fields=['notification_type']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
    
    def mark_as_sent(self, platform=None):
        self.is_sent = True
        self.sent_at = timezone.now()
        
        if platform == 'email':
            self.sent_to_email = True
        elif platform == 'push':
            self.sent_to_push = True
        elif platform == 'web':
            self.sent_to_web = True
        elif platform == 'desktop':
            self.sent_to_desktop = True
        
        self.save()


class NotificationPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email notifications
    email_booking_updates = models.BooleanField(default=True)
    email_messages = models.BooleanField(default=True)
    email_reviews = models.BooleanField(default=True)
    email_promotions = models.BooleanField(default=False)
    email_system = models.BooleanField(default=True)
    
    # Push notifications
    push_booking_updates = models.BooleanField(default=True)
    push_messages = models.BooleanField(default=True)
    push_reviews = models.BooleanField(default=False)
    push_promotions = models.BooleanField(default=False)
    
    # Desktop notifications
    desktop_booking_updates = models.BooleanField(default=True)
    desktop_messages = models.BooleanField(default=True)
    desktop_reviews = models.BooleanField(default=True)
    
    # Web notifications
    web_booking_updates = models.BooleanField(default=True)
    web_messages = models.BooleanField(default=True)
    web_reviews = models.BooleanField(default=True)
    
    # Quiet hours
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(default='22:00')
    quiet_hours_end = models.TimeField(default='08:00')
    
    # Platform preferences
    preferred_notification_platform = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('push', 'Push'),
            ('web', 'Web'),
            ('desktop', 'Desktop')
        ],
        default='web'
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification preferences for {self.user.email}"
