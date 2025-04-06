import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone


class Table(models.Model):
    number = models.IntegerField(unique=True)  # 餐桌编号
    qr_code = models.ImageField(upload_to="qrcodes/", blank=True)  # 存储二维码图片


class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="menu_image/", blank=True, null=True)  # 修改为 ImageField


class Order(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Preparing", "Preparing"),
        ("Completed", "Completed"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    table = models.ForeignKey('Table', on_delete=models.CASCADE)
    items = models.ManyToManyField(MenuItem, through='OrderItems')
    created_at = models.DateTimeField(default=timezone.now, blank=True)

    def calculate_total_price(self):
        return sum(item.menuitem.price * item.quantity for item in self.order_items.all())


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    stripe_payment_id = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[("Pending", "Pending"), ("Paid", "Paid")])


class OrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="menu_orders")
    quantity = models.IntegerField(default=1)  # 添加 quantity 字段，确保记录菜品数量

    class Meta:
        unique_together = (('order', 'menuitem'),)

