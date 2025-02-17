from django.shortcuts import render, get_object_or_404
from .models import Table, MenuItem, Order
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render, redirect


stripe.api_key = settings.STRIPE_SECRET_KEY


def table_order(request, table_id):
    return render(request, 'orders/table_order.html', {'table_id': table_id})


# 支付订单的视图函数
def pay_order(request, order_id):
    return HttpResponse(f"Processing payment for order {order_id}")


# 提交订单的视图函数
def submit_order(request):
    if request.method == "POST":
        table_id = request.POST.get("table_id")
        menu_item_id = request.POST.get("menu_item_id")

        # 在这里可以存储订单（如果有订单模型）
        # 这里只是示例，重定向到菜单页面
        return redirect(f"/order/menu/{table_id}/")


def create_checkout_session(request):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': '餐厅订单',
                },
                'unit_amount': 5000,  # 价格（分），$50.00
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url="http://127.0.0.1:8000/success/",
        cancel_url="http://127.0.0.1:8000/cancel/",
    )
    return redirect(session.url, code=303)


def menu(request, table_id):
    menu_items = MenuItem.objects.all()  # 查询所有菜单项
    return render(request, 'orders/menu.html', {'menu_items': menu_items, 'table_id': table_id})


def home(request):
    table_id = 1  # 或从数据库中获取动态的 table_id
    return render(request, 'orders/home.html')


def checkout(request):
    return render(request, 'orders/checkout.html')


def success(request):
    return render(request, 'orders/success.html')


def cancel(request):
    return render(request, 'orders/cancel.html')
