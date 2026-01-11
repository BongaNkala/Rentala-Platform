from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
from listings.models import Listing


class Booking(models.Model):
    """Booking model for rental reservations"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('active', 'Active'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    
    # Booking details
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField(default=1)
    special_requests = models.TextField(blank=True)
    
    # Pricing
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Status and timestamps
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Payment reference (for Stripe)
    payment_intent_id = models.CharField(max_length=100, blank=True)
    payment_status = models.CharField(max_length=20, default='pending')
    
    # Review tracking
    is_reviewed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['listing', 'check_in', 'check_out']),
            models.Index(fields=['payment_status']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.listing.title} ({self.check_in} to {self.check_out})"
    
    @property
    def nights(self):
        """Calculate number of nights"""
        if self.check_in and self.check_out:
            return (self.check_out - self.check_in).days
        return 0
    
    @property
    def is_active(self):
        """Check if booking is currently active"""
        if not self.check_in or not self.check_out:
            return False
        
        today = timezone.now().date()
        return self.status == 'active' and self.check_in <= today <= self.check_out
    
    @property
    def is_upcoming(self):
        """Check if booking is upcoming"""
        if not self.check_in:
            return False
        
        today = timezone.now().date()
        return self.status == 'confirmed' and self.check_in > today
    
    @property
    def is_past(self):
        """Check if booking is in the past"""
        if not self.check_out:
            return False
        
        today = timezone.now().date()
        return self.check_out < today
    
    def confirm_booking(self):
        """Mark booking as confirmed"""
        self.status = 'confirmed'
        self.confirmed_at = timezone.now()
        self.save()
    
    def cancel_booking(self):
        """Mark booking as cancelled"""
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.save()
    
    def complete_booking(self):
        """Mark booking as completed"""
        self.status = 'completed'
        self.save()


class BookingChangeRequest(models.Model):
    """Model for booking change requests (modifications)"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='change_requests'
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    
    # Requested changes
    requested_check_in = models.DateField(null=True, blank=True)
    requested_check_out = models.DateField(null=True, blank=True)
    requested_guests = models.PositiveIntegerField(null=True, blank=True)
    
    # Price adjustment
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reason = models.TextField()
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    response_note = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Change request for {self.booking}"


class BookingMessage(models.Model):
    """Messages between guest and host about a specific booking"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_booking_messages'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_booking_messages'
    )
    
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender} about {self.booking}"
