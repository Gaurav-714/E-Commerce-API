from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate


class RegisterSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = User
        fields = ['first_name','last_name','email','password']
        extra_kwargs = {
            'first_name': { 'required': True },
            'last_name': { 'required': True },
            'email': { 'required': True },
            'password': { 'required': True, 'write_only': True }
        }

    def validate(self, data):
        user = User.objects.filter(username=data['email'])
        if user.exists():
            raise serializers.ValidationError('User already exists.')
        return data
    
    def create(self, validated_data):
        user = User.objects.create(
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            email = validated_data['email'],
            username = validated_data['email'],
            password = make_password(validated_data['password'])
        )
        return user


class LoginSerializer(serializers.Serializer):

    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = User.objects.filter(username=data['username'])
        if not user.exists():
            raise serializers.ValidationError('Account does not exists.')
        return data
    
    def get_jwt_token(self, validated_data):
        user = authenticate(username=validated_data['username'], password=validated_data['password'])
        if user:
            refresh = RefreshToken.for_user(user)
            return {'message':'Logged in successfully.', 'data':{'token':{'refresh':str(refresh), 'access':str(refresh.access_token)}}}
        else:
            return {'message':'Invalid credentials.', 'data':{}}



class UpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['first_name','last_name','email','password']

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return User.objects.create(**validated_data)
    