"""
商品序列化器
"""
from .models import Goods, GoodsBanner, GoodsGroup, Detail, Collect
from rest_framework import serializers


class GoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goods
        fields = "__all__"


class GoodsBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsBanner
        fields = "__all__"


class GoodsGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsGroup
        fields = "__all__"


class CollectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collect
        fields = "__all__"


class DetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detail
        fields = ['producer', 'norms', 'details']
