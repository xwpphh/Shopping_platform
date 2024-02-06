from django.shortcuts import render
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet

from goods.models import GoodsGroup, GoodsBanner, Goods, Collect, Detail
from goods.permissions import CollectPermission
from goods.serializers import GoodsSerializer, GoodsGroupSerializer, GoodsBannerSerializer, CollectSerializer, \
    DetailSerializer


# Create your views here.

class IndexView(APIView):
    def get(self, request):
        """商城首页"""
        # 序列化的时候如果有图片字段，返回数据需要补全完整的图片获取域名，需要在序列化器时传入请求对象。
        # 1.获取商品所有分类信息
        group = GoodsGroup.objects.filter(status=True)
        group_ser = GoodsGroupSerializer(group, many=True, context={'request': request})
        # 2. 获取商品的海报
        banner = GoodsBanner.objects.filter(status=True)
        banner_ser = GoodsBannerSerializer(banner, many=True, context={'request': request})
        # 3. 获取所有的推荐商品
        goods = Goods.objects.filter(recommend=True)
        goods_ser = GoodsSerializer(goods, many=True, context={'request': request})

        result = dict(
            group=group_ser.data,
            banner=banner_ser.data,
            goods=goods_ser.data
        )
        return Response(result)


class GoodsView(ReadOnlyModelViewSet):
    """
    商品视图集
    查询商品列表
    查询单个商品
    根据要求对商品进行排序
    """
    queryset = Goods.objects.filter(is_on=True)
    serializer_class = GoodsSerializer
    # 实现通过商品分类和是否推荐
    filterset_fields = ('group', 'recommend')
    # 通过价格和销量和上架时间进行排序
    ordering_fields = ('sales', 'price', 'id')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        # 获取商品详情
        detail = Detail.objects.get(goods=instance)
        detail_ser = DetailSerializer(detail)
        result = serializer.data
        result['detail'] = detail_ser.data
        return Response(result)


class CollectView(mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
    """
    收藏商品视图集
    post收藏商品
    delete取消收藏
    list收藏列表
    """

    queryset = Collect.objects.all()
    serializer_class = CollectSerializer
    # 设置认证用户才有权限访问
    permission_classes = [IsAuthenticated, CollectPermission]

    def create(self, request, *args, **kwargs):
        # 收藏商品
        # 获取请求参数
        user = request.user
        params_user_id = request.data.get('user')

        # 校验请求参数中的用户id是否为当前登录的用户
        if user.id != params_user_id:
            return Response({'error': "没有操作其他用户的权限"})
        # 校验通过 直接调用继承过来的方法进行创建
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(user=request.user)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class GoodsGroupView(mixins.ListModelMixin,
                     GenericViewSet):
    """商品分类序列化器"""
    queryset = GoodsGroup.objects.filter(status=True)
    serializer_class = GoodsGroupSerializer

