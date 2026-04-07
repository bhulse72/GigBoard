from django.shortcuts import render, redirect

def home(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    return redirect('accounts:login')