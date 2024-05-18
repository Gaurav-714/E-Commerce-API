from django.db import models
from django.contrib.auth.models import User
from product.models import Product

class OrderStatus(models.TextChoices):
    PROCESSING = 'Processing'
    SHIPPED = 'Shipped'
    DELIVERD = 'Deliverd'


class PaymentStatus(models.TextChoices):
    PAID = 'Paid'
    UNPAID = 'Unpaid'


class PaymentMode(models.TextChoices):
    COD = 'COD'
    CARD = 'CARD'


class Order(models.Model):

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    total_amount = models.IntegerField(default=0)

    area = models.CharField(max_length=500, default='', blank=False)
    city = models.CharField(max_length=100, default='', blank=False)
    state = models.CharField(max_length=100, default='', blank=False)
    country = models.CharField(max_length=100, default='', blank=False)

    zip_code = models.CharField(max_length=100, default='', blank=False)
    phone_no = models.CharField(max_length=100, default='', blank=False)    

    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
    payment_mode = models.CharField(max_length=20, choices=PaymentMode.choices, default=PaymentMode.COD)
    order_status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PROCESSING)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
        
    def __str__(self):
        return self.id
    

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderitems')
    name = models.CharField(max_length=200, default='', blank=False)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=False)

    def __str__(self):
        return self.name