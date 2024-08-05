from django.urls import path
from . views import register,user_login,user_logout,RefreshTokenView

urlpatterns = [
    path('register/',register,name='register'),
    path('login/', user_login, name='login'),
     path('logout/', user_logout, name='logout'),
     path('api/token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),

    
]