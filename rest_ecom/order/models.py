from django.db import models
from account.models import CustomUser
from cart.models import Cart, CartItem
from product.models import ProductLine
# Create your models here.


class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=255)
    payment_method = models.CharField(max_length=255)
    amount_paid = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.payment_id

class Order(models.Model):
   
   STATUS = {
       'New':'New',
       'Accepted':'Accepted',
       'Completed':'Completed',
       'Cancelled':'Cancelled'
    }
   
   user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
   payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
   order_number = models.CharField(max_length=255, null=True, unique=True)
   name = models.CharField(max_length=255)
   phone = models.CharField(max_length=15)
   email = models.EmailField()
   address_line = models.CharField(max_length=255)
   landmark = models.CharField(max_length=255, null=True, blank=True)
   country = models.CharField(max_length=50)
   state = models.CharField(max_length=50)
   city = models.CharField(max_length=50)
   order_note = models.CharField(max_length=255)
   order_total = models.FloatField()
   tax = models.FloatField()
   status = models.CharField(choices=STATUS, default='New', max_length=255)
   is_paid = models.BooleanField(default=False)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)
   
   def __str__(self):
    return self.order_number



   
class OrderProduct(models.Model):

	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	product_line = models.ForeignKey(ProductLine, on_delete=models.CASCADE)
	quantity = models.IntegerField()
	product_price = models.IntegerField()
	created_at = models.DateTimeField(auto_now_add=True)



	def __str__(self):
		return self.product_line.product.name
   

    