from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
from django.contrib.auth import login, authenticate
from DjangoUeditor.models import UEditorField


class UserProfile(AbstractUser):
    """
    用户
    """
    name = models.CharField(max_length=30, null=True, blank=True, verbose_name="姓名")
    birthday = models.DateField(null=True, blank=True, verbose_name="出生年月")
    gender = models.CharField(max_length=6, choices=(("male", u"男"), ("female", "女")), default="female", verbose_name="性别")
    mobile = models.CharField(null=True, blank=True, max_length=11, verbose_name="电话")
    email = models.EmailField(max_length=100, null=True, blank=True, verbose_name="邮箱")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class VerifyCode(models.Model):
    """
    短信验证码
    """
    code = models.CharField(max_length=10, verbose_name="验证码")
    mobile = models.CharField(max_length=11, verbose_name="电话")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "短信验证码"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.code


# 修改密码
def db_change_password(username, oldPassword, newPassword):
    user = authenticate(username=username, password=oldPassword)
    if user is not None:
        if user.is_active:
            user.set_password(newPassword)
            user.save()
            return 1    # 修改成功，允许特殊符号
        else:
            return -2   # 没有权限
    else:
        return -1      # 旧密码错误

