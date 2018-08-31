# -*- coding:utf-8 -*-
__author__ = 'admin_tan'
__date__ = '2018/5/3 18:01'
__title__ = ''
import sys
import os

# 获取当前文件的目录'/dbtools/'
pwd = os.path.dirname(os.path.realpath(__file__))
# 将根目录设置为当前路径的上一级路径，也就是/MxShop下(项目路径下)
sys.path.append(pwd + '../')
# 之后运行将会再项目路径下去查找setting配置,其中包括settings中install app的配置
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MSM.settings")

# 启用配置
import django

django.setup()

from goods.models import Goods, GoodsCategory, GoodsImage
from db_tools.data.product_data import row_data

# 录入商品详细数据
for goods_detail in row_data:
    # 实例商品对象
    goods = Goods()
    goods.name = goods_detail["name"]
    goods.market_price = float(int(goods_detail["market_price"].replace('￥', '').replace('元', '')))
    goods.shop_price = float(int(goods_detail["sale_price"].replace('￥', '').replace('元', '')))
    goods.goods_brief = goods_detail["desc"] if goods_detail['desc'] is not None else ''
    goods.goods_desc = goods_detail['goods_desc'] if goods_detail['goods_desc'] is not None else ''
    goods.goods_front_image = goods_detail['images'][0] if goods_detail['images'][0] else ''

    category_name = goods_detail["categorys"][-1]
    category = GoodsCategory.objects.filter(name=category_name)
    if category:
        goods.category = category[0]
    goods.save()
    # 录入每个商品的商品图片信息
    for goods_image in goods_detail["images"]:
        goods_image_instance = GoodsImage()
        goods_image_instance.image = goods_image
        goods_image_instance.goods = goods
        goods_image_instance.save()
