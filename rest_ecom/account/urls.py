from django.urls import path, include
from .views import RegisterUser, Login, UserProfileView, ChangePassword, SendResetPassword, UserPasswordReset


urlpatterns = [
    
    path('user/profile/', UserProfileView.as_view(), name='user_profile'),
    path('user/register/', RegisterUser.as_view(), name="register"),
    path('user/login/', Login.as_view(), name='login'),
    path('user/change_password', ChangePassword.as_view(), name='change_password'),
    path('user/send-reset-password/', SendResetPassword.as_view(), name='send_reset_password'),
    path('user/reset-password/<str:uid>/<str:token>/', UserPasswordReset.as_view(), name='reset_password'),
     
]