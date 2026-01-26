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
                dept_belong_id=supai_dept.id  # 部门归属ID
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
