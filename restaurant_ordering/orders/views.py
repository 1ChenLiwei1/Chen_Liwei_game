from django.shortcuts import render, get_object_or_404
from .models import Table, MenuItem, Order
import stripe
import json
from django.conf import settings
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Order, OrderItem


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
    import json
    order_data = json.loads(request.GET.get('orderData', '{}'))

    total_amount = 0
    for item_id, quantity in order_data.items():
        menu_item = get_object_or_404(MenuItem, id=item_id)
        total_amount += menu_item.price * quantity

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'cny',
                'product_data': {'name': '餐厅订单'},
                'unit_amount': int(total_amount * 100),
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
    table_id = request.GET.get('table_id')  # 或者从 session 读取

    # 获取该桌号的所有订单项
    order_items = OrderItem.objects.filter(order__table_id=table_id)

    # 计算总金额
    total_amount = sum(item.menu_item.price * item.quantity for item in order_items)

    return render(request, 'orders/checkout.html', {
        'order_items': order_items,
        'total_amount': total_amount,
    })


def success(request):
    return render(request, 'orders/success.html')


def cancel(request):
    return render(request, 'orders/cancel.html')


def update_order(request):
    if request.method == "POST":
        data = json.loads(request.body)
        menu_item_id = data.get("menu_item_id")
        quantity = data.get("quantity")

        if menu_item_id is None or quantity is None:
            return JsonResponse({"error": "Invalid data"}, status=400)

        table_id = request.session.get("table_id", 1)  # 假设 table_id 从 session 读取
        order, created = Order.objects.get_or_create(table_id=table_id)

        menu_item = MenuItem.objects.get(id=menu_item_id)
        order_item, created = OrderItem.objects.get_or_create(order=order, menu_item=menu_item)
        order_item.quantity = quantity
        order_item.save()

        return JsonResponse({"message": "Order updated"})