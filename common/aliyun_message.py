import json

from alibabacloud_dysmsapi20170525.client import Client
from alibabacloud_tea_openapi.models import Config
from alibabacloud_dysmsapi20170525.models import SendSmsRequest
from alibabacloud_tea_util.models import RuntimeOptions


class AliyunSMS:

    def __init__(self):
        self.access_key_id = 'LTAI5tSoqB5Kqe5QxBa7Tvxb'
        self.access_key_secret = '4xCEaDh05zZzT8SzK1AwgWJdOOwzmO'
        self.endpoint = f'dysmsapi.aliyuncs.com'
        self.sign_name = '阿里云短信测试'
        self.template_code = 'SMS_154950909'

    def send_msg(self, mobile, code):
        """
        AccessKey ID
        LTAI5tSoqB5Kqe5QxBa7Tvxb

        AccessKey Secret
        4xCEaDh05zZzT8SzK1AwgWJdOOwzmO

        :param mobile:手机号
        :param code:验证码
        :return:
        """
        # 3. 设置短信 创建短信对象
        message = SendSmsRequest(
            sign_name=self.sign_name,
            template_code=self.template_code,
            phone_numbers=mobile,
            template_param=json.dumps({"code": code})
        )
        config = Config(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
            endpoint=self.endpoint
        )
        #  创建一个客户端
        client = Client(config)
        # 4. 设置运行时间
        runtime = RuntimeOptions()
        try:
            # 5. 发送短信
            res = client.send_sms_with_options(message, runtime)
            if res.body.code == 'OK':
                return {'code': "OK", "message": "短信发送成功"}
            else:
                return {'code': "NO", "error": res.body.message}
        except Exception as e:
            return {'code': "NO", "error": "短信发送失败"}


if __name__ == '__main__':
    AliyunSMS().send_msg(mobile='15935402546', code='020211')
