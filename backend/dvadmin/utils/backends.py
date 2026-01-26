import hashlib
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password
from django.utils import timezone

from dvadmin.utils.validator import CustomValidationError

logger = logging.getLogger(__name__)
UserModel = get_user_model()


class CustomBackend(ModelBackend):
    """
    Django原生认证方式
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        msg = '%s 正在使用本地登录...' % username
        logger.info(msg)
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
        else:
            verify_password = check_password(password, user.password)
            if not verify_password:
                password = hashlib.md5(password.encode(encoding='UTF-8')).hexdigest()
                verify_password = check_password(password, user.password)
            if verify_password:
                if self.user_can_authenticate(user):
                    user.last_login = timezone.now()
                    user.save()
                    return user
                raise CustomValidationError("当前用户已被禁用，请联系管理员!")
# -*- coding: utf-8 -*-
"""
创建营销部命令
"""
from django.core.management.base import BaseCommand
from django.db import models
from django.utils import timezone

from dvadmin.system.models import Dept


class Command(BaseCommand):
    help = '创建营销部部门'

    def handle(self, *args, **options):
        try:
            # 获取SUPAI部门
            supai_dept = Dept.objects.get(name='SUPAI')
            self.stdout.write(f'找到SUPAI部门，ID：{supai_dept.id}')

            # 获取同级部门的最大排序号
            max_sort = Dept.objects.filter(parent=supai_dept).aggregate(models.Max('sort'))['sort__max'] or 0

            # 检查营销部是否已存在
            existing_dept = Dept.objects.filter(name='营销部', parent=supai_dept)
            if existing_dept.exists():
                self.stdout.write(
                    self.style.WARNING(f'营销部已存在，ID：{existing_dept.first().id}')
                )
                return

            # 创建营销部
            marketing_dept = Dept.objects.create(
                name='营销部',
                parent=supai_dept,
                sort=max_sort + 1,  # 排序号在同级最后一位
                status=True,  # 启用
                dept_belong_id=supai_dept.id,  # 部门归属ID
                create_time=timezone.now(),
                update_time=timezone.now()
            )

            self.stdout.write(
                self.style.SUCCESS(f'营销部创建成功，ID：{marketing_dept.id}')
            )

        except Dept.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('未找到SUPAI部门，请先创建SUPAI部门')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'创建营销部失败：{str(e)}')
            )
