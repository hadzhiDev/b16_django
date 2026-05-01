from django.urls import path

from . import views

urlpatterns = [
    path("register/request-otp/", views.RequestRegisterOTPView.as_view()),
    # path("register/verify-otp/"),
    path("register/complate/", views.RegisterAPIView.as_view()),
    path("login/", views.login),
    path("logout/", views.logout),
    path('delete-account/', views.delete_account),
    path("profile/", views.ProfileAPIView.as_view()),
    path("change-password/", views.change_password),

    path('request-otp/',    views.RequestOTPView.as_view(),    name='request-otp'),
    path('verify-otp/',     views.VerifyOTPView.as_view(),     name='verify-otp'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset-password'),
]
