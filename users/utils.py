import random
from django.core.mail import send_mail
from django.conf import settings


def generate_otp(length=4):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def send_otp_email(email, otp, subject, message):
    # subject = 'Сброс пароля с помощью OTP'
    # message = f'''{otp} - это ваш 
    # одноразовый пароль для сброса пароля. Он действителен в течение 5 минут.'''
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )