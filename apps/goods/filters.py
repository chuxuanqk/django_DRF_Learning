# -*- coding:utf-8 -*-
__author__ = 'Saber'
__date__ = '30/8/18 下午5:20'


import django_filters

from .models import Goods


class GoodsFilter(django_filters.rest_framework.FilterSet):
    """
    商品过滤的类
    """
    # 两个参数，name是要过滤的字段， lookup是执行的行为，
    price_min = django_filters.NumberFilter(field_name="shop_price", lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name="shop_price", lookup_expr='lte')

    class Meta:
        model = Goods
        fields = ['price_min', 'price_max']
