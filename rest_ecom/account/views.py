from rest_framework.views import APIView
from .models import CustomUser, UserProfile
from drf_spectacular.utils import extend_schema
from .serializers import CustomUserSerializer, UserProfileSerializer, RegisterSerializer, LoginSerializer, ChangePasswordSerializer, SendPasswordResetSerializer, UserPasswordResetSerializer
from rest_framework.response import Response
from django.contrib import auth
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from cart.utils import _cart_id
from cart.models import Cart, CartItem
from rest_framework.decorators import action
from order.models import Order
from order.serializers import OrderSerializer
# Create your views here.


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    

class RegisterUser(APIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    @extend_schema(
        description="Register a user.",
        request=RegisterSerializer
    )
    def post(self, request, format=None):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response({'token':token, 'message':'Registration success'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
    
    

class Login(APIView):
    
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    def get_cart(self, request):
        cart_id = _cart_id(request)
        cart, _ = Cart.objects.get_or_create(cart_id=cart_id)
    
        return cart
    
    @extend_schema(
        description="User login area",
        request=LoginSerializer
    )
    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        
        if request.user.is_authenticated:
            return Response({'warning':'You are already logged in.'}, status=status.HTTP_200_OK)
        
        if serializer.is_valid():
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            user = auth.authenticate(email=email, password=password)
            if user is not None:
                user_cart = Cart.objects.filter(user=user).exists()
                if not user_cart:    
                    session_cart = self.get_cart(request)
                    session_cart.user = user
                    session_cart.save()
                else:
                    user_cart = Cart.objects.get(user=user)
                    session_cart = self.get_cart(request)
                    if session_cart.cartitem_set.exists():
                        for session_item in session_cart.cartitem_set.all():
                            user_cart_item = CartItem.objects.filter(cart=user_cart, product_line=session_item.product_line)
                            if not user_cart_item.exists():
                                session_item.cart = user_cart
                                session_item.save()
                            else:
                                user_cart_item = CartItem.objects.get(cart=user_cart, product_line=session_item.product_line)
                                user_cart_item.quantity += session_item.quantity
                                user_cart_item.save()
                                session_item.delete()

    
                    session_cart.delete()
                            
                    
                    
                token = get_tokens_for_user(user)
                user_serializer = CustomUserSerializer(user)
                return Response({'token':token, 'user':user_serializer.data, 'message':'Login Success'}, status=status.HTTP_200_OK)
            else:
                return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class ChangePassword(APIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            current_password = serializer.validated_data.get('current_password')
            password = serializer.validated_data.get('password')

            if not user.check_password(current_password):
                return Response({'errors': 'Current password does not match'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(password)
            user.save()
            return Response({'messages': 'Password updated successfully'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class SendResetPassword(APIView):
    
    serializer_class = SendPasswordResetSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'messages':'A password reset email has been send to you email.'})
    
    
class UserPasswordReset(APIView):
    serializer_class = UserPasswordResetSerializer
    permission_classes = [AllowAny]
    def post(self, request, uid, token, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'uid': uid, 'token': token})
        serializer.is_valid(raise_exception=True)
        return Response({'messages': 'Password reset successfully.'}, status=status.HTTP_200_OK)
    
    
    
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer

    @extend_schema(
        responses={
            200: CustomUserSerializer,
        },
        request=CustomUserSerializer,
        description='Retrieve user profile and orders or update profile information'
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        user_serializer = CustomUserSerializer(user)
        orders = Order.objects.filter(user=user)
        order_serializer = OrderSerializer(orders, many=True)
    
        response_data = {
            'profile': user_serializer.data,
            'orders': order_serializer.data
        }      
        return Response(response_data, status=status.HTTP_200_OK)
    


    @action(detail=False, methods=['post'], url_path=r'update/')
    @extend_schema(
        request=CustomUserSerializer,
        responses={
            200: CustomUserSerializer,
            400: 'Invalid request',
        },
        description='Update user profile information'
    )
    def patch(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    