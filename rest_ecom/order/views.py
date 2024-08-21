from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
import stripe
from django.conf import settings
from rest_framework import viewsets, status
from cart.models import Cart, CartItem
from rest_framework.permissions import IsAuthenticated
from cart.utils import _cart_id
from decimal import Decimal
from .utils import generate_order_number
from .serializers import CheckoutSerializer, OrderItemSerializer, PaymentSerializer
from.models import OrderProduct, Order, Payment

# Create your views here.

class CheckOutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CheckoutSerializer

    @extend_schema(
        description = 'order related details and create order',
        request=CheckoutSerializer,
        responses = {
            200:CheckoutSerializer
        }
    )
    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        
        if not cart_items.exists():
            return Response({'errors':'Your cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        subtotal = sum(item.product_line.price * item.quantity for item in cart_items)
        tax_rate = Decimal(0.10)
        tax_amount = subtotal * tax_rate
        grand_total = subtotal + tax_amount
        
        items = []
        for cart_item in cart_items:
            items.append(
                {
                    'product_line':cart_item.product_line.id,
                    'quantity':cart_item.quantity,
                    'product_price':cart_item.product_line.price,
                }
            )
        
        order_data = {
            'name': request.data.get('name'),
            'phone': request.data.get('phone'),
            'email': request.data.get('email'),
            'address_line': request.data.get('address_line'),
            'landmark': request.data.get('landmark', ''),
            'country': request.data.get('country'),
            'state': request.data.get('state'),
            'city': request.data.get('city'),
            'order_note': request.data.get('order_note', ''),
        }
        
        serializer = CheckoutSerializer(data=order_data, context={'request':request})
        if serializer.is_valid():
            order_number = generate_order_number()
            order = serializer.save(order_number=order_number, tax=tax_amount, order_total=grand_total)
            order.save()
            
            for cart_item in cart_items:
                OrderProduct.objects.create(
                    order=order,
                    product_line=cart_item.product_line,
                    quantity=cart_item.quantity,
                    product_price=cart_item.product_line.price
                )

            
            cart_items.delete()
            
            return Response({'messages': 'Checkout successfully', 'order_number':order_number, 'order_total':grand_total}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class PaymentView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    
    @extend_schema(
        description = 'order related details and create a order',
        request=PaymentSerializer,
        responses = {
            200:PaymentSerializer
        }
    )
    def post(self, request): 
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            payment_method_id = serializer.data.get('payment_method_id')
            order_number = serializer.data.get('order_number')
            
            try:
                order = Order.objects.get(order_number=order_number, user=request.user)
            except Order.DoesNotExist:
                return Response({'errors':'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
            
            try:
                payment_intent = stripe.PaymentIntent.create(
                    amount = int(order.order_total * 100 ), # Stripe expects the amount in cents
                    currency='usd',
                    confirmation_method = 'manual',
                    confirm = True,
                    payment_method=payment_method_id,
                    return_url='http://127.0.0.1:8000/api'
                )   
                
            except stripe.error.StripeError as e:
                return Response({'errors':str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            
            if payment_intent['status'] == 'succeeded':
                payment = Payment.objects.create(
                    user = request.user,
                    payment_id = payment_intent['id'],
                    payment_method = payment_intent['payment_method'],
                    amount_paid = order.order_total,
                    status = payment_intent['status'],
                )

                order.is_paid = True
                order.status = 'Accepted'
                order.payment = payment
                order.save()
                
                return Response({'messages':'Payment successfull', 'order_id':order.order_number}, status=status.HTTP_200_OK)
            
            else:
                return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)
       
        return Response({'errors':'Payment failed'}, status=status.HTTP_400_BAD_REQUEST)
    
     