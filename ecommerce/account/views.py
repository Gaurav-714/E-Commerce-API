from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
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