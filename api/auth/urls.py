from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.RegisterAPIView.as_view()),
    path("login/", views.login),
    path("logout/", views.logout),
    path('delete-account/', views.delete_account),
    path("profile/", views.ProfileAPIView.as_view()),
    path("change-password/", views.change_password),

    path('request-otp/',    views.RequestOTPView.as_view(),    name='request-otp'),

]
