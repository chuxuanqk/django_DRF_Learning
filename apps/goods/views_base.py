# -*- coding:utf-8 -*-
__author__ = 'Saber'
__date__ = '13/8/18 下午10:45'

import json
import pandas as pd
import sqlite3 as sql

from django.views.generic.base import View
from rest_framework.response import Response
from django.db import connection
from django.http import HttpResponse, JsonResponse
from rest_framework.pagination import PageNumberPagination
from rest_framework import mixins, viewsets

from goods.models import Goods
from .serializers import GoodsSerializer


# class GoodsListView(View):
#     def get(self, request):
#         """
#         通过django的view实现商品列表页
#         :param request:
#         :return:
#         """
#         json_list = []
#         goods = Goods.objects.all()[:10]
#         for good in goods:
#             json_dict = {}
#             json_dict["name"] = good.name
#             json_dict["category"] = good.category.name
#             json_dict["market_price"] = good.market_price
#             json_list.append(json_dict)
#
#         # from django.forms.models import model_to_dict
#         # for good in goods:
#         #     json_dict = model_to_dict(good)
#         #     json_list.append(json_dict)
#
#         # 将不同的字段序列化,可以解决图片对象不能json序列化问题
#         from django.core import serializers
#         json_data = serializers.serialize("json", goods)
#         json_data = json.loads(json_data)
#
#         return HttpResponse(json.dumps(json_data), content_type="application/json")
#         # 直接传递一个dict
#         # return JsonResponse(json_data, safe=False)


class Goodslist(View):

    def get(self, request):
        # cur=connection.cursor()
        # cur.execute("")

        sql = "select * from users_userprofile where username"
        userprofile = pd.read_sql(sql, connection)
        print(userprofile)
        # json_data = json.lo

        return HttpResponse(userprofile)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 1000
    page_query_param = "page"


# 继承ListAPIView很简洁的展示商品列表
class GoodsListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    商品列表页
    """
    pagination_class = StandardResultsSetPagination
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer


# 显示 request.META 中的所有信息
def display_meta(request):

    query_parras = request.query_params
    values = request.META.items()
    # values.sort()
    html = []
    for k, v in values:
        html.append('<tr><td>%s</td><td>%s</td></tr>' % (k, v))
    return HttpResponse('<table>%s</table>' % '\n'.join(html))
