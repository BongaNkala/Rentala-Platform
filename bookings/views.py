from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import View, TemplateView, CreateView, ListView, DetailView
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods

from .models import Booking, Listing, BookingChangeRequest
from .forms import BookingForm, BookingChangeRequestForm


class BookingCreateView(CreateView):
    """Create a new booking"""
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/booking_create.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.listing = get_object_or_404(Listing, pk=self.kwargs['listing_id'])
        return super().dispatch(*args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['listing'] = self.listing
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.listing = self.listing
        form.instance.status = 'pending'
        
        # Calculate total price
        price_calculation = form.calculate_total_price()
        form.instance.total_price = price_calculation['total']
        
        # Save booking
        self.object = form.save()
        
        # Store price details in session for payment page
        self.request.session['booking_price_details'] = price_calculation
        self.request.session['booking_id'] = self.object.id
        
        messages.success(self.request, 'Booking request submitted! Please complete payment to confirm.')
        return redirect('bookings:payment', pk=self.object.pk)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['listing'] = self.listing
        
        # If form is bound, calculate price
        if self.request.method == 'POST' and self.request.POST:
            form = self.get_form()
            if form.is_valid():
                context['price_calculation'] = form.calculate_total_price()
        
        return context


class BookingDetailView(DetailView):
    """View booking details"""
    model = Booking
    template_name = 'bookings/booking_detail.html'
    context_object_name = 'booking'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        # Users can only see their own bookings
        return Booking.objects.filter(user=self.request.user)


class BookingListView(ListView):
    """List all bookings for a user"""
    model = Booking
    template_name = 'bookings/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 10
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        # Users can only see their own bookings
        queryset = Booking.objects.filter(user=self.request.user)
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')


class BookingPaymentView(DetailView):
    """Payment page for booking"""
    model = Booking
    template_name = 'bookings/booking_payment.html'
    context_object_name = 'booking'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user, status='pending')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get price details from session
        price_details = self.request.session.get('booking_price_details', {})
        context.update(price_details)
        
        return context


class HostBookingsListView(ListView):
    """List all bookings for a host's properties"""
    model = Booking
    template_name = 'bookings/host_bookings.html'
    context_object_name = 'bookings'
    paginate_by = 10
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        # Host can only see bookings for their own listings
        return Booking.objects.filter(
            listing__host=self.request.user
        ).order_by('-created_at')


@login_required
@require_http_methods(["POST"])
def cancel_booking(request, pk):
    """Cancel a booking"""
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    
    # Only allow cancellation if booking is pending or confirmed
    if booking.status in ['pending', 'confirmed']:
        booking.status = 'cancelled'
        booking.cancelled_at = timezone.now()
        booking.save()
        messages.success(request, 'Booking cancelled successfully.')
    else:
        messages.error(request, 'Cannot cancel this booking.')
    
    return redirect('bookings:list')


@login_required
@require_http_methods(["POST"])
def confirm_booking(request, pk):
    """Host confirms a booking"""
    booking = get_object_or_404(Booking, pk=pk, listing__host=request.user)
    
    if booking.status == 'pending':
        booking.status = 'confirmed'
        booking.confirmed_at = timezone.now()
        booking.save()
        messages.success(request, 'Booking confirmed successfully.')
    else:
        messages.error(request, 'Cannot confirm this booking.')
    
    return redirect('bookings:host_bookings')


@login_required
def check_availability(request, listing_id):
    """Check availability for a listing (API endpoint)"""
    listing = get_object_or_404(Listing, pk=listing_id)
    
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    
    if not check_in or not check_out:
        return JsonResponse({'error': 'Missing dates'}, status=400)
    
    try:
        check_in_date = timezone.datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_date = timezone.datetime.strptime(check_out, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    # Check for overlapping bookings
    overlapping = Booking.objects.filter(
        listing=listing,
        status__in=['pending', 'confirmed', 'active'],
        check_in__lt=check_out_date,
        check_out__gt=check_in_date
    ).exists()
    
    available = not overlapping
    
    # Calculate price if available
    price_calculation = {}
    if available:
        nights = (check_out_date - check_in_date).days
        if nights < 1:
            nights = 1
        
        base_price = listing.price_per_night * nights
        cleaning_fee = listing.cleaning_fee or 0
        service_fee = (base_price + cleaning_fee) * 0.10
        total = base_price + cleaning_fee + service_fee
        
        price_calculation = {
            'nights': nights,
            'base_price': round(base_price, 2),
            'cleaning_fee': round(cleaning_fee, 2),
            'service_fee': round(service_fee, 2),
            'total': round(total, 2)
        }
    
    return JsonResponse({
        'available': available,
        'price_calculation': price_calculation,
        'max_guests': listing.max_guests
    })
