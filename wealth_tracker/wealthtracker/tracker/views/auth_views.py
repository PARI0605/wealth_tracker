from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm

from tracker.forms import SignUpForm


def landing_view(request):
    """
    Public marketing landing page.
    Automatically redirects logged-in users to their dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'tracker/landing.html')


def signup_view(request):
    """
    User registration with dual-panel layout.
    Automatically establishes authenticated session on successful creation.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()

    return render(request, 'tracker/signup.html', {'form': form})


def login_view(request):
    """
    User authentication with dual-panel layout.
    Redirects to `next` query parameter or defaults to dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next') or request.POST.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'tracker/login.html', {'form': form})


def logout_view(request):
    """
    Terminates session and redirects user to public landing showcase.
    """
    logout(request)
    return redirect('landing')
