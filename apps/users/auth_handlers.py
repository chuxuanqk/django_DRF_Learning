# -*- coding:utf-8 -*-
__author__ = 'Saber'
__date__ = '30/8/18 下午1:15'


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义JWT响应负载
    """
    return{
        "message": "登陆成功",
        "code": "200",
        "Authorization": "JWT %s" % token,
        "mobile": user.mobile,
        "user_id": user.id,
        # "user_type": user.type,
        # "hx_username": user.id,
        # "hx_password": user.password
    }
