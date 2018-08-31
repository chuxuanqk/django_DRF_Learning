# -*- coding:utf-8 -*-
__author__ = 'Saber'
__date__ = '19/8/18 下午6:31'


from rest_framework import serializers

from goods.models import Goods, GoodsCategory


# Serializer实现商品列表页
# class GoodsSerializer(serializers.Serializer):
#     name = serializers.CharField(required=True,max_length=100)
#     click_num = serializers.IntegerField(default=0)
#     goods_front_image = serializers.ImageField()


class CategorySerializer3(serializers.ModelSerializer):
    """
    三级分类
    """
    class Meta:
        model = GoodsCategory
        fields = "__all__"


class CategorySerializer2(serializers.ModelSerializer):
    """
    二级分类
    """
    # 在parent_category字段中定义的related_name="sub_cat"
    sub_cat = CategorySerializer3(many=True)

    class Meta:
        model = GoodsCategory
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    """
    一级分类
    """
    sub_cat = CategorySerializer2(many=True)

    class Meta:
        model = GoodsCategory
        fields = "__all__"


# ModelSerializer实现商品列表页
class GoodsSerializer(serializers.ModelSerializer):
    # 外键的序列化,覆盖外键字段
    category = CategorySerializer(many=True)

    class Meta:
        model = Goods
        fields = "__all__"

