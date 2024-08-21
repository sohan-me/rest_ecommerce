from rest_framework.routers import DefaultRouter
from .views import CheckOutView, PaymentView
from django.urls import path

router = DefaultRouter()

urlpatterns = [
    path('checkout/', CheckOutView.as_view(), name='checkout'),
    path('payment/', PaymentView.as_view(), name='payment'),
    
]