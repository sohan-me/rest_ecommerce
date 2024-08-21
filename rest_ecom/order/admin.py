from django.contrib import admin
from .models import Order, OrderProduct, Payment
# Register your models here.


@admin.register(Payment)
class PaymentAdminView(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount_paid', 'status']


@admin.register(Order)
class OrderAdminView(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'is_paid', 'status']
    list_editable = ['is_paid']


@admin.register(OrderProduct)
class OrderProductAdminView(admin.ModelAdmin):
    list_display = ['product_line', 'quantity']
