from rest_framework import permissions


class CollectPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        # 如果不是管理员 则判断操作的用户对象和登录的用户对象是否为同一个
        return obj.user == request.user
