import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models
class Table(models.Model):
    number = models.IntegerField(unique=True)  # 餐桌编号
    qr_code = models.ImageField(upload_to="qrcodes/", blank=True)  # 存储二维码图片

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='images/', null=True, blank=True)

    def __str__(self):
        return self.name
class Order(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    items = models.ManyToManyField(MenuItem)
    total_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=[("Pending", "Pending"), ("Completed", "Completed")])

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    stripe_payment_id = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[("Pending", "Pending"), ("Paid", "Paid")])
