from django.db import models
from django.conf import settings
import uuid
from django.utils.text import slugify


class Property(models.Model):
    """Property model for rental properties"""
    
    PROPERTY_TYPES = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('mixed', 'Mixed Use'),
        ('industrial', 'Industrial'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
        ('vacant', 'Vacant'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_properties'
    )
    
    # Basic Information
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    property_type = models.CharField(
        max_length=20,
        choices=PROPERTY_TYPES,
        default='residential'
    )
    
    # Address
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True
    )
    
    # Property Details
    year_built = models.PositiveIntegerField(null=True, blank=True)
    total_units = models.PositiveIntegerField(default=1)
    occupied_units = models.PositiveIntegerField(default=0)
    square_feet = models.PositiveIntegerField(null=True, blank=True)
    lot_size = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    # Financial Information
    purchase_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    current_value = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    monthly_rent = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    # Amenities
    amenities = models.TextField(blank=True)
    parking_spaces = models.PositiveIntegerField(default=0)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    is_featured = models.BooleanField(default=False)
    
    # Dates
    purchase_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Properties"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['city', 'country']),
            models.Index(fields=['property_type']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure slug is unique
            original_slug = self.slug
            counter = 1
            while Property.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    @property
    def vacancy_rate(self):
        """Calculate vacancy rate"""
        if self.total_units > 0:
            vacant = self.total_units - self.occupied_units
            return (vacant / self.total_units) * 100
        return 0
    
    @property
    def total_rent_income(self):
        """Calculate total monthly rent income"""
        if self.monthly_rent:
            return self.occupied_units * self.monthly_rent
        return 0


class PropertyImage(models.Model):
    """Images for properties"""
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='property_images/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', '-is_primary']
    
    def __str__(self):
        return f"Image for {self.property.name}"


class PropertyDocument(models.Model):
    """Documents for properties"""
    DOCUMENT_TYPES = [
        ('deed', 'Deed'),
        ('mortgage', 'Mortgage'),
        ('insurance', 'Insurance'),
        ('inspection', 'Inspection Report'),
        ('other', 'Other'),
    ]
    
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='property_documents/')
    description = models.TextField(blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-upload_date']
    
    def __str__(self):
        return f"{self.title} - {self.property.name}"
