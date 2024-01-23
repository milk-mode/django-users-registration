from django.urls import path
from user_app import views


app_name = 'user_app'

urlpatterns = [

    path('register/', views.register, name='register'),
    path('user_login/', views.user_login, name='user_login'),
    path('user_profile/', views.user_profile, name='user_profile'),


]
