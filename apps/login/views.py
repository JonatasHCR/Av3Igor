from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
# Create your views here.
def entrar(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username = email, password = password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            return render(request,'login.html',{'msg':'Usuário ou senha estão incorretos'})
    return render(request,'login.html')

login_required
def sair(request):
    logout(request)
    return redirect('login')