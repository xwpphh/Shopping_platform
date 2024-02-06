from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from users.models import User
from rest_framework import serializers

"""
自定义用户登录的认证类 实现多字段登录
"""


class MyBackend(ModelBackend):
    """
    自定义认证登录
    """

    def authenticate(self, request, password=None, username=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(mobile=username) | Q(email=username))
        except:
            raise serializers.ValidationError({'error': "未找到该用户"})
        else:
            # check
            if user.check_password(password):
                return user
            else:
                raise serializers.ValidationError({'error': "密码不正确"})
