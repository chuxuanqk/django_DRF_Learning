# -*- coding:utf-8 -*-
__author__ = 'Saber'
__date__ = '22/8/18 下午11:11'


from django.conf.urls import url

from .views import SmsCodeView, UserJWTLoginAPIView

urlpatterns = [
    url(r'^send_code/(?P<mobile>.*)', SmsCodeView.as_view()),
    url(r'^UserJWTLoginAPIView/$', UserJWTLoginAPIView.as_view()),
]