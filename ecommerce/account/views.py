from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django.core.mail import send_mail

from django.utils import timezone
from datetime import timedelta

from .serializers import RegisterSerializer, LoginSerializer, UpdateSerializer


class RegisterUserView(APIView):
    def post(self, request):
        try:
            data = request.data
            serializer = RegisterSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Your account is created.',
                    'data': serializer.data
                })
            
            return Response({
                'success': False,
                'message': 'Error occured.',
                'error': serializer.errors
            })
        
        except Exception as ex:
            return Response({
                'success': False,
                'message': 'Something went wrong.',
                'error': str(ex)
            })


class LoginUserView(APIView):
    def post(self, request):
        try:
            data = request.data
            serializer = LoginSerializer(data=data)

            if serializer.is_valid():
                response = serializer.get_jwt_token(serializer.validated_data)
                return Response(response)
            
            return Response({
                'success' : False,
                'message' : 'Error occured.',
                'error' : serializer.errors
            })
        
        except Exception as ex:
            return Response({
                'success': False,
                'message': 'Something went wrong.',
                'error': str(ex)
            })


class UpdateUserView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        try:
            serializer = UpdateSerializer(request.user, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Profile updated successfully.',
                    'data': serializer.data
                })
            
            return Response({
                'success': False,
                'message': 'Error occured.',
                'error': serializer.errors
            })
        
        except Exception as ex:
            return Response({
                'success': False,
                'message': 'Something went wrong.',
                'error': str(ex)
            })
        

class ForgotPasswordView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            user = get_object_or_404(User, email=data['email'])

            token = get_random_string(40)
            expiry_date = timezone.now() + timedelta(minutes=30)

            user.profile.reset_password_token = token
            user.profile.reset_password_expiry = expiry_date
            user.profile.save()

            def get_current_host(request):
                protocol = request.is_secure() and 'http' or 'https'
                host = request.get_host()
                return f"{protocol}://{host}/"
            
            host = get_current_host(request)

            link = f"{host}api/account/reset_password/{token}"
            body = f"Your password reset link is : {link}"

            send_mail(
                'Password reset for ecommerce site', # Subject
                body, # Message
                'noreply@ecom.djdev.com', # Sender
                [data['email']] # Recipient
            )

            return Response({
                'success': True,
                'message': f"Email for password reset is sent to {data['email']}"
            })
        
        except Exception as ex:
            return Response({
                'success': False,
                'message': 'Something went wrong.',
                'error': str(ex)
            })
        

class ResetPasswordView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, token):
        try:
            data = request.data
            user = get_object_or_404(User, profile__reset_password_token=token)
           
            if user.profile.reset_password_expiry < timezone.now():
                return Response({
                    'success': False,
                    'error': 'Token is expired.'
                })
            
            if data['password'] != data['confirm_password']:
                return Response({
                    'success': False,
                    'error': 'Passwords are not matching.'
                })
            
            user.password = make_password(data['password'])
            user.reset_password_token = ''
            user.reset_password_expiry = None

            user.profile.save()
            user.save()

            return Response({
                    'success': True,
                    'error': 'Password reset successfully.'
                })
        
        except Exception as ex:
            return Response({
                'success': False,
                'message': 'Something went wrong.',
                'error': str(ex)
            })