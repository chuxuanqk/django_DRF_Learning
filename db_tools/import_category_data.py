# -*- coding:utf-8 -*-
__author__ = 'admin_tan'
__date__ = '2018/5/3 17:26'
__title__ = '独立使用django的model'
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

# 单独使用model去导入数据
from goods.models import GoodsCategory
from db_tools.data.category_data import row_data

'''
导入数据与model通过ORM操作实现数据的映射入库
'''
for lev1_cat in row_data:
    # 创建类目一的实例
    lev1_instance = GoodsCategory()
    # 保存数据
    lev1_instance.code = lev1_cat["code"]
    lev1_instance.name = lev1_cat["name"]
    lev1_instance.category_type = 1
    lev1_instance.save()

    for lev2_cat in lev1_cat['sub_categorys']:
        lev2_instance = GoodsCategory()
        lev2_instance.code = lev2_cat["code"]
        lev2_instance.name = lev2_cat["name"]
        lev2_instance.category_type = 2
        lev2_instance.parent_category = lev1_instance
        lev2_instance.save()

        for lev3_cat in lev2_cat['sub_categorys']:
            lev3_instance = GoodsCategory()
            lev3_instance.code = lev3_cat["code"]
            lev3_instance.name = lev3_cat["name"]
            lev3_instance.category_type = 3
            lev3_instance.parent_category = lev2_instance
            lev3_instance.save()
