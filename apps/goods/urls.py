# -*- coding:utf-8 -*-
__author__ = 'Saber'
__date__ = '28/8/18 上午10:06'


from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from .views_base import Goodslist, display_meta
from .views import GoodsListView, GoodsListViewSet, CategoryViewSet

router = DefaultRouter()

router.register(r'goods_list', GoodsListViewSet, base_name="goods")

router.register(r'categorys', CategoryViewSet, base_name="categorys")

urlpatterns = [
    url(r'^', include(router.urls)),
    # 请求数据
    url(r'^data/$', Goodslist.as_view(), name="data"),
    # 商品列表页
    url(r'^goods/$', GoodsListView.as_view(), name="goods-list"),

    url(r'^meta/$', display_meta),
]