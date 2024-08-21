from rest_framework import serializers
from product.serializers import ProductLineSerializer
from .models import Cart, CartItem


class CartItemSerializer(serializers.Serializer):
    product_line_id = serializers.CharField(max_length=200)
    quantity = serializers.CharField(max_length=200)
    
    class Meta:
        model = CartItem
        fields = ['quantity', 'product_line_id']


class CartSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Cart
        fields = ['cart_id', 'user', 'created_at']
        
        
