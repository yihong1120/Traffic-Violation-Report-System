"""
This file contains views for the accounts app in the Traffic Violation Report system.
"""

from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render

from .forms import RegistrationForm


def validate_and_create_user(request):
    """
    Validates the user registration form and creates a new user if the form is valid.
    """
    form = RegistrationForm(request.POST)
    if form.is_valid():
        form.save()
        return True
    return False

def authenticate_and_login_user(request):
    """
    Authenticates a user with the provided username and password and logs them in if the authentication is successful.
    """
    username = request.POST['username']
    password = request.POST['password1']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return True
    return False

def handle_post_request(request):
    """
    Handles POST requests to the register endpoint. Validates and creates a new user if the request data is valid.
    """
    if validate_and_create_user(request):
        if authenticate_and_login_user(request):
            return redirect('home')
    return render(request, 'register.html', {'form': RegistrationForm()})

def handle_get_request(request):
    """
    Handles GET requests to the register endpoint. Returns a registration form.
    """
    return render(request, 'register.html', {'form': RegistrationForm()})

def register(request):
    """
    Main view for the register endpoint. Handles both GET and POST requests.
    """
    if request.method == 'POST':
        return handle_post_request(request)
    return handle_get_request(request)
