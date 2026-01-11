from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone


class MaintenanceRequest(models.Model):
    """Model for maintenance requests"""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # We'll use generic foreign key for now to avoid circular imports
    property_id = models.UUIDField()
    property_name = models.CharField(max_length=200)
    
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_maintenance'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_maintenance'
    )
    
    # Maintenance details
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Dates
    reported_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    
    # Cost tracking
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    actual_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Additional information
    category = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    contractor_info = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    # Attachments
    attachment = models.FileField(
        upload_to='maintenance_attachments/',
        null=True,
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-reported_date', 'priority']
        indexes = [
            models.Index(fields=['property_id', 'status']),
            models.Index(fields=['priority', 'due_date']),
            models.Index(fields=['submitted_by', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.property_name}"
    
    @property
    def is_overdue(self):
        """Check if maintenance is overdue"""
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return self.due_date < timezone.now().date()
        return False
    
    @property
    def days_open(self):
        """Calculate number of days the request has been open"""
        if self.status == 'completed' and self.completed_date:
            return (self.completed_date.date() - self.reported_date.date()).days
        return (timezone.now().date() - self.reported_date.date()).days


class MaintenanceSchedule(models.Model):
    """Model for scheduled maintenance"""
    
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('biannually', 'Biannually'),
        ('annually', 'Annually'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property_id = models.UUIDField()
    property_name = models.CharField(max_length=200)
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='monthly'
    )
    
    # Schedule details
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    last_performed = models.DateField(null=True, blank=True)
    next_due = models.DateField()
    
    # Cost and time estimates
    estimated_duration = models.PositiveIntegerField(
        help_text="Duration in minutes",
        default=60
    )
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Requirements
    requirements = models.TextField(blank=True)
    contractor_required = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['next_due']
    
    def __str__(self):
        return f"{self.title} - {self.property_name}"
    
    def mark_as_completed(self):
        """Mark schedule as completed and update next due date"""
        self.last_performed = timezone.now().date()
        
        # Calculate next due date based on frequency
        if self.frequency == 'daily':
            self.next_due = self.last_performed + timezone.timedelta(days=1)
        elif self.frequency == 'weekly':
            self.next_due = self.last_performed + timezone.timedelta(weeks=1)
        elif self.frequency == 'monthly':
            self.next_due = self.last_performed + timezone.timedelta(days=30)
        elif self.frequency == 'quarterly':
            self.next_due = self.last_performed + timezone.timedelta(days=90)
        elif self.frequency == 'biannually':
            self.next_due = self.last_performed + timezone.timedelta(days=182)
        elif self.frequency == 'annually':
            self.next_due = self.last_performed + timezone.timedelta(days=365)
        
        self.save()


class MaintenanceCategory(models.Model):
    """Model for maintenance categories"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    estimated_duration = models.PositiveIntegerField(
        default=60,
        help_text="Default duration in minutes"
    )
    average_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name_plural = "Maintenance Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
