from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from .models import *
from .serializers import *
# Create your views here.


class BrandViewSet(viewsets.ViewSet):
   
    serializer_class = BrandSerializer
    queryset = Brand.objects.all()
    
    @extend_schema(
        description="Retrieve a list of all brands",
        responses={200: ProductSerializer(many=True)},
    )
    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ViewSet):
    
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    
    @extend_schema(
        description="Retrieve a list of all categories",
        responses={200: ProductSerializer(many=True)},
        )
    def list(self, request):  
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        return self.queryset
    

class ProductViewSet(viewsets.ViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all().order_by('name')

    @extend_schema(
        description="Retrieve a list of all products",
        responses={200: ProductSerializer(many=True)},
        )
    def list(self, request):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        return self.queryset
    
    @action(detail=False, methods=['get'], url_path=r'categorize-products/(?P<category_id>\d+)')
    @extend_schema(
        description="Filter by category",
        responses={200: ProductSerializer(many=True)},
    )
    def categorize_products(self, request, category_id=None):
        queryset = self.get_queryset().filter(category__id=category_id)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path=r'details/(?P<product_id>\d+)')
    @extend_schema(
        description="Get by product primary key",
        responses={200: ProductSerializer(many=True)},
        )
    def get_product(self, request, product_id=None):
        queryset = self.get_queryset().get(id=product_id)
        serializer = self.serializer_class(queryset, many=False)
        return Response(serializer.data)


