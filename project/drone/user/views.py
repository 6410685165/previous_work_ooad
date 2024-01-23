from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from user.models import Account
from task.models import Task
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework.authtoken.models import Token

# Create your views here.

def signin(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            if not user.is_superuser:
                account = Account.objects.get(user=request.user)
            return HttpResponseRedirect(reverse('task:index'))
        else:
            return render(request, "user/signin.html", {
                "messages": "Invalid credential."
            })
    return render(request, "user/signin.html")

def signup(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        repeat_password = request.POST.get('password2')
        authority = request.POST.get('authority')
        
        # Check if all required fields are filled out
        if not all([first_name, last_name, username, email, password, repeat_password]):
            messages.error(request, "Please fill out all fields")
            return render(request, "user/signup.html")
            
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address")
            return render(request, "user/signup.html")
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "This email is already taken")
            return render(request, "user/signup.html")
              
        # Check if password is at least 6 characters long
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long")
            return render(request, "user/signup.html")

        if password != repeat_password:
            messages.error(request, "Password didn't match")
            return render(request, "user/signup.html")
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "This username is already taken")
            return render(request, "user/signup.html")
        
        user = User.objects.create_user(first_name=first_name, 
                                   last_name=last_name, 
                                   username=username,
                                   email=email, 
                                   password=password)
        user.save()
        account = Account.objects.create(user=user, authority=authority)
        account.save()
        
        # Log in the user and redirect to home page
        user = authenticate(request, username=username, password=password)
        login(request, user)
        return HttpResponseRedirect(reverse('task:index'))
    return render(request, "user/signup.html")

def signout(request):
    logout(request)
    return HttpResponseRedirect(reverse('task:index'))

def view_profile(request, username):
    user = User.objects.get(username = username)
    user_account = Account.objects.get(user = user)
    if request.user.is_superuser:
        account = None
    else:
        account = Account.objects.get(user=request.user)
    task = Task.objects.filter(owner=username)
    return render(request, 'user/myprofile.html',{
        "account" : account,
        "user_account": user_account,
        "user_task": task,
    })

def settings(request):
    account = Account.objects.get(user = request.user)
    return render(request, 'user/edit_profile.html',{
        "account" : account,
    })

def edit_profile(request):
    user = request.user
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        repeat_password = request.POST.get('password2')
        profile_pics = request.FILES['file']
            
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address")
            return HttpResponseRedirect(reverse('user:settings'))
        
        if user.email != email and User.objects.filter(email=email).exists():
            messages.error(request, "This email is already taken")
            return HttpResponseRedirect(reverse('user:settings'))
              
        # Check if password is at least 6 characters long
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long")
            return HttpResponseRedirect(reverse('user:settings'))

        if password != repeat_password:
            messages.error(request, "Password didn't match")
            return HttpResponseRedirect(reverse('user:settings'))
        
        if user.username != username and User.objects.filter(username=username).exists():
            messages.error(request, "This username is already taken")
            return HttpResponseRedirect(reverse('user:settings'))
        
        account = Account.objects.get(user = user)
        user.first_name=first_name
        user.last_name=last_name
        user.username=username
        user.email=email
        user.set_password(password)

        user.save()
        account.user = user
        account.profile_pics = profile_pics
        account.save()
        login(request, user)

        return HttpResponseRedirect(reverse('user:settings'))
    return render(request, "user/edit_profile.html", {
        'account': account,
    })

def all_user_page(request):
    traffic_police = Account.objects.filter(authority='ตำรวจจราจร')
    local_police = Account.objects.filter(authority='ตํารวจส่วนท้องถิ่น')
    department_of_highway = Account.objects.filter(authority='กรมทางหลวง')
    return render(request, "user/users.html", {
        'traffic_police': traffic_police,
        'local_police': local_police,
        'department_of_highway': department_of_highway,
    })
