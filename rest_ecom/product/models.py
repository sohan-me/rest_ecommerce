from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

# Create your models here.
class Brand(models.Model):
    
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
class Category(MPTTModel):
    
    name = models.CharField(max_length=100, unique=True)
    parent = TreeForeignKey('self', on_delete=models.PROTECT, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class MPTTMeta:
        order_insertion_by = ['name']
    
    class Meta:
        verbose_name_plural = 'Categories'
        
    def __str__(self):
        return self.name
    
class Product(models.Model):
    
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    is_digital = models.BooleanField(default=False)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = TreeForeignKey(Category, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    
class ProductLine(models.Model):
    
    price = models.DecimalField(decimal_places=2, max_digits=6)
    stock = models.IntegerField()
    sku = models.CharField(max_length=50)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    order_by = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.product} - {self.sku}' 
    
    def save(self, *args, **kwargs):
        if self.order_by:
            ProductLine.objects.filter(product=self.product).exclude(pk=self.id).update(order_by=False)
        super().save(*args, **kwargs)
    
    
class ProductLineImage(models.Model):
    
    name = models.CharField(max_length=100)
    alter_text = models.CharField(max_length=100)
    image_url = models.ImageField(upload_to='product_images/')
    productline = models.ForeignKey(ProductLine, on_delete=models.CASCADE, related_name='productline_image')
    order_by = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if self.order_by:
            ProductLineImage.objects.filter(productline=self.productline).exclude(pk=self.id).update(order_by=False)
        super().save(*args, **kwargs)