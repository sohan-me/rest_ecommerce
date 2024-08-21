from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from nested_admin import NestedModelAdmin, NestedTabularInline
from .models import *
# Register your models here.

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at',)
    
    
@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ('id', 'name', 'parent', 'description', 'created_at',)
    
class ProductLineImageAdmin(NestedTabularInline):
    model = ProductLineImage
    extra = 1
      
class ProductInLineAdmin(NestedTabularInline):
    model = ProductLine
    inlines = [ProductLineImageAdmin]
    extra = 0

@admin.register(Product)
class ProductAdmin(NestedModelAdmin):
    list_display = ('id', 'name', 'brand', 'category', 'is_digital', 'created_at',)
    list_editable = ('is_digital',)
    list_filter = ('brand', 'category',)
    inlines = [ProductInLineAdmin]
