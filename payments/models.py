from django.db import models
from django.conf import settings
import uuid
from properties.models import Property
from tenants.models import Tenant

# Move PAYMENT_METHODS to module level so it can be used by Expense class
PAYMENT_METHODS = [
    ('bank_transfer', 'Bank Transfer'),
    ('cash', 'Cash'),
    ('card', 'Credit/Debit Card'),
    ('check', 'Check'),
    ('eft', 'EFT'),
    ('mobile', 'Mobile Payment'),
    ('other', 'Other'),
]


class Payment(models.Model):
    """Payment model for rent and other payments"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_TYPES = [
        ('rent', 'Rent'),
        ('security_deposit', 'Security Deposit'),
        ('pet_deposit', 'Pet Deposit'),
        ('late_fee', 'Late Fee'),
        ('maintenance', 'Maintenance Fee'),
        ('utility', 'Utility Payment'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rental_property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    
    # Payment Information
    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPES,
        default='rent'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='ZAR')
    
    # Dates
    payment_date = models.DateField()
    due_date = models.DateField()
    received_date = models.DateField(null=True, blank=True)
    
    # Payment Details
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,  # Using the module-level variable
        default='bank_transfer'
    )
    reference_number = models.CharField(max_length=100, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Financial Details
    late_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    net_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    # Additional Information
    notes = models.TextField(blank=True)
    is_recurring = models.BooleanField(default=False)
    recurring_frequency = models.CharField(
        max_length=20,
        choices=[
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('annually', 'Annually'),
        ],
        blank=True
    )
    
    # Attachments
    receipt = models.FileField(
        upload_to='payment_receipts/',
        null=True,
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['rental_property', 'tenant', 'status']),
            models.Index(fields=['payment_date']),
            models.Index(fields=['status', 'due_date']),
            models.Index(fields=['reference_number']),
        ]
    
    def __str__(self):
        return f"Payment {self.reference_number or self.id} - {self.tenant.full_name}"
    
    def save(self, *args, **kwargs):
        # Calculate net amount
        self.net_amount = self.amount + self.late_fee - self.discount
        
        # Set received_date for completed payments
        if self.status == 'completed' and not self.received_date:
            self.received_date = self.payment_date
        
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if payment is overdue"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.status == 'pending' and today > self.due_date
    
    @property
    def days_overdue(self):
        """Calculate days overdue"""
        from django.utils import timezone
        if self.is_overdue:
            today = timezone.now().date()
            return (today - self.due_date).days
        return 0


class Invoice(models.Model):
    """Invoice model for billing"""
    
    INVOICE_STATUS = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rental_property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    
    # Invoice Information
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=INVOICE_STATUS,
        default='draft'
    )
    
    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Description
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    # Payment Link
    payment_link = models.URLField(blank=True)
    
    # Dates
    paid_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-invoice_date']
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.tenant.full_name}"
    
    @property
    def is_overdue(self):
        """Check if invoice is overdue"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.status in ['sent', 'overdue'] and today > self.due_date


class Expense(models.Model):
    """Expense model for property expenses"""
    
    EXPENSE_CATEGORIES = [
        ('maintenance', 'Maintenance'),
        ('repair', 'Repair'),
        ('utility', 'Utility'),
        ('insurance', 'Insurance'),
        ('tax', 'Tax'),
        ('management', 'Management Fee'),
        ('advertising', 'Advertising'),
        ('legal', 'Legal Fees'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rental_property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    
    # Expense Information
    category = models.CharField(
        max_length=20,
        choices=EXPENSE_CATEGORIES,
        default='maintenance'
    )
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='ZAR')
    
    # Dates
    expense_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    
    # Vendor Information
    vendor = models.CharField(max_length=200, blank=True)
    invoice_number = models.CharField(max_length=100, blank=True)
    
    # Payment Details
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,  # Now using the module-level variable
        default='bank_transfer'
    )
    
    # Status
    is_paid = models.BooleanField(default=False)
    
    # Attachments
    receipt = models.FileField(
        upload_to='expense_receipts/',
        null=True,
        blank=True
    )
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-expense_date']
    
    def __str__(self):
        return f"{self.description} - {self.rental_property.name}"
