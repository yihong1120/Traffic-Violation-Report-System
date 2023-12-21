from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render

from .forms import CustomUserCreationForm
from .models import UserProfile


def validate_and_create_user(request, form):
    if form.is_valid():
        user = form.save()
        return user

def authenticate_and_login_user(request, user, form):
    user = authenticate(username=user.username, password=form.cleaned_data['password1'])
    if user is not None:
        login(request, user)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        user = validate_and_create_user(request, form)
        create_user_profile(user)
        authenticate_and_login_user(request, user, form)
        return redirect('accounts:verify')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})
