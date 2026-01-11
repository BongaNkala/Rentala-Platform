from django.shortcuts import render
from django.utils import timezone

def home(request):
    """Home page view - redirects to dashboard if authenticated, otherwise to login"""
    if request.user.is_authenticated:
        context = {
            'user': request.user,
            'current_date': timezone.now(),
        }
        return render(request, 'core/home.html', context)
    else:
        return render(request, 'core/landing.html')
