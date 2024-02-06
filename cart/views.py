from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework import mixins, status

from cart.models import Cart
from cart.permissions import CartPermission
from cart.serializers import CartSerializer, ReadCartSerializer


# Create your views here.

class CartView(GenericViewSet,
               mixins.UpdateModelMixin,
               mixins.CreateModelMixin,
               mixins.DestroyModelMixin,
               mixins.ListModelMixin,
               ):
    """添加商品"""
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    # 设置认证用户才有权限访问
    permission_classes = [IsAuthenticated, CartPermission]

    def get_serializer_class(self):
        if self.action == 'list':
            return ReadCartSerializer
        else:
            return self.serializer_class

    def create(self, request, *args, **kwargs):
        # 获取用户信息
        user = request.user
        # 获取参数
        goods = request.data.get('goods')
        # 校验参数
        # 1. 校验该用户的购物车中是否有该商品
        if Cart.objects.filter(user=user, goods=goods).exists():
            # 该用户添加过该商品到购物车 直接修改商品数量即可 无需重复添加该商品
            cart_goods = Cart.objects.get(user=user, goods=goods)
            cart_goods.number += 1
            cart_goods.save()
            # 对该商品进行序列化
            serializer = self.get_serializer(cart_goods)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # 没有添加过 则调用父类继承的create方法创建 记得验证id 可能无效
            request.data['user'] = user.id
            return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """获取用户购物车的所有商品"""
        query = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(query, many=True)
        return Response(serializer.data)

    def update_goods_status(self, request, *args, **kwargs):
        """
        修改商品的选中状态
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        obj = self.get_object()
        obj.is_checked = not obj.is_checked
        obj.save()
        return Response({"message": "修改成功"}, status=status.HTTP_200_OK)

    def update_goods_number(self, request, *args, **kwargs):
        """
        修改商品数量
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        number = request.data.get('number')
        obj = self.get_object()
        # 校验参数
        if not isinstance(number, int):
            return Response({'error': "填写的数量有误"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 修改商品的数量
        if number <= 0:
            # 删除该商品
            obj.delete()
            return Response({'message': "操作成功，已从购物车中移除"}, status=status.HTTP_200_OK)
        # 判断商品数量是否超过库存
        elif number > (obj.goods.stock - obj.goods.sales):
            return Response({'message': "库存不够啦~"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        else:
            # 修改
            obj.number = number
            obj.save()
            return Response({'message': "操作成功"}, status=status.HTTP_200_OK)
