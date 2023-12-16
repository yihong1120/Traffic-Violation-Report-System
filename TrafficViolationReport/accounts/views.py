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
    - request: HttpRequest object containing login credentials.
    - args: Additional positional arguments.
    - kwargs: Additional keyword arguments.

    Returns:
    - HttpResponse object that represents the login page, or a redirection to the home page if the login is successful.
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

def handle_post_request(request, form):
    if request.method == 'POST':
        if form.is_valid():
            return form.save()

def create_user_profile(user):
    code = generate_random_code()
    UserProfile.objects.create(user=user, email_verified_code=code)
    return code

def send_verification_email(user, code):
    send_mail(
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
    View for user registration. Processes the registration form and sends a verification email.

    Parameters:
    - request: The HTTP request object

    Returns:
    - A redirect to the verification view or the registration form view
    """
    form = CustomUserCreationForm(request.POST if request.method == 'POST' else None)
    user = handle_post_request(request, form)
    if user:
        code = create_user_profile(user)
        send_verification_email(user, code)
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
        verify_user_email(request, code)
        return redirect_to_login()
    return render(request, 'accounts/verify.html')
