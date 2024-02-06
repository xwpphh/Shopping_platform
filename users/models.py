from django.db import models
# django自带的用户认证模型
from django.contrib.auth.models import AbstractUser
from rest_framework.throttling import AnonRateThrottle

# 公共模型字段
from common.db import BaseModel


class User(AbstractUser, BaseModel):
    # 用户表
    mobile = models.CharField(verbose_name='手机号', default='', max_length=11)
    avatar = models.ImageField(verbose_name='用户头像', blank=True, null=True)

    class Meta:
        db_table = "users"
        verbose_name = "用户表"
        verbose_name_plural = verbose_name


class Addr(models.Model):
    """
    收货地址模型
    """
    user = models.ForeignKey('User', verbose_name='所属用户', on_delete=models.CASCADE)
    phone = models.CharField(verbose_name='手机号码', max_length=11)
    name = models.CharField(verbose_name='联系人', max_length=20)
    province = models.CharField(verbose_name='省份', max_length=20)
    city = models.CharField(verbose_name='城市', max_length=20)
    country = models.CharField(verbose_name='区县', max_length=20)
    address = models.CharField(verbose_name='详细地址', max_length=200)
    is_default = models.BooleanField(verbose_name='是否为默认地址', default=False)

    class Meta:
        db_table = 'addr'
        verbose_name = '收获地址表'
        verbose_name_plural = verbose_name


class Area(models.Model):
    """
    省市区
    国家0
    省份1
    市2
    区县4
    """
    pid = models.IntegerField(verbose_name='上级id')
    name = models.CharField(verbose_name='地区名', max_length=20)
    level = models.CharField(verbose_name='区域等级', max_length=20)

    class Meta:
        db_table = 'area'
        verbose_name = '地区表'
        verbose_name_plural = verbose_name


class VerifCode(models.Model):
    """验证码模型"""
    mobile = models.CharField(verbose_name="手机号", max_length=11)
    code = models.CharField(max_length=6, verbose_name='验证码')
    creat_time = models.DateTimeField(auto_now_add=True, verbose_name='生成时间')

    class Meta:
        db_table = 'VerifCode'
        verbose_name = '验证码表'
        verbose_name_plural = verbose_name
