# -*- coding:utf-8 -*-
__author__ = 'Saber'
__date__ = '12/8/18 下午4:49'


from qcloudsms_py import SmsSingleSender
from qcloudsms_py.httpclient import HTTPError
from random import choice


class tengxun(object):
    """
    发送短信
    """
    appid = 1400122294
    appkey = "ce5a435193b971f75f90b4f96e052596"
    template_id = 171767
    __instance = None

    def __new__(cls, *args, **kw):
        if cls.__instance is None:
            cls.__instance = super(tengxun, cls).__new__(cls)
        return cls.__instance

    def __init__(self, mobile):
        self.mobile = mobile

    def generate_code(self):
        """
        生成六位数字的验证码
        :return:
        """
        seeds = "1234567890"
        random_str = []
        for i in range(6):
            random_str.append(choice(seeds))
        return "".join(random_str)

    def send_sms(self, code):
        ssender = SmsSingleSender(self.appid, self.appkey)
        try:
            result = ssender.send_with_param(86, self.mobile, self.template_id, [code, 3])
        except HTTPError as e:
            # print(e)
            return e
        except Exception as e:
            # print(e)
            return e

        # print(result)
        return result


if __name__ == '__main__':
    message = tengxun(mobile="13249439291")
    code = message.generate_code()
    result = message.send_sms(code)
    print(result)


