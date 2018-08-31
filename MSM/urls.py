"""MSM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.static import serve
from MSM.settings import MEDIA_ROOT
import xadmin
from rest_framework.authtoken import views
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter

from users.views import SmsCodeViewset, UserViewset, UserLoginViewset
from users.views import  SmsCodeView_1


router = DefaultRouter()

#发送短信
router.register(r'sms_code', SmsCodeViewset, base_name="sms_code")

#注册
router.register(r'user', UserViewset, base_name="user")

#登录
router.register(r'login', UserLoginViewset, base_name="logins")


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^ueditor/', include('DjangoUeditor.urls')),
    # url(r'users/send_code/$', SmsCodeView.as_view(), name="users"),
    url(r'^', include('snippets.urls')),

    url(r'^media/(?P<path>.*)$', serve,{"document_root":MEDIA_ROOT}),
    url(r'^', include(router.urls)),
    url(r'^users/', include('users.urls'), name="users"),
    url(r'^goods/', include('goods.urls'), name="goods"),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    #配置文档
    url(r'docs/', include_docs_urls(title="牧神记")),

    #drf自带的token认证模式
    url(r'^api-token-auth/', views.obtain_auth_token),

    #jwt的认证接口
    url(r'^login_JWT/', obtain_jwt_token),


    #发送短信
    url(r'^sms/(?P<mobile>.*)',SmsCodeView_1.as_view(), name='sms'),
]
