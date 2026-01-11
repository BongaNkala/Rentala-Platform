from django.db import models
from django.conf import settings
import uuid
from properties.models import Property


class Tenant(models.Model):
    """Tenant model for property tenants"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
        ('evicted', 'Evicted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rental_property = models.ForeignKey(  # Changed from 'property' to 'rental_property'
        Property,
        on_delete=models.CASCADE,
        related_name='tenants'
    )
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    alternate_phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Address (if different from property)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Employment Information
    employer = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    monthly_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relationship = models.CharField(max_length=100, blank=True)
    
    # Lease Information
    lease_start_date = models.DateField()
    lease_end_date = models.DateField()
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    pet_deposit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    
    # Additional Information
    notes = models.TextField(blank=True)
    pets = models.TextField(blank=True)
    vehicles = models.TextField(blank=True)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    move_in_date = models.DateField(null=True, blank=True)
    move_out_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['rental_property', 'status']),
            models.Index(fields=['email']),
            models.Index(fields=['last_name', 'first_name']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def lease_status(self):
        """Check lease status"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.status != 'active':
            return self.status
        
        if today < self.lease_start_date:
            return 'upcoming'
        elif self.lease_start_date <= today <= self.lease_end_date:
            return 'active'
        elif today > self.lease_end_date:
            return 'expired'
        return 'unknown'
    
    @property
    def is_lease_active(self):
        """Check if lease is currently active"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.lease_start_date <= today <= self.lease_end_date and self.status == 'active'


class TenantDocument(models.Model):
    """Documents for tenants"""
    DOCUMENT_TYPES = [
        ('id', 'ID/Passport'),
        ('lease', 'Lease Agreement'),
        ('employment', 'Employment Verification'),
        ('credit', 'Credit Report'),
        ('background', 'Background Check'),
        ('other', 'Other'),
    ]
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='tenant_documents/')
    description = models.TextField(blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-upload_date']
    
    def __str__(self):
        return f"{self.title} - {self.tenant.full_name}"


class TenantNote(models.Model):
    """Notes about tenants"""
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='notes_history'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    note = models.TextField()
    is_important = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note for {self.tenant.full_name} - {self.created_at.date()}"
