from django.shortcuts import render,redirect
from django.contrib.auth.models import User

# Create your views here.
def cadastro(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=email)
            
        except User.DoesNotExist:
            user = User.objects.create_user(username= email,email=email, password=password)
            user.save()
       
            return redirect('login')
        return render(request,'cadastro.html',{"msg":'Usuario já existe tente outro nome'})
    return render(request,'cadastro.html')