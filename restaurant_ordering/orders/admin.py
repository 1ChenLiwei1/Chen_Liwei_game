from django.contrib import admin
from .models import Table, MenuItem, Order, Payment

admin.site.register(Table)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(Payment)

