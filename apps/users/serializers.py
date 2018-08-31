# -*- coding: utf-8 -*-
__author__ = 'bobby'
import re
from datetime import datetime
from datetime import timedelta

from django.utils.translation import ugettext as _
from django_redis import get_redis_connection
from django.contrib.auth import get_user_model, authenticate
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.compat import get_username_field, PasswordField, Serializer

from .models import VerifyCode
from MSM.settings import REGEX_MOBILE

User = get_user_model()
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


class JWTSerializer(Serializer):
    """
    Serializer class used to validate a username and password.

    'username' is identified by the custom UserModel.USERNAME_FIELD.

    Returns a JSON Web Token that can be used to authenticate later calls.
    """
    def __init__(self, *args, **kwargs):
        """
        Dynamically add the USERNAME_FIELD to self.fields.
        """
        super(JWTSerializer, self).__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField()
        self.fields['password'] = PasswordField(write_only=True)

    @property
    def username_field(self):
        return get_username_field()

    def validate(self, attrs):
        credentials = {
            self.username_field: attrs.get(self.username_field),
            'password': attrs.get('password')
        }

        if all(credentials.values()):
            user = authenticate(**credentials)

            if user:
                if not user.is_active:
                    """
                    is_active: Boolean。 用户是否活跃,默认True。
                    一般不删除用户，而是将用户的is_active设为False。
                    """
                    msg = _('User account is disabled.')
                    # raise serializers.ValidationError(msg)
                    raise Exception(msg)

                payload = jwt_payload_handler(user)

                return {
                    'token': jwt_encode_handler(payload),
                    'user': user
                }
            else:
                msg = _('Unable to log in with provided credentials.')
                # raise serializers.ValidationError(msg)
                raise Exception(msg)
        else:
            msg = _('Must include "{username_field}" and "password".')
            msg = msg.format(username_field=self.username_field)
            # raise serializers.ValidationError(msg)
            raise Exception(msg)


class SmsSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11)

    def validate_mobile(self, mobile):
        """
        验证手机号码
        :param data:
        :return:
        """

        # # 手机是否注册
        # if User.objects.filter(mobile=mobile).count():
        #     raise serializers.ValidationError("用户已经存在")

        # 验证手机号码是否合法
        if not re.match(REGEX_MOBILE, mobile):
            # raise serializers.ValidationError("手机号码非法")
            raise Exception("手机号码非法")

        # 验证码发送频率
        one_mintes_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        if VerifyCode.objects.filter(add_time__gt=one_mintes_ago, mobile=mobile).count():
            # raise serializers.ValidationError("距离上一次发送未超过60s")
            raise Exception("距离上一次发送未超过60s")

    def create(self, validated_data):
        return validated_data


# 注册serializer
class UserRegSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=6,min_length=6)

    def validate_code(self, code):
        verify_recodes = VerifyCode.objects.filter(mobile=self.initial_data["username"].order)
        one_mints_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)

    class Meta:
        model = User
        fileds = ("user", "code", "mobile")


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详情序列化类
    """
    class Meta:
        model = User
        fields = ("name", "gender", "birthday", "email", "mobile")


class UserRegSerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=True, write_only=True, max_length=4, min_length=4,label="验证码",
                                 error_messages={
                                     "blank": "请输入验证码",
                                     "required": "请输入验证码",
                                     "max_length": "验证码格式错误",
                                     "min_length": "验证码格式错误"
                                 },
                                 help_text="验证码")
    username = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False,
                                     validators=[UniqueValidator(queryset=User.objects.all(), message="用户已经存在")])

    password = serializers.CharField(
        style={'input_type': 'password'},help_text="密码", label="密码", write_only=True,
    )

    # 用密文保存密码
    def create(self, validated_data):
        user = super(UserRegSerializer, self).create(validated_data=validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user

    def validate_code(self, code):
        # try:
        #     verify_records = VerifyCode.objects.get(mobile=self.initial_data["username"], code=code)
        # except VerifyCode.DoesNotExist as e:
        #     pass
        # except VerifyCode.MultipleObjectsReturned as e:
        #     pass
        verify_records = VerifyCode.objects.filter(mobile=self.initial_data["username"]).order_by("-add_time")
        if verify_records:
            last_record = verify_records[0]

            five_mintes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            if five_mintes_ago > last_record.add_time:
                raise serializers.ValidationError("验证码过期")

            if last_record.code != code:
                raise serializers.ValidationError("验证码错误")

        else:
            raise serializers.ValidationError("验证码错误")

    def validate(self, attrs):
        attrs["mobile"] = attrs["username"]
        del attrs["code"]
        return attrs

    class Meta:
        model = User
        fields = ("username", "code", "mobile", "password")


class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False,write_only=True)
    password = serializers.CharField(
        style={'input_type': 'password'},help_text="密码", label="密码", write_only=True,
    )

    def create(self, validated_data):
        return validated_data

    def validate(self, attrs):
        attrs["mobile"] = attrs["username"]
        return attrs

    class Meta:
        model = User
        fields = ('username', 'password')

    # extra_kwargs = {
    #     "password":{"write_only":True}
    # }


class UserChangePasswordSerializer(serializers.ModelSerializer):
    username = serializers.CharField(label="手机号码", max_length=11, required=True, allow_blank=False, write_only=True)
    code = serializers.CharField(required=True, write_only=True, max_length=6, min_length=6, label="验证码")
    password = serializers.CharField(style={'input_type': 'password'},help_text="密码", label="密码", write_only=True)

    def validate(self, attrs):
        attrs["mobile"] = attrs["username"]
        redis_conn = get_redis_connection("verify_code")
        mobile = attrs["username"]
        sms_code = attrs["code"]
        try:
            real_sms_code = redis_conn.get("sms_%s" % mobile).decode()
        except Exception as e:
            raise Exception("验证码已过期")
        if real_sms_code is None:
            raise Exception("验证码无效")
        if real_sms_code != sms_code:
            raise Exception("验证码错误")

        del attrs["code"]

        return attrs

    class Meta:
        model = User
        fields = ('username', 'code', 'password')
