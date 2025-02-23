from django.urls import path
from . import views  # 导入 views 文件中的视图函数
from .views import update_order

urlpatterns = [
    path('order/<int:table_id>/', views.table_order, name='table_order'),  # 订单页面，显示指定桌号的订单信息
    path('pay_order/<int:order_id>/', views.pay_order, name='pay_order'),  # 支付订单，处理订单支付
    path('submit_order/', views.submit_order, name='submit_order'),  # 提交订单，提交餐厅订单
    path('update_order/', update_order, name='update_order'),
    path('menu/<int:table_id>/', views.menu, name='menu'),
    path("checkout/<int:order_id>/", views.checkout, name="checkout"),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.success, name='success'),
    path('add_to_cart/<int:table_id>/<int:menu_item_id>/', views.add_to_cart, name="add_to_cart"),
    path('cancel/', views.cancel, name='cancel'),
    path("kitchen/", views.kitchen_orders, name="kitchen_orders"),
    path("api/orders/", views.get_orders, name="get_orders"),

    path('', views.home, name='home')
]
