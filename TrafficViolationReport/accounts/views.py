from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render

from .forms import CustomUserCreationForm
from .models import UserProfile


def validate_and_create_user(request, form):
    """
    Validates a user creation form and creates a new user if the form is valid.

    Parameters:
        request: The HTTP request.
        form: The user creation form.

    Returns:
        The created user if the form is valid, otherwise None.
    """
    if form.is_valid():
        user = form.save()
        return user

def authenticate_and_login_user(request, user, form):
    """
    Authenticates a user and logs them in if the authentication is successful.

    Parameters:
        request: The HTTP request.
        user: The user to authenticate.
        form: The form containing the user's credentials.

    This function does not return anything.
    """
    user = authenticate(username=user.username, password=form.cleaned_data['password1'])
    if user is not None:
        login(request, user)

def register_post_request(request):
    """
    Processes a form submission (POST request) for user registration.
    
    Parameters:
        request: The HTTP request containing the registration form.

    Returns:
        A redirect to the account verification page after successful registration.
    """
    """
    Processes a POST request during user registration.

    Parameters:
        request: The HTTP request containing the registration form.

    Returns:
        A redirect to the account verification page after successful registration.
    """
    form = CustomUserCreationForm(request.POST)
    user = validate_and_create_user(request, form)
    create_user_profile(user)
    authenticate_and_login_user(request, user, form)
    return redirect('accounts:verify')
def register_get_request(request):
    """
    Provides the registration form for a GET request.
    
    Parameters:
        request: The HTTP request.
    
    Returns:
        The rendered registration form.
    """
    form = handle_get_request()
    return CustomUserCreationForm()
def register(request):
    """
    Handles user registration by delegating to the appropriate function based on the method of the request.

    Parameters:
        request: The HTTP request.

    This function does not return anything.
    """
    if request.method == 'POST':
        return register_post_request(request)
    else:  # GET request
        return register_get_request(request)
