from django.shortcuts import render, get_object_or_404
from .models import Table, MenuItem, Order, OrderItems
import stripe
import json
from django.conf import settings
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Order


stripe.api_key = settings.STRIPE_SECRET_KEY


def table_order(request, table_id):
    return render(request, 'orders/table_order.html', {'table_id': table_id})


# 支付订单的视图函数
def pay_order(request, order_id):
    return HttpResponse(f"Processing payment for order {order_id}")


# 提交订单的视图函数
def submit_order(request):
    if request.method == "POST":
        data = json.loads(request.body)  # 获取前端传来的数据
        table_id = data.get("table_id")  # 餐桌 ID
        order_items = data.get("order_items")  # 菜品列表，格式：[{menu_item_id: 1, quantity: 2}, ...]

        if not table_id or not order_items:
            return JsonResponse({"error": "Missing data"}, status=400)

        table = get_object_or_404(Table, id=table_id)

        # 计算订单总价
        total_price = 0
        order = Order.objects.create(table=table, total_price=0, status="Pending")  # 先创建订单，稍后更新价格

        for item in order_items:
            menu_item = get_object_or_404(MenuItem, id=item["menu_item_id"])
            quantity = item["quantity"]
            OrderItems.objects.create(order=order, menuitem=menu_item, quantity=quantity)
            total_price += menu_item.price * quantity

        # 更新订单总价
        order.total_price = total_price
        order.save()

        return JsonResponse({"message": "Order submitted successfully", "order_id": order.id})


def create_checkout_session(request):
    import json
    order_id = request.GET.get('order_id')  # 获取订单 ID

    order = get_object_or_404(Order, id=order_id)  # 确保订单存在

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'cny',
                'product_data': {'name': '餐厅订单'},
                'unit_amount': int(order.total_price * 100),  # 确保价格正确
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


def checkout(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItems.objects.filter(order=order)

    total_price = sum(item.menuitem.price * item.quantity for item in order_items)

    return render(request, "orders/checkout.html", {
        "order": order,
        "order_items": order_items,
        "total_price": total_price,
    })


def success(request):
    return render(request, 'orders/success.html')


def cancel(request):
    return render(request, 'orders/cancel.html')


def update_order(request):
    if request.method == "POST":
        data = json.loads(request.body)  # 获取前端传来的数据
        table_id = data.get("table_id")  # 餐桌 ID
        order_items = data.get("order_items")  # 菜品列表，格式：[{menu_item_id: 1, quantity: 2}, ...]

        if not table_id or not order_items:
            return JsonResponse({"error": "Missing data"}, status=400)

        table = Table.objects.get(id=table_id)  # 获取餐桌

        # 尝试获取已存在的订单，如果没有则创建
        order, created = Order.objects.get_or_create(table=table, status="Pending")

        # 计算总价
        total_price = 0
        for item in order_items:
            menu_item = MenuItem.objects.get(id=item["menu_item_id"])
            quantity = item["quantity"]
            # 创建或更新 OrderItems
            OrderItems.objects.create(order=order, menuitem=menu_item, quantity=quantity)
            total_price += menu_item.price * quantity

        # 更新订单总价
        order.total_price = total_price
        order.save()

        return JsonResponse({"message": "Order updated successfully", "order_id": order.id})


def add_to_cart(request, table_id, menu_item_id):
    if request.method == "POST":
        table = get_object_or_404(Table, id=table_id)
        # 查找当前桌子的“待支付”订单，若无则创建新订单
        order, created = Order.objects.get_or_create(table=table, status="Pending")

        menu_item = get_object_or_404(MenuItem, id=menu_item_id)
        order_item, created = OrderItems.objects.get_or_create(order=order, menuitem=menu_item)
        order_item.quantity += 1  # 增加数量
        order_item.save()

        return JsonResponse({
            "message": "菜品已加入购物车",
            "order_id": order.id,  # 确保返回 order_id
            "menu_item": menu_item.name,
            "quantity": order_item.quantity,
        })
    else:
        return JsonResponse({"error": "只支持 POST 请求"}, status=400)


def menu_view(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    menu_items = MenuItem.objects.all()

    # 获取当前桌子未支付订单（如果有）
    order = Order.objects.filter(table=table, status="Pending").first()

    return render(request, "menu.html", {
        "table_id": table.id,
        "menu_items": menu_items,
        "order": order  # 传递订单给模板
    })