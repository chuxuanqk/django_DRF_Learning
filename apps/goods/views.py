from django.shortcuts import render

# Create your views here.

from rest_framework import generics, mixins, viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Goods, GoodsCategory
from .filters import GoodsFilter
from .serializers import GoodsSerializer, CategorySerializer


class GoodsPagination(PageNumberPagination):
    """
    商品列表自定义分页
    """
    # 默认每页显示的个数
    page_size = 10
    # 可以动态改变每页显示的个数
    page_size_query_param = 'page'
    #最多能显示多少页
    max_page_size = 100


class GoodsListView(generics.ListAPIView):
    """
    商品列表页
    """
    pagination_class = GoodsPagination    # 分页
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer

    filter_backends = (DjangoFilterBackend,)

    # 设置filter的类为我们自定义的类
    filter_class = GoodsFilter


class GoodsListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    商品列表页
    """
    # 这里必须要定义一个默认的排序，否则会报错
    queryset = Goods.objects.all().order_by('id')
    # 分页
    pagination_class = GoodsPagination
    serializer_class = GoodsSerializer
    # 添加过滤器选项
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)

    # 设置filter的类为我们自定义的类
    filter_class = GoodsFilter
    search_fields = ('=name', 'goods_brief')


class CategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
        商品分类列表数据
    """

    queryset = GoodsCategory.objects.filter(category_type=1)
    serializer_class = CategorySerializer
