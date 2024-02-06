from rest_framework import serializers

from users.models import User, Addr


class UserSerializer(serializers.ModelSerializer):
    """
    用户模型的序列化器
    """

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'mobile', 'avatar']


class AddrSerializer(serializers.ModelSerializer):
    """
    收货地址模型序列化器哦
    """

    class Meta:
        model = Addr
        fields = '__all__'
