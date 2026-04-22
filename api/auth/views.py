from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView, GenericAPIView
from rest_framework import status
from rest_framework.views import APIView
# from rest_framework.authtoken.models import Token

from .serializers import (RegisterSerializer, LoginSerializer, UserProfileSerializer,
                          ChangePasswordSerializer, RequestOTPSerializer, VerifyOTPSerializer, ResetPasswordSerializer)
from users.models import User, PasswordResetOTP
from users.utils import generate_otp, send_otp_email


# Register
# @permission_classes([AllowAny])

@api_view(['POST'])
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

        PasswordResetOTP.objects.filter(user=user, is_used=False).update(is_used=True)

        otp = generate_otp(4)
        PasswordResetOTP.objects.create(user=user, otp=otp)

        send_otp_email(email, otp)

        return Response(
            {'message': 'Одноразовый пароль (OTP) будет отправлен на вашу электронную почту. Действителен в течение 5 минут.'},
            status=status.HTTP_200_OK
        )

