from rest_framework import serializers
from .models import *


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['name', 'description']
        
        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'parent', 'description']
        
class ProductLineImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductLineImage
        fields = ('name', 'alter_text', 'image_url', 'order_by',)
        
        
class ProductLineSerializer(serializers.ModelSerializer):
    productlineimage = ProductLineImageSerializer(many=True, source='productline_image')
    
    class Meta:
        model = ProductLine
        fields = ('price', 'stock', 'sku', 'order_by', 'productlineimage', )        
        
        
class ProductSerializer(serializers.ModelSerializer):
    brand = BrandSerializer()
    category = CategorySerializer()
    productline = ProductLineSerializer(many=True, source='productline_set')
    
    class Meta:
        model = Product
        fields = ['name', 'brand', 'category', 'description', 'is_digital', 'productline',]
        
       
