from django.urls import path
from . import views

"""购物车模块的路由配置"""
urlpatterns = [
    path('goods/', views.CartView.as_view({
        'post': 'create',
        'get': 'list',
    })),
    # 修改购物车中选中状态
    path('goods/<int:pk>/checked/', views.CartView.as_view({
        'put': 'update_goods_status',
    })),
    # 修改购物车商品数量
    path('goods/<int:pk>/number/', views.CartView.as_view({
        'put': 'update_goods_number',
    })),
]
