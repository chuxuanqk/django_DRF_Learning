# Create your views here.


from rest_framework import viewsets
from rest_framework.viewsets import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from utils.permissions import IsOwnerOrReadOnly
from .serializer import LeavingMessageSerializer
from .models import UserLeavingMessage


class LeavingMessageViewset(mixins.ListModelMixin, mixins.DestroyModelMixin, mixins.CreateModelMixin,
                            viewsets.GenericViewSet):
    """
    list:
        获取用户留言
    create:
        添加留言
    delete:
        删除留言功能
    """
    # 用户权限验证
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    # 认证方式
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    # 序列化
    serializer_class = LeavingMessageSerializer

    # 只能看到自己的留言
    def get_queryset(self):
        return UserLeavingMessage.objects.filter(user=self.request.user)