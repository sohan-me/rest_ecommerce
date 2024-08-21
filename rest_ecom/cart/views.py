from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Cart, CartItem
from product.models import ProductLine
from .utils import _cart_id
from .serializers import CartSerializer, CartItemSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from decimal import Decimal

# Create your views here.
class CartItemView(viewsets.ViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [AllowAny]
    
    def get_cart(self, request):
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
        else:
            cart_id = _cart_id(request)
            cart, _ = Cart.objects.get_or_create(cart_id=cart_id)
        
        return cart

        
        
    @action(detail=False, methods=['post'])
    @extend_schema(
        description ='Add a new item or increase the quantity',
        request=CartItemSerializer,
        responses={
            200:CartItemSerializer,
        }
    )
    def add(self, request):
        cart = self.get_cart(request)
        product_line_id = request.data.get('product_line_id')
        quantity = request.data.get('quantity', 1)

        try:
            product_line = ProductLine.objects.get(id=product_line_id)
        except ProductLine.DoesNotExist:
            return Response({'errors':'product line not found !'}, status=status.HTTP_404_NOT_FOUND)
        
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product_line=product_line, defaults={'quantity':quantity})

        if not created:
            cart_item.quantity += int(quantity)
            cart_item.save()
            return Response({'messages':f'{product_line.product.name} quantity updated.'}, status=status.HTTP_200_OK)     
            
        return Response({'messages':f'{product_line.product.name} has been added to cart'}, status=status.HTTP_201_CREATED)        
    
    
    @action(detail=False, methods=['patch'])
    @extend_schema(
        description ='Decrease the quantity',
        request=CartItemSerializer,
        responses={
            200:CartItemSerializer
        }
    )
    def decrease(self, request):
        cart = self.get_cart(request)
        product_line_id = request.data.get('product_line_id')
        quantity = int(request.data.get('quantity', 1))
        
        try:
            product_line = ProductLine.objects.get(id=product_line_id)
            cart_item = CartItem.objects.get(cart=cart, product_line=product_line)
        except (ProductLine.DoesNotExist, CartItem.DoesNotExist):
            return Response({'errors':'product line or cart item not found.'})
        
        if cart_item.quantity > quantity:
            cart_item.quantity -= quantity
            cart_item.save()
            return Response({'messages':f'{product_line.product.name} quantity udpated'}, status=status.HTTP_200_OK)
        else:
            cart_item.delete()
            return Response({'messages':f'Cart item {product_line.product.name} has been removed'}, status=status.HTTP_200_OK)
        
        
        
    @action(detail=False, methods=['delete'],  url_path=r'(?P<product_line_id>\d+)')
    @extend_schema(
        description='Remove an item from the cart using the product line ID from the URL path.',
        responses={
            200: 'Item successfully removed from cart',
            404: 'Product line or cart item not found'
        }
    )
    def remove(self, request, product_line_id=None):
        cart = self.get_cart(request)

        try:
            product_line = ProductLine.objects.get(id=product_line_id)
            cart_item = CartItem.objects.get(cart=cart, product_line=product_line)
            cart_item.delete()
            return Response({'message': f'{cart_item.product_line.product.name} has been removed from cart.'}, status=status.HTTP_200_OK)
        except (ProductLine.DoesNotExist, CartItem.DoesNotExist):
            return Response({'errors': 'Product line or cart item not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
        
class CartView(viewsets.ViewSet):
    serializer_class = CartSerializer
    permission_classes = [AllowAny]
    
    def get_cart(self, request):
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            print('User Cart Found')
        else:
            print('Not Found user cart')
            cart_id = _cart_id(request)
            cart, _ = Cart.objects.get_or_create(cart_id=cart_id)
        
        return cart
    
    @extend_schema(
        description='Retrieve all the cart items available in cart',
        request=CartSerializer,
        responses={
            200:CartSerializer
        }
    )
    def list(self, request):
        
        cart = self.get_cart(request)    
        cart_items = CartItem.objects.filter(cart=cart)
        
        subtotal = sum(item.product_line.price * item.quantity for item in cart_items)  
        tax_rate = Decimal(0.10)
        tax_amount = subtotal * tax_rate
        grand_total = subtotal + tax_amount
        serializer = CartItemSerializer(cart_items, many=True)
        
        return Response({
            'cart_items': serializer.data,
            'subtotal': (subtotal),
            'tax_amount': float(tax_amount),
            'grand_total':float(grand_total),
        }, status=status.HTTP_200_OK)
    
    
    
    

    @action(detail=False, methods=['delete'])
    @extend_schema(
        description='Delete Cart',
        responses={
            200: CartSerializer,
            404: 'Cart not found'
        }
    )
    def remove(self, request):
        cart = self.get_cart(request)
        if not cart:
            return Response({'errors': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        
        cart.delete()
        return Response({'message': 'Cart has been removed successfully'}, status=status.HTTP_200_OK)
