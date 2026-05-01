from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from users.models import User, PasswordResetOTP


class RequestRegisterOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp   = serializers.CharField(max_length=4)

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь с этим адресом электронной почты не найден")

        otp_obj = PasswordResetOTP.objects.filter(
            user=user,
            otp=data['otp'],
            is_used=False,
            is_verified=False,
        ).last()

        if not otp_obj:
            raise serializers.ValidationError("Недействительный OTP.")

        if otp_obj.is_expired():
            raise serializers.ValidationError("Срок действия одноразового пароля истек. Пожалуйста, запросите новый пароль.")

        # attach to validated_data for the view to use
        data['otp_obj'] = otp_obj
        data['user'] = user
        return data


# Registration
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Пароли не совпадают!")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)  
        return user
    

# Login 
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(email=attrs['email'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError("Неверный email или пароль")

        token, _ = Token.objects.get_or_create(user=user)
        return {"token": token.key, "email": user.email}
    

# Profile 
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'first_name', "last_name", 'phone_number', "bio",
                  "address", "avatar", "date_joined")
        read_only_fields = ('email',) 


# Change Password
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True, 
        validators=[validate_password]
    )

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError(
                "Старый пароль неверный")
        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(
            self.validated_data['new_password'])
        user.save()
        return user
    



class RequestOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Пользователь с этим адресом электронной почты не найден."
            )
        return value


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp   = serializers.CharField(max_length=4)

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь с этим адресом электронной почты не найден")

        otp_obj = PasswordResetOTP.objects.filter(
            user=user,
            otp=data['otp'],
            is_used=False,
            is_verified=False,
        ).last()

        if not otp_obj:
            raise serializers.ValidationError("Недействительный OTP.")

        if otp_obj.is_expired():
            raise serializers.ValidationError("Срок действия одноразового пароля истек. Пожалуйста, запросите новый пароль.")

        # attach to validated_data for the view to use
        data['otp_obj'] = otp_obj
        data['user'] = user
        return data


class ResetPasswordSerializer(serializers.Serializer):
    email        = serializers.EmailField()
    reset_token  = serializers.CharField()  
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Пароли не совпадают.")
        
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь с этим адресом электронной почты не найден")
        
        try:
            otp_obj = PasswordResetOTP.objects.get(
                id=data['reset_token'],
                user=user,
                is_verified=True,
                is_used=False,
            )
        except PasswordResetOTP.DoesNotExist:
            raise serializers.ValidationError("Недействительный или просроченный токен сброса.")

        if otp_obj.is_expired():
            raise serializers.ValidationError("Сброс сессии завершен. Пожалуйста, начните заново.")
        
        validate_password(data['new_password'], user)
        
        data['user'] = user
        data['otp_obj'] = otp_obj
        return data