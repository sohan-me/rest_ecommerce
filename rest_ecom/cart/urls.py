from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartItemView, CartView


router = DefaultRouter()

router.register(r'cart', CartView, basename='cart')
router.register(r'cart-item', CartItemView, basename='cart_item')




urlpatterns = [
    path('', include(router.urls)),

       
]