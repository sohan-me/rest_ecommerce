from rest_framework import serializers
from .models import Order, OrderProduct




class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ['product_line', 'quantity', 'product_price']

class CheckoutSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Order
        fields = [
            'name', 'phone', 'email', 'address_line', 'landmark', 'country', 
            'state', 'city', 'order_note', 'order_total', 'tax'
        ]
        read_only_fields = ['order_total', 'tax']

    def create(self, validated_data):
        user = self.context['request'].user
        order = Order.objects.create(user=user, **validated_data)  
        return order
    
class PaymentSerializer(serializers.Serializer):
    payment_method_id = serializers.CharField(max_length=255)
    order_number= serializers.CharField(max_length=255)
    

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        exclude = ['created_at', 'updated_at']
    