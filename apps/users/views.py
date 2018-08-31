# -*- coding:utf-8 -*-

# Create your views here.
import re
from random import randint
from datetime import datetime
from datetime import timedelta

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model, login, authenticate
from django.db.models import Q
from django_redis import get_redis_connection
from rest_framework.mixins import CreateModelMixin
from rest_framework import mixins, viewsets, permissions, authentication, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler
from rest_framework_jwt.settings import api_settings

from utils.message import tengxun
from MSM.settings import REGEX_MOBILE
from .serializers import SmsSerializer, UserRegSerializer, UserDetailSerializer, UserLoginSerializer
from .serializers import UserChangePasswordSerializer, JWTSerializer
from .models import VerifyCode

User = get_user_model()
SMS_CODE_REDIS_EXPIRES = 300  # 短信过期时间 [秒]
SMS_CODE_SEND_INTERVAL = 60  # 短信发送间隔 [秒]
jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


class CustomBackend(ModelBackend):
    """
    自定义用户登录规则
    """

    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(mobile=username))
            if user.check_password(password):
                # print(user,type(user))
                return user
        except Exception as e:
            return None


class UserJWTLoginAPIView(APIView):
    """
    重写JWT认证登录
    Base API View that various JWT interactions inherit from.
    """
    serializer_class = JWTSerializer
    permission_classes = ()
    authentication_classes = ()

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'view': self,
        }

    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.
        You may want to override this if you need to provide different
        serializations depending on the incoming request.
        (Eg. admins get full serialization, others get basic serialization)
        """
        assert self.serializer_class is not None, (
                "'%s' should either include a `serializer_class` attribute, "
                "or override the `get_serializer_class()` method."
                % self.__class__.__name__)
        return self.serializer_class

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            if serializer.is_valid():
                user = serializer.object.get('user') or request.user
                token = serializer.object.get('token')
                response_data = jwt_response_payload_handler(token, user, request)
                response = Response(response_data)
                if api_settings.JWT_AUTH_COOKIE:
                    expiration = (datetime.utcnow() +
                                  api_settings.JWT_EXPIRATION_DELTA)
                    response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                        token,
                                        expires=expiration,
                                        httponly=True)
                return response
        except Exception as e:
            return Response({
                "message": str(e),
                "code": 400})


class UserLoginView(GenericAPIView):
    """
    用户登陆
    """
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid()
        except Exception as e:
            logger.error("%s" % e)
        data = serializer.validated_data
        username = data["username"]
        password = data["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            payload = jwt_payload_handler(user)
            return Response({
                "code": "200",
                "Authorization": "JWT %s" % jwt_encode_handler(payload),
                "message": "成功登录",
            })
        else:
            return Response({
                "code": "400",
                "message": "用户名或密码错误"
            })


class SmsCodeViewset(CreateModelMixin, viewsets.GenericViewSet):
    """
    发送短信验证码
    """
    serializer_class = SmsSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data["mobile"]
        message = Teng_xun(template_id=171767)
        code = self.generate_code()
        sms_status = message.send_sms(params=[code, 3], mobile=mobile)

        if sms_status["result"] != 0:
            return Response({
                "mobile": sms_status["errmsg"]
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            code_record = VerifyCode(code=code, mobile=mobile)
            code_record.save()
            return Response({
                "mobile": mobile,
                "code": code
            }, status=status.HTTP_201_CREATED)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class SmsCodeView(APIView):
    """
    发送短信
    """

    # permission_classes = (permissions.IsAuthenticated,)
    # authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)

    def get(self, request, mobile):

        # mobile = request.data['mobile']
        try:
            if not re.match(REGEX_MOBILE, mobile):
                # raise serializers.ValidationError("手机号码非法")
                raise Exception("手机号码非法")

            # 验证码发送频率
            one_mintes_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
            if VerifyCode.objects.filter(add_time__gt=one_mintes_ago, mobile=mobile).count():
                # raise serializers.ValidationError("距离上一次发送未超过60s")
                raise Exception("距离上一次发送未超过60s")

        except Exception as e:
            return Response({
                "code": "400",
                "message": e,
            })
        message = tengxun(mobile=mobile)
        code = message.generate_code()
        sms_status = message.send_sms(code)

        if sms_status["result"] != 0:
            return Response({
                "code": "400",
                "message": sms_status["errmsg"],
            })
        else:
            # 保存code到数据库
            code_record = VerifyCode(code=code, mobile=mobile)
            code_record.save()
            return Response({
                "code": "201",
                "message": "success",
            })


# 注册
# mixins.UpdateModelMixin提供的增删改查,接收 put和patch.用户的信息修改
# class UserViewset(CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
# mixins.RetrieveModelMixin获取用户详情
class UserViewset(CreateModelMixin, viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    """
    用户
    """
    serializer_class = UserRegSerializer
    queryset = User.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)

    # 动态设置serializer
    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserDetailSerializer
        elif self.action == "create":
            return UserRegSerializer

        return UserDetailSerializer

    # 这里需要动态权限配置
    # 1.用户注册的时候不应该有权限限制
    # 2.当想获取用户详情信息的时候，必须登录才行
    # permission_classes = (permissions.IsAuthenticated, )
    def get_permissions(self):
        if self.action == "retrieve":
            return [permissions.IsAuthenticated()]
        elif self.action == "create":
            return []

        return []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        re_dict = serializer.data
        payload = jwt_payload_handler(user)
        re_dict["token"] = jwt_encode_handler(payload)
        re_dict["name"] = user.name if user.name else user.username

        # headers = self.get_success_headers(serializer.data)
        # return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)
        return Response({
            "code": "200",
            "message": re_dict,
        })

    # 和mixins.Retreve方法用到,用于修改和删除
    # 返回当前用户id
    # 虽然继承了Retrieve可以获取用户详情，但是并不知道用户的id，所有要重写get_object方法
    # 重写get_object方法，就知道是哪个用户了
    def get_object(self):
        return self.request.user

    def perform_create(self, serializer):
        return serializer.save()


# 用于登录
class UserLoginViewset(CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):
        """
        用户登录
        :param request:
        :param format:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user_name = user.get('username')
        pass_word = user.get('password')
        user = authenticate(username=user_name, password=pass_word)
        if user is not None:
            re_dict = {}
            login(request, user)
            payload = jwt_payload_handler(user)
            re_dict["token"] = jwt_encode_handler(payload)
            return Response({
                "code": "200",
                "token": re_dict["token"]
            })
        else:
            return Response({
                "code": "502",
                "token": "用户名或密码错误"
            })


class loginview(APIView):

    def post(self, request):
        data = request.data
        print(type(data))

        return Response(data)


from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_http_methods


@login_required(login_url='slg:login')
@require_http_methods(["POST"])
@permission_required('slg.views_slg_manager_tem', login_url='slg:get_permissionDenied')
def change_password(request):
    """
    修改密码
    :param request:
    :return:
    """
    username = request.POST['username']
    oldPassword = request.POST['oldPassword']
    newPassword = request.POST['newPassword']
    changeResult = db_change_password(username, oldPassword, newPassword)
    return HttpResponse(changeResult)


class SmsCodeView_1(APIView):
    """
    发送短信验证码视图
    """

    def get(self, request, mobile):
        """
        1. 创建redis数据库连接,小体积缓存使用redis数据库2
        2. 生成6位验证码
        3. 分别设置验证码过期时间与短信发送间隔限制时间 ===> 使用pipeline能加快redis执行速度
        4. 异步执行发送短信任务
        """
        redis_conn = get_redis_connection("verify_code")
        sms_code = "%06d" % randint(0, 999999)

        pl = redis_conn.pipeline()
        pl.setex("sms_%s" % mobile, SMS_CODE_REDIS_EXPIRES, sms_code)
        # pl.setex("sms_%s" % mobile)
        pl.setex("send_flag_%s" % mobile, SMS_CODE_SEND_INTERVAL, 1)
        pl.execute()
        try:
            # send_sms_code.delay(sms_code=sms_code, mobile=mobile)
            message = tengxun(mobile=mobile)
            result = message.send_sms(sms_code)
            response = Response({"message": "发送成功", "code": "200"})
        except Exception as e:
            # logger.error("短信发送失败,错误原因==> %s" % e)
            response = Response({"message": "发送失败", "code": "500"})
        return response
