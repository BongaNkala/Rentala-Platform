from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
import datetime
from .models import Booking, Listing, BookingChangeRequest


class DateInput(forms.DateInput):
    input_type = 'date'
    
    def __init__(self, **kwargs):
        kwargs.setdefault('attrs', {})
        kwargs['attrs'].update({'class': 'form-control', 'min': timezone.now().date().isoformat()})
        super().__init__(**kwargs)


class BookingForm(forms.ModelForm):
    """Form for creating a new booking"""
    check_in = forms.DateField(
        widget=DateInput(),
        label="Check-in Date"
    )
    check_out = forms.DateField(
        widget=DateInput(),
        label="Check-out Date"
    )
    guests = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Number of Guests"
    )
    special_requests = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any special requests or questions for the host?'
        }),
        label="Special Requests"
    )
    
    class Meta:
        model = Booking
        fields = ['check_in', 'check_out', 'guests', 'special_requests']
    
    def __init__(self, *args, **kwargs):
        self.listing = kwargs.pop('listing', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.listing:
            # Set max guests based on listing capacity
            self.fields['guests'].max_value = self.listing.max_guests
            self.fields['guests'].widget.attrs['max'] = self.listing.max_guests
    
    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        guests = cleaned_data.get('guests')
        
        if check_in and check_out:
            # Check dates are valid
            if check_in < timezone.now().date():
                raise ValidationError({'check_in': 'Check-in date cannot be in the past.'})
            
            if check_out <= check_in:
                raise ValidationError({'check_out': 'Check-out date must be after check-in date.'})
            
            # Check minimum stay
            nights = (check_out - check_in).days
            if self.listing and nights < self.listing.minimum_stay:
                raise ValidationError(f'Minimum stay is {self.listing.minimum_stay} nights.')
            
            # Check maximum stay if set
            if self.listing and self.listing.maximum_stay and nights > self.listing.maximum_stay:
                raise ValidationError(f'Maximum stay is {self.listing.maximum_stay} nights.')
        
        if guests and self.listing:
            # Check capacity
            if guests > self.listing.max_guests:
                raise ValidationError({'guests': f'This property can only accommodate {self.listing.max_guests} guests.'})
        
        return cleaned_data
    
    def calculate_total_price(self):
        """Calculate total price based on dates and listing price"""
        if not self.listing or not self.cleaned_data.get('check_in') or not self.cleaned_data.get('check_out'):
            return 0
        
        check_in = self.cleaned_data['check_in']
        check_out = self.cleaned_data['check_out']
        
        # Calculate number of nights
        nights = (check_out - check_in).days
        if nights < 1:
            nights = 1
        
        # Base price (using price_per_day as nightly rate)
        base_price = self.listing.price_per_day * nights
        
        # For now, no cleaning fee in the model - could add later
        cleaning_fee = 0
        
        # Add service fee (10%)
        service_fee = (base_price + cleaning_fee) * 0.10
        total = base_price + cleaning_fee + service_fee
        
        return {
            'nights': nights,
            'base_price': float(base_price),
            'cleaning_fee': float(cleaning_fee),
            'service_fee': float(service_fee),
            'total': round(float(total), 2)
        }


class BookingChangeRequestForm(forms.ModelForm):
    """Form for requesting booking changes"""
    requested_check_in = forms.DateField(
        widget=DateInput(),
        required=False,
        label="New Check-in Date"
    )
    requested_check_out = forms.DateField(
        widget=DateInput(),
        required=False,
        label="New Check-out Date"
    )
    requested_guests = forms.IntegerField(
        min_value=1,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="New Number of Guests"
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Please explain why you need to change your booking...'
        }),
        label="Reason for Change"
    )
    
    class Meta:
        model = BookingChangeRequest
        fields = ['requested_check_in', 'requested_check_out', 'requested_guests', 'reason']
    
    def __init__(self, *args, **kwargs):
        self.booking = kwargs.pop('booking', None)
        super().__init__(*args, **kwargs)
        
        if self.booking:
            # Set initial values
            self.fields['requested_check_in'].initial = self.booking.check_in
            self.fields['requested_check_out'].initial = self.booking.check_out
            self.fields['requested_guests'].initial = self.booking.guests
            
            # Set max guests based on listing
            if self.booking.listing:
                self.fields['requested_guests'].max_value = self.booking.listing.max_guests
    
    def clean(self):
        cleaned_data = super().clean()
        
        # At least one field should be changed
        changed = False
        if self.booking:
            if cleaned_data.get('requested_check_in') and cleaned_data['requested_check_in'] != self.booking.check_in:
                changed = True
            if cleaned_data.get('requested_check_out') and cleaned_data['requested_check_out'] != self.booking.check_out:
                changed = True
            if cleaned_data.get('requested_guests') and cleaned_data['requested_guests'] != self.booking.guests:
                changed = True
        
        if not changed:
            raise ValidationError('Please make at least one change to your booking.')
        
        return cleaned_data
