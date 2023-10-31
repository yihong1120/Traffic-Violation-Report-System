from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def home(request):
    return render(request, 'reports/home.html')

@login_required
def account_view(request):
    return render(request, 'reports/account.html', {'user': request.user})

@login_required
def dashboard(request):
    return render(request, 'reports/dashboard.html')