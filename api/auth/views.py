from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView, GenericAPIView
from rest_framework import status
from rest_framework.views import APIView
# from rest_framework.authtoken.models import Token

from .serializers import (RegisterSerializer, LoginSerializer, UserProfileSerializer,
                          ChangePasswordSerializer, RequestOTPSerializer, VerifyOTPSerializer, 
                          ResetPasswordSerializer,
                          RequestRegisterOTPSerializer)
from users.models import User, PasswordResetOTP
from users.utils import generate_otp, send_otp_email


class RequestRegisterOTPView(APIView):
    def post(self, request):
        serializer = RequestRegisterOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        PasswordResetOTP.objects.filter(
            email=email, is_used=False, 
            purpose="register"
        ).update(is_used=True)

        otp = generate_otp(4)
        PasswordResetOTP.objects.create(email=email, otp=otp, purpose="register")

        subject = 'OTP-код для регистрации.'
        message = f'''{otp} - это ваш 
        одноразовый пароль для регистрации. Он действителен в течение 5 минут.'''

        send_otp_email(email, otp, subject, message)

        return Response(
            {'message': 'Одноразовый пароль (OTP) будет отправлен на вашу электронную почту. Действителен в течение 5 минут.'},
            status=status.HTTP_200_OK
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"message": "Пользователь успешно создан!"})


class RegisterAPIView(GenericAPIView):
    pass

# Login
# @permission_classes([AllowAny])
@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response(serializer.validated_data)   


# Logout
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    print(request.user)
    Token.objects.filter(user=request.user).delete()
    return Response({"message": "Токен успешно удалён, пользователь разлогинен!"})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    user = request.user
    Token.objects.filter(user=user).delete()
    user.delete()
    return Response({"message": "Аккаунт успешно удалён!"})


class ProfileAPIView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()

    def get_object(self):
        user = self.request.user
        return user
    

# Change Password
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(
        data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"message": "Пароль успешно изменён!"}, 
                    status=status.HTTP_200_OK)



class RequestOTPView(APIView):
    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.get(email=email)

        PasswordResetOTP.objects.filter(user=user, is_used=False, purpose="reset_password").update(is_used=True)

        otp = generate_otp(4)
        PasswordResetOTP.objects.create(user=user, otp=otp, purpose="reset_password")

        subject = 'Сброс пароля с помощью OTP'
        message = f'''{otp} - это ваш 
        одноразовый пароль для сброса пароля. Он действителен в течение 5 минут.'''

        send_otp_email(email, otp, subject, message)

        return Response(
            {'message': 'Одноразовый пароль (OTP) будет отправлен на вашу электронную почту. Действителен в течение 5 минут.'},
            status=status.HTTP_200_OK
        )


class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp_obj = serializer.validated_data['otp_obj']
        otp_obj.is_verified = True
        otp_obj.save()

        return Response(
            {
                'message': 'OTP-код успешно подтвержден.',
                'reset_token': str(otp_obj.id),
            },
            status=status.HTTP_200_OK
        )
    

class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        otp_obj = serializer.validated_data['otp_obj']

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        otp_obj.is_used = True
        otp_obj.save()

        return Response(
            {'message': 'Пароль успешно сброшен. Теперь вы можете войти в систему.'},
            status=status.HTTP_200_OK
        )