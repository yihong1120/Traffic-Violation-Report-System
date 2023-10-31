from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from .forms import CustomUserCreationForm

def home(request):
    return render(request, 'reports/home.html')

def login(request, *args, **kwargs):
    # 如果用戶已登入，重定向到首頁
    if request.user.is_authenticated:
        return redirect('home')
    return LoginView.as_view()(request, *args, **kwargs)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'reports/register.html', {'form': form})

@login_required
def account_view(request):
    return render(request, 'reports/account.html', {'user': request.user})

@login_required
def dashboard(request):
    return render(request, 'reports/dashboard.html')