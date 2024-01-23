# -*- coding: utf-8 -*-

from django.shortcuts import render
from user_app.forms import UserForm, UserProfileInfoForm

from django.urls import reverse
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from azure.storage.blob import BlobServiceClient

from user_app.models import UserProfileInfo
# Create your views here.


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user:
            print('authenticated')
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('user_app:user_profile'))
            else:
                return HttpResponse('Account not active')

        else:
            print('Someone tried to login and failed')
            print('Username: {} and password {}'.format(username, password))
            return HttpResponse('Invalid login details supplied')

    else:
        return render(request, 'user_app/login.html', {})


@login_required
def user_profile(request):
    # get username,portfolio_site and profile_pic

    user = request.user
    user_profile, created = UserProfileInfo.objects.get_or_create(user=user)
    username = user.username
    email = user.email
    site = user_profile.portfolio_site
    pic = user_profile.profile_pic

    return render(request, 'user_app/user_profile.html', {'username': username, 'site': site, 'email': email, 'pic': pic})
   # return HttpResponse('You are logged in')


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def index(request):
    return render(request, 'user_app/index.html')


def register(request):
    registered = False

    user_form = UserForm(data=request.POST)
    profile_form = UserProfileInfoForm(data=request.POST)

    if user_form.is_valid() and profile_form.is_valid():
        user = user_form.save()
        user.set_password(user.password)
        user.save()

        profile = profile_form.save(commit=False)
        profile.user = user

        if 'profile_pic' in request.FILES:
            profile.profile_pic = request.FILES['profile_pic']

            # Upload the profile picture to Azure Blob Storage           
          
            blob_service_client = BlobServiceClient.from_connection_string("get the connection string")
            container_client = blob_service_client.get_container_client("container1")
            blob_client = container_client.get_blob_client(profile.profile_pic.name)
            blob_client.upload_blob(profile.profile_pic)
            
        profile.save()
        registered = True

    else:
        print(user_form.errors, profile_form.errors)

    user_form = UserForm()
    profile_form = UserProfileInfoForm()

    return render(request, 'user_app/registration.html', {'user_form': user_form,
                                                          'profile_form': profile_form,
                                                          'registered': registered})
