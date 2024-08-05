from functools import wraps
from urllib import request, response
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import status
from django.http import HttpResponse, JsonResponse
from .models import CustomUser

# Secret key for signing the JWT
SECRET_KEY = settings.SECRET_KEY

# Token expiration time
ACCESS_TOKEN_LIFETIME = timedelta(minutes=5)
REFRESH_TOKEN_LIFETIME = timedelta(days=1)

def generate_access_token(user):
    expiration = datetime.utcnow() + ACCESS_TOKEN_LIFETIME
    payload = {
        'user_id': user.id,
        'exp': expiration,
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def generate_refresh_token(user):
    expiration = datetime.utcnow() + REFRESH_TOKEN_LIFETIME
    payload = {
        'user_id': user.id,
        'exp': expiration,
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return JsonResponse({"message": "Token is expired"}, status=status.HTTP_498_INVALID_TOKEN)
    except jwt.InvalidTokenError:
        return JsonResponse({"message": "Invalid token"}, status=status.HTTP_403_FORBIDDEN)


def token_required(fun):
    @wraps(fun)
    def wrap(request, *args, **kwargs):
        print("Line 49>>>", request.headers)
        print("Line 50", request, *args, **kwargs)

        token = request.headers.get('Authorization')
        
        if not token:
            return JsonResponse({"message": "Token is missing!"}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = decoded_token.get("user_id")
            
            # Fetch the user using the user_id from the token
            request.user_id = user_id
            
            return fun(request, *args, **kwargs)
        
        except jwt.ExpiredSignatureError:
            return JsonResponse({"message": "Token is expired"}, status=status.HTTP_498_INVALID_TOKEN)
        except jwt.InvalidTokenError:
            return JsonResponse({"message": "Invalid token"}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            return JsonResponse({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    return wrap
        
        # except jwt.InvalidTokenError:
        #  return None