from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard:index')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def register(request):
    # Simple registration view for now
    return render(request, 'accounts/register.html')

def profile_view(request):
    return render(request, 'accounts/profile.html')
