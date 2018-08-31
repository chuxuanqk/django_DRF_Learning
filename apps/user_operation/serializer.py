# -*- coding:utf-8 -*-
__author__ = 'Saber'
__date__ = '31/8/18 上午12:24'

from rest_framework import serializers

from .models import UserFav, UserLeavingMessage
from goods.serializers import GoodsSerializer


class UserFavDetailSerializer(serializers.ModelSerializer):
    """
    用户收藏详情
    """

    # 通过商品id获取收藏的商品，需要嵌套商品的序列化
    goods = GoodsSerializer()

    class Meta:
        model = UserFav
        fields = ("goods", "id")


class LeavingMessageSerializer(serializers.ModelSerializer):
    """
    用户留言
    """
    # 获取当前登录的用户
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    # read_only:只返回，post时候可以不用提交，format：格式化输出
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')

    class Meta:
        model = UserLeavingMessage
        fields = ("user", "message_type", "subject", "message", "file", "id", "add_time")