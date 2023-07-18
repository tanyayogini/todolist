from django.urls import path

from core.views import UserCreateView, UserLoginView, ProfileView, UpdatePasswordView

urlpatterns = [
    path('signup', UserCreateView.as_view()),
    path('login', UserLoginView.as_view()),
    path('profile', ProfileView.as_view()),
    path('update_password', UpdatePasswordView.as_view(),)
]
