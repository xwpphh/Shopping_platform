import os.path
import random
import re
import time

from django.http import FileResponse
from rest_framework import status, mixins
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from Shopping_platform.settings import MEDIA_ROOT
from common.aliyun_message import AliyunSMS
from users.models import User, Addr, VerifCode
from .permissions import UserPermission, AddrPermission
from .serializers import UserSerializer, AddrSerializer
from rest_framework.permissions import IsAuthenticated


class RegisterView(APIView):

    def post(self, request):
        """
        1.接受用户参数
        2.参数校验
        3.创建用户
        """
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        password_confirmation = request.data.get('password_confirmation')
        # 参数校验
        # 是否为空
        if not all([username, password, email, password_confirmation]):
            return Response({'error': "请您确保已经填完所有信息"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 用户名是否已经注册
        if User.objects.filter(username=username).exists():
            return Response({'error': "用户名已存在"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 校验密码是否输入一致
        if password != password_confirmation:
            return Response({'error': "两次密码输入不一致"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 校验密码长度
        if not (6 <= len(password) <= 18):
            return Response({'error': "密码长度需在6-18位之间"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 校验邮箱是否正确
        if User.objects.filter(email=email).exists():
            return Response({'error': "该邮箱已被其他用户使用"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            return Response({'error': "邮箱格式有误"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        obj = User.objects.create_user(username=username, password=password, email=email)
        res = {
            "username": obj.username,
            "id": obj.id,
            "email": obj.email
        }
        return Response(res, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        # 自定义登录成功之后返回的结果
        result = serializer.validated_data
        result['id'] = serializer.user.id
        result['mobile'] = serializer.user.mobile
        result['email'] = serializer.user.email
        result['username'] = serializer.user.username
        result['token'] = result.pop('access')

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserView(GenericViewSet, mixins.RetrieveModelMixin, ):
    """
    用户相关操作的视图集
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # 设置认证用户才有权限访问
    permission_classes = [IsAuthenticated, UserPermission]

    def upload_avatar(self, request, *args, **kwargs):
        """
        上传用户头像
        :return:
        """
        avatar = request.data.get('avatar')
        # 校验是否有上传文件
        if not avatar:
            return Response({'error': '上传失败 文件不能为空'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 校验文件大小
        if avatar.size > 1024 * 1024:
            return Response({'error': '上传失败, 文件不能超过1mb'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 保存文件
        user = self.get_object()
        # 获取序列化对象
        ser = self.get_serializer(user, data={"avatar": avatar}, partial=True)
        # 校验保存
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response({'url': ser.data['avatar']})

    @staticmethod
    def verif_code(code, codeID, mobile):
        """
        验证校验通用逻辑
        :param request:
        :return:
        """
        # 2.参数校验
        if not code:
            return {'error': "验证码不能为空"}
        if not codeID:
            return {'error': "验证码ID不能为空"}
        if not mobile:
            return {'error': "手机号不能为空"}

        # 3.校验验证码
        if VerifCode.objects.filter(id=codeID, code=code, mobile=mobile).exists():
            # 校验验证码是否过期 过期时间为三分钟
            c_obj = VerifCode.objects.get(id=codeID, code=code, mobile=mobile)
            # 获取验证码创建时间的时间戳
            c_time = c_obj.creat_time.timestamp()
            # 获取当前时间的时间戳
            n_time = time.time()
            # 删除验证码 避免用户在有效期限内重复使用同一个验证码
            c_obj.delete()
            if c_time + 180 < n_time:
                return {'error': "验证码已过期, 请重新获取验证码"}

        else:
            return {'error': "验证码错误"}

    def bind_mobile(self, request, *args, **kwargs):
        """绑定手机号"""
        # 1.获取参数
        code = request.data.get('code')  # 获取验证码
        codeID = request.data.get('codeID')  # 获取验证码id
        mobile = request.data.get('mobile')  # 获取手机号
        result = self.verif_code(code, codeID, mobile)
        if result:
            return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 4.绑定手机号
        if User.objects.filter(mobile=mobile).exists():
            return Response({'error': "改手机号已被其他用户使用"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 绑定手机号 把手机号保存到用户mobile字段
        user = request.user
        user.mobile = mobile
        user.save()

        return Response({"message": "手机号绑定成功"}, status=status.HTTP_200_OK)

    def unbind_mobile(self, request, *args, **kwargs):
        """
        解绑手机号
        获取参数
        校验
        校验验证码
        将手机号制空
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # 1.获取参数
        code = request.data.get('code')  # 获取验证码
        codeID = request.data.get('codeID')  # 获取验证码id
        mobile = request.data.get('mobile')  # 获取手机号
        result = self.verif_code(code, codeID, mobile)
        if result:
            return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 3. 解绑手机(验证用户已绑定手机号)
        user = request.user
        if user.mobile == mobile:
            user.mobile = ''
            user.save()
            return Response({"message": "手机号解绑成功"}, status=status.HTTP_200_OK)
        else:
            return Response({'error': "手机号输入错误"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def update_name(self, request, *args, **kwargs):
        """
        修改用户昵称
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # 获取参数
        last_name = request.data.get('last_name')

        # 校验参数
        if not last_name:
            return Response({'message': "last_name不能为空"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        # 修改用户名
        user = request.user
        user.last_name = last_name
        user.save()

        return Response({'message': "用户名修改成功"}, status=status.HTTP_200_OK)

    def update_email(self, request, *args, **kwargs):
        """
        修改邮箱
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # 获取参数
        email = request.data.get('email')
        # 校验参数
        if not email:
            return Response({"message": "邮箱不能为空"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if User.objects.filter(email=email).exists():
            return Response({"message": "该邮箱已经被其他用户使用"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            return Response({"message": "邮箱格式输入错误"})

        # 修改邮箱
        user = request.user
        user.email = email
        user.save()
        return Response({'message': "邮箱修改成功"}, status=status.HTTP_200_OK)

    def update_password(self, request, *args, **kwargs):
        """
        修改密码
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # 获取参数
        password = request.data.get('password')
        password_confirmation = request.data.get('password_confirmation')
        mobile = request.data.get('mobile')
        codeID = request.data.get('codeID')
        code = request.data.get('code')
        user = request.user
        # 如果手机号正确 发送验证那
        res = re.match(r'^(13[0-9]|14[01456879]|15[0-35-9]|16[2567]|17[0-8]|18[0-9]|19[0-35-9])\d{8}$', mobile)
        if not res:
            return Response({'error': "无效的手机号"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if not mobile:
            return Response({"message": "手机号不能为空"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        if mobile == user.mobile:
            result = self.verif_code(code, codeID, mobile)
            if result:
                return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        else:
            return Response({"message": "该手机号不是您绑定的手机号"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        # 参数校验
        if not password:
            return Response({"message": "密码不能为空"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 校验密码是否输入一致
        if password != password_confirmation:
            return Response({'error': "两次密码输入不一致"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 校验密码长度
        if not (6 <= len(password) <= 18):
            return Response({'error': "密码长度需在6-18位之间"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        # 修改密码
        user = request.user
        user.set_password(password)
        user.save()

        return Response({'message': "密码修改成功 请重新登录"}, status=status.HTTP_200_OK)


class FileView(APIView):
    def get(self, request, name):
        path = MEDIA_ROOT / name
        if os.path.isfile(path):
            return FileResponse(open(path, 'rb'))

        return Response({'code': "没有找到该文件"}, status=status.HTTP_404_NOT_FOUND)


class AddrView(GenericViewSet,
               mixins.ListModelMixin,
               mixins.CreateModelMixin,
               mixins.UpdateModelMixin,
               mixins.DestroyModelMixin):
    """
    地址管理视图
    """
    queryset = Addr.objects.all()
    serializer_class = AddrSerializer

    # 设置认证用户才有权限访问
    permission_classes = [IsAuthenticated, AddrPermission]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # 通过请求过来的用户进行过滤
        queryset = queryset.filter(user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def set_default_addr(self, request, *args, **kwargs):
        """
        设置默认收获地址
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # 1. 获取到要设置的对象
        obj = self.get_object()
        obj.is_default = True
        obj.save()
        # 2.将该地址设置为默认地址 其他地址设置为非默认地址
        # 获取用户收获地址
        queryset = self.get_queryset().filter(user=request.user)
        for item in queryset:
            if item != obj:
                item.is_default = False
                item.save()

        return Response({"message": "设置成功"}, status=status.HTTP_200_OK)


class SendSMSView(APIView):
    """
    发送短信验证码
    """

    # 设置限流
    throttle_classes = (AnonRateThrottle,)

    def post(self, request):
        """
        获取手机号码
        :param request:
        :return:
        """
        mobile = request.data.get('mobile', '')
        # 验证手机号码格式 (正则表达式)
        res = re.match(r'^(13[0-9]|14[01456879]|15[0-35-9]|16[2567]|17[0-8]|18[0-9]|19[0-35-9])\d{8}$', mobile)
        if not res:
            return Response({'error': "无效的手机号"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 随机生成验证码
        code = self.get_random_code()
        # 发送验证码
        result = AliyunSMS().send_msg(mobile, code)
        if result['code'] == 'OK':
            # 将短信验证码入库
            obj = VerifCode.objects.create(mobile=mobile, code=code)
            result['codeID'] = obj.id
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_random_code(self):
        """
        随机生成验证码
        :return:
        """
        code = ''
        for i in range(6):
            n = random.choice(range(10))
            code += str(n)
        return code
