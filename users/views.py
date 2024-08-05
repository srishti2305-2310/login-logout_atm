from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db.models import Q
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework.authtoken.models import Token
from .utils import generate_access_token, generate_refresh_token, decode_token,token_required
import utils as utl

@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def user_login(request):
    username_or_email = request.data.get('username')
    password = request.data.get('password')

    if not username_or_email or not password:
        return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(Q(username=username_or_email) | Q(email=username_or_email))
    except CustomUser.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.check_password(password):
        return Response({'error': 'Incorrect password'}, status=status.HTTP_401_UNAUTHORIZED)

    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)

    user_data = UserSerializer(user).data
    print("user--->",user_data)
    user_data.update({
        "access_token":access_token,
        "refresh_token":refresh_token
    })
    
  
    return Response(user_data, status=status.HTTP_200_OK)
@api_view(['POST'])
@token_required
def user_logout(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            request.user.auth_token.delete()
            return Response({"message": "You are logged out successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "User is not authenticated"}, status=status.HTTP_400_BAD_REQUEST)
        #Before
    # try: 
    #     # Get the token from the request
    #     username = request.username
    #     user = User.objects.get(username = username)
    #     if username.is_authenticated:
    #         return Response({'message': 'User is not authenticated'}, status=status.HTTP_400_BAD_REQUEST)
        
    #     #Performing logout
    #     user_logout(request)


    #          # Remove the user's token
    #     token = Token.objects.filter(username=username).first()
    #     if token:
    #         token.delete()
        
    #     return Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)
    
    # except Exception as e:
    #     return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

        payload = decode_token(refresh_token)
        if isinstance(payload, dict) and 'error' in payload:
            return Response({'error': payload['error']}, status=status.HTTP_401_UNAUTHORIZED)

        if not payload:
            return Response({'error': 'Invalid or expired refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            user = CustomUser.objects.get(id=payload['user_id'])
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        new_access_token = generate_access_token(user)
        return Response({'access': new_access_token}, status=status.HTTP_200_OK)
