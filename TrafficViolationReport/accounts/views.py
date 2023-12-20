"""
Module accounts.views

This module contains views related to handling user accounts in the Traffic Violation Report System. This includes user registration, login, email verification, and other account-related functionalities. The purpose is to manage user interactions with their account and streamline the process of user authentication and management.
"""

"""

This module contains the views for user account management, including login, registration, verification, and other account-related views.
"""

"""
Module accounts.views

This module contains the views for user account management, including login, registration, verification, and other account-related views.
"""

from django.contrib import messages
from django.shortcuts import redirect

from .forms import CustomUserCreationForm
from .models import User, UserProfile
from .utils import generate_random_code, send_mail


def redirect_if_authenticated(request):
    if request.user.is_authenticated:
        return redirect('home')

def login(request, *args, **kwargs):
    """
    Handles user login requests by authenticating users and redirecting to the home page upon successful login.

    Parameters:
    - request (HttpRequest): The request object containing the user's login credentials.
    - args: Additional positional arguments.
    - kwargs: Additional keyword arguments.

    Returns:
    - HttpResponse: Renders the login page or redirects to the home page upon successful login.
    """
    """
    View for user login. Redirects to the home page if the user is already authenticated.

    Parameters:
    - request: The HTTP request object
    - args: Additional positional arguments
    - kwargs: Additional keyword arguments

    Returns:
    - A rendered login view or a redirect to the home page
    """
    redirect_if_authenticated(request)
    return LoginView.as_view(template_name='accounts/login.html')(request, *args, **kwargs)

def check_username_exists(username):
    return User.objects.filter(username=username).exists()

def check_email_exists(email):
    return User.objects.filter(email=email).exists()

def validate_username_email(request):
    """
    Validates if the username or email already exists in the system to prevent duplicate entries.

    Parameters:
    - request: HttpRequest object containing 'username' and 'email' GET parameters.

    Returns:
    - JsonResponse containing the existence errors for both username and email, if any.
    """
    """
    Validates if the username or email already exists.

    Parameters:
    - request: The HTTP request object with 'username' and 'email' GET parameters.

    Returns:
    - JsonResponse with data containing potential errors for username and email
    """
    username = request.GET.get('username', None)
    email = request.GET.get('email', None)

    username_error = '這個用戶名已被使用' if check_username_exists(username) else None
    email_error = '這個電子郵件地址已被使用' if check_email_exists(email) else None

    data = {
        'username_error': username_error,
        'email_error': email_error
    }
    return JsonResponse(data)

def validate_form(request, form):
    """
    Validates a form based on a POST request and returns the form if it is valid.

    Parameters:
    - request: HttpRequest object for the current session.
    - form: The form instance to be validated.

    Returns:
    - The validated form instance if the form is valid; otherwise, None.
    """
    if request.method == 'POST' and form.is_valid():
        return form

def create_user(request, form):
    """
    Creates a user by validating a form and saving it if it is valid.

    Parameters:
    - request: HttpRequest object for the current session.
    - form: The form instance to create a user with.

    Returns:
    - The newly created User instance if the form is valid; otherwise, None.
    """
    validated_form = validate_form(request, form)
    if validated_form is not None:
        return validated_form.save()

def create_user_profile(user):
    """
    Creates a user profile for the given user.

    Parameters:
    - user: The User instance for which the profile is to be created.

    Returns:
    - The newly created UserProfile instance.
    """
    code = generate_random_code()
    UserProfile.objects.create(user=user, email_verified_code=code)
    return UserProfile.objects.get(user=user)

def send_verification_email(user):
    """
    Sends a verification email to the given user.

    Parameters:
    - user: The User instance to whom the verification email is to be sent.

    Returns:
    - None
    """
        subject="驗證您的帳戶",
        message="您的驗證碼是：{code}".format(code=code),
        from_email="trafficviolationtaiwan@gmail.com",
        recipient_list=[user.email],
        fail_silently=False,
    )

def redirect_to_verify():
    return redirect('verify')

def register(request):
    """
    Registers a user by creating a user, creating a user profile, sending a verification email, and redirecting to the verification page.

    Parameters:
    - request: HttpRequest object for the current session.

    Returns:
    - An HttpResponse object that redirects to the verification view upon successful registration, or renders the registration form view with errors if the registration fails.
    """
    form = CustomUserCreationForm(request.POST or None)
    form = validate_form(request, form)
    if form.is_valid():
        user = create_user(request, form)
        user_profile = create_user_profile(user)
        send_verification_email(user_profile)
        return redirect_to_verify()
    return render(request, 'accounts/register.html', {'form': form})

def verify_user_email(request, code):
    try:
        profile = UserProfile.objects.get(user=request.user, email_verified_code=code)
        profile.email_verified = True
        profile.email_verified_code = ''
        profile.save()
    except UserProfile.DoesNotExist:
        messages.error(request, '驗證碼錯誤。')
        return render(request, 'reports/verify.html')

def redirect_to_login():
    return redirect('login')

def verify(request):
    """
    Verifies a user's email address using a submitted verification code.

    Parameters:
    - request (HttpRequest): An object containing the verification code submitted by the user in a POST request.

    Returns:
    - An HttpResponse object that redirects to the login view upon successful verification,
      or renders the verification code form view with error messages if the verification fails.
    """
    """
    View for verifying a user's email. Processes the POST request with a verification code.

    Parameters:
    - request: The HTTP request object

    Returns:
    - A redirect to the login view or the verification code form view
    """
    if request.method == 'POST':
        code = request.POST.get('code')
        if not code:
            messages.error(request, '請輸入驗證碼。')
            return render(request, 'accounts/verify.html')

def account_view(request):
    """
    Displays the user's account information on the account view page.

    Parameters:
    - request: HttpRequest object for the current session.

    Returns:
    - HttpResponse object that renders the account view with the user's account information.
    """
    # Implementation for account view goes here
        verify_user_email(request, code)
        return redirect_to_login()
    return render(request, 'accounts/verify.html')
