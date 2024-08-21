from rest_framework import serializers
from .models import CustomUser, UserProfile
from django.contrib.auth import authenticate
from .models import CustomUser
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .utils import Util




class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ['address_line_1', 'address_line_2', 'profile_image', 'city', 'state', 'country']


class CustomUserSerializer(serializers.ModelSerializer):
    
    userprofile = UserProfileSerializer()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'userprofile']
        
    def update(self, instance, validated_data):
        userprofile_data = validated_data.pop('userprofile', None)

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.save()


        if userprofile_data:
            user_profile, created = UserProfile.objects.get_or_create(user=instance)
            for attr, value in userprofile_data.items():
                setattr(user_profile, attr, value)
            user_profile.save()

        return instance


class RegisterSerializer(serializers.ModelSerializer):
    
    confirm_password= serializers.CharField(write_only=True, style={'input_type':'password'})

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}}
        }

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        if password != confirm_password:
            raise serializers.ValidationError("confirm password doesn't match.")
        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password']
        )
        return user

class LoginSerializer(serializers.Serializer):
    
    email = serializers.EmailField(max_length=255, required=True)
    password = serializers.CharField(max_length=255, required=True)
    
    class Meta:
        model = CustomUser
        fields = ['email', 'password']
        extra_kwargs = {
            'password':{'write_only':True}
        }
        
        
class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
    password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
    confirm_password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
    
    class Meta:
        fields = ['current_password', 'password', 'confirm_password']
        
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Confirm password does not match."})
        return data


class SendPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, required=True)
    
    class Meta:
        fields = ['email']
        
    def validate(self, data):
        email = data['email']
    
        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            link = f'http://localhost/8000/api/user/reset-password/{uid}/{token}/'
            body = 'Click following link to reset you password ' + link
            data = {
                'subject':'reset your password',
                'body': body,
                'to_email':user.email,
            }
            Util.send_email(data)
            return data
        else:
            return serializers.ValidationError('you are not a registered user.')
        
        
        
        

class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    confirm_password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    class Meta:
        fields = ['password', 'confirm_password']

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        uid = self.context.get('uid')
        token = self.context.get('token')

        if password != confirm_password:
            raise serializers.ValidationError('Confirm password does not match.')

        try:
            user_id = smart_str(urlsafe_base64_decode(uid))
            user = CustomUser.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError('Token is not valid or expired.')

            user.set_password(password)
            user.save()

        except DjangoUnicodeDecodeError:
            raise serializers.ValidationError('token is not valid or expired.')

        return data
    
    
