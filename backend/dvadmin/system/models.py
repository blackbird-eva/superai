import hashlib
import os
import uuid
from time import time
from pathlib import PurePosixPath

from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.hashers import make_password
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils import timezone
from application import dispatch
from dvadmin.utils.models import CoreModel, table_prefix, get_custom_app_models


class CustomUserManager(UserManager):
    """自定义用户管理器"""

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)


class Users(AbstractUser, CoreModel):
    """用户模型"""

    username = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        verbose_name="用户账号",
        help_text="用户账号"
    )
    email = models.EmailField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="邮箱",
        help_text="邮箱"
    )
    mobile = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="电话",
        help_text="电话"
    )
    avatar = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="头像",
        help_text="头像"
    )
    name = models.CharField(
        max_length=40,
        verbose_name="姓名",
        help_text="姓名"
    )
    gender = models.IntegerField(
        choices=[(0, '未知'), (1, '男'), (2, '女')],
        default=0,
        null=True,
        blank=True,
        verbose_name="性别",
        help_text="性别"
    )
    user_type = models.IntegerField(
        choices=[(0, '后台用户'), (1, '前台用户')],
        default=0,
        null=True,
        blank=True,
        verbose_name="用户类型",
        help_text="用户类型"
    )
    login_error_count = models.IntegerField(
        default=0,
        verbose_name="登录错误次数",
        help_text="登录错误次数"
    )
    pwd_change_count = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name="密码修改次数",
        help_text="密码修改次数"
    )
    dept = models.ForeignKey(
        'Dept',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_constraint=False,
        verbose_name="所属部门",
        help_text="所属部门"
    )
    current_role = models.ForeignKey(
        'Role',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_constraint=False,
        related_name='current_role_set',
        verbose_name="当前登录角色",
        help_text="当前登录角色"
    )
    manage_dept = models.ManyToManyField(
        'Dept',
        blank=True,
        db_constraint=False,
        related_name='manage_dept_set',
        verbose_name="管理部门",
        help_text="管理部门"
    )
    post = models.ManyToManyField(
        'Post',
        blank=True,
        db_constraint=False,
        verbose_name="关联岗位",
        help_text="关联岗位"
    )
    role = models.ManyToManyField(
        'Role',
        blank=True,
        db_constraint=False,
        verbose_name="关联角色",
        help_text="关联角色"
    )

    objects = CustomUserManager()

    class Meta:
        db_table = table_prefix + "users"
        verbose_name = "用户表"
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)

    def __str__(self):
        return f"{self.name}({self.username})"

    def set_password(self, raw_password):
        """设置密码"""
        md5_pwd = hashlib.md5(raw_password.encode(encoding='UTF-8')).hexdigest()
        return super().set_password(md5_pwd)


class Dept(CoreModel):
    """部门表"""

    name = models.CharField(max_length=64, verbose_name="部门名称", help_text="部门名称")
    key = models.CharField(
        max_length=64,
        unique=True,
        null=True,
        blank=True,
        verbose_name="关联字符",
        help_text="关联字符"
    )
    sort = models.IntegerField(default=1, verbose_name="显示排序", help_text="显示排序")
    owner = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        verbose_name="负责人",
        help_text="负责人"
    )
    phone = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        verbose_name="联系电话",
        help_text="联系电话"
    )
    email = models.EmailField(
        max_length=32,
        null=True,
        blank=True,
        verbose_name="邮箱",
        help_text="邮箱"
    )
    status = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        verbose_name="部门状态",
        help_text="部门状态"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_constraint=False,
        default=None,
        verbose_name="上级部门",
        help_text="上级部门"
    )

    class Meta:
        db_table = table_prefix + "dept"
        verbose_name = "部门表"
        verbose_name_plural = verbose_name
        ordering = ('sort',)

    def __str__(self):
        return self.name


class Role(CoreModel):
    """角色表"""

    name = models.CharField(max_length=64, verbose_name="角色名称", help_text="角色名称")
    key = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="权限字符",
        help_text="权限字符"
    )
    sort = models.IntegerField(default=1, verbose_name="角色顺序", help_text="角色顺序")
    status = models.BooleanField(default=True, verbose_name="角色状态", help_text="角色状态")

    class Meta:
        db_table = table_prefix + "role"
        verbose_name = "角色表"
        verbose_name_plural = verbose_name
        ordering = ('sort',)

    def __str__(self):
        return self.name


class Post(CoreModel):
    """岗位表"""

    name = models.CharField(max_length=64, verbose_name="岗位名称", help_text="岗位名称")
    code = models.CharField(max_length=32, verbose_name="岗位编码", help_text="岗位编码")
    sort = models.IntegerField(default=1, verbose_name="岗位顺序", help_text="岗位顺序")
    status = models.IntegerField(
        choices=[(0, '离职'), (1, '在职')],
        default=1,
        verbose_name="岗位状态",
        help_text="岗位状态"
    )

    class Meta:
        db_table = table_prefix + "post"
        verbose_name = "岗位表"
        verbose_name_plural = verbose_name
        ordering = ('sort',)

    def __str__(self):
        return self.name


class Menu(CoreModel):
    """菜单表"""

    icon = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name="菜单图标",
        help_text="菜单图标"
    )
    name = models.CharField(max_length=64, verbose_name="菜单名称", help_text="菜单名称")
    sort = models.IntegerField(
        default=1,
        null=True,
        blank=True,
        verbose_name="显示排序",
        help_text="显示排序"
    )
    is_link = models.BooleanField(default=False, verbose_name="是否外链", help_text="是否外链")
    link_url = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="链接地址",
        help_text="链接地址"
    )
    is_catalog = models.BooleanField(default=False, verbose_name="是否目录", help_text="是否目录")
    web_path = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        verbose_name="路由地址",
        help_text="路由地址"
    )
    component = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        verbose_name="组件地址",
        help_text="组件地址"
    )
    component_name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="组件名称",
        help_text="组件名称"
    )
    status = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        verbose_name="菜单状态",
        help_text="菜单状态"
    )
    cache = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        verbose_name="是否页面缓存",
        help_text="是否页面缓存"
    )
    visible = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        verbose_name="侧边栏中是否显示",
        help_text="侧边栏中是否显示"
    )
    is_iframe = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        verbose_name="框架外显示",
        help_text="框架外显示"
    )
    is_affix = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        verbose_name="是否固定",
        help_text="是否固定"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_constraint=False,
        verbose_name="上级菜单",
        help_text="上级菜单"
    )

    class Meta:
        db_table = table_prefix + "menu"
        verbose_name = "菜单表"
        verbose_name_plural = verbose_name
        ordering = ('sort',)

    def __str__(self):
        return self.name


class MenuButton(CoreModel):
    """菜单权限表"""

    name = models.CharField(max_length=64, verbose_name="名称", help_text="名称")
    value = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="权限值",
        help_text="权限值"
    )
    api = models.CharField(max_length=200, verbose_name="接口地址", help_text="接口地址")
    method = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name="接口请求方法",
        help_text="接口请求方法"
    )
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        db_constraint=False,
        related_name='menuPermission',
        verbose_name="关联菜单",
        help_text="关联菜单"
    )

    class Meta:
        db_table = table_prefix + "menu_button"
        verbose_name = "菜单权限表"
        verbose_name_plural = verbose_name
        ordering = ('-name',)

    def __str__(self):
        return self.name


class RoleMenuPermission(CoreModel):
    """角色菜单权限表"""

    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        db_constraint=False,
        related_name='role_menu',
        verbose_name="关联菜单",
        help_text="关联菜单"
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        db_constraint=False,
        related_name='role_menu',
        verbose_name="关联角色",
        help_text="关联角色"
    )

    class Meta:
        db_table = table_prefix + "role_menu_permission"
        verbose_name = "角色菜单权限表"
        verbose_name_plural = verbose_name


class RoleMenuButtonPermission(CoreModel):
    """角色按钮权限表"""

    data_range = models.IntegerField(
        choices=[
            (0, '仅本人数据权限'),
            (1, '本部门及以下数据权限'),
            (2, '本部门数据权限'),
            (3, '全部数据权限'),
            (4, '自定数据权限')
        ],
        default=0,
        verbose_name="数据权限范围",
        help_text="数据权限范围"
    )
    menu_button = models.ForeignKey(
        MenuButton,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_constraint=False,
        related_name='menu_button_permission',
        verbose_name="关联菜单按钮",
        help_text="关联菜单按钮"
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        db_constraint=False,
        related_name='role_menu_button',
        verbose_name="关联角色",
        help_text="关联角色"
    )
    dept = models.ManyToManyField(
        Dept,
        blank=True,
        db_constraint=False,
        verbose_name="数据权限-关联部门",
        help_text="数据权限-关联部门"
    )

    class Meta:
        db_table = table_prefix + "role_menu_button_permission"
        verbose_name = "角色按钮权限表"
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)


class OperationLog(CoreModel):
    """操作日志"""

    request_modular = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name="请求模块",
        help_text="请求模块"
    )
    request_path = models.CharField(
        max_length=400,
        null=True,
        blank=True,
        verbose_name="请求地址",
        help_text="请求地址"
    )
    request_body = models.TextField(
        null=True,
        blank=True,
        verbose_name="请求参数",
        help_text="请求参数"
    )
    request_method = models.CharField(
        max_length=8,
        null=True,
        blank=True,
        verbose_name="请求方式",
        help_text="请求方式"
    )
    request_msg = models.TextField(
        null=True,
        blank=True,
        verbose_name="操作说明",
        help_text="操作说明"
    )
    request_ip = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        verbose_name="请求ip地址",
        help_text="请求ip地址"
    )
    request_browser = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name="请求浏览器",
        help_text="请求浏览器"
    )
    response_code = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        verbose_name="响应状态码",
        help_text="响应状态码"
    )
    request_os = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name="操作系统",
        help_text="操作系统"
    )
    json_result = models.TextField(
        null=True,
        blank=True,
        verbose_name="返回信息",
        help_text="返回信息"
    )
    status = models.BooleanField(default=False, verbose_name="响应状态", help_text="响应状态")

    class Meta:
        db_table = table_prefix + "operation_log"
        verbose_name = "操作日志"
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)


class LoginLog(CoreModel):
    """登录日志"""

    username = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        verbose_name="登录用户名",
        help_text="登录用户名"
    )
    ip = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        verbose_name="登录ip",
        help_text="登录ip"
    )
    agent = models.TextField(
        null=True,
        blank=True,
        verbose_name="agent信息",
        help_text="agent信息"
    )
    browser = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="浏览器名",
        help_text="浏览器名"
    )
    os = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="操作系统",
        help_text="操作系统"
    )
    continent = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="州",
        help_text="州"
    )
    country = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="国家",
        help_text="国家"
    )
    province = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="省份",
        help_text="省份"
    )
    city = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="城市",
        help_text="城市"
    )
    district = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="县区",
        help_text="县区"
    )
    isp = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="运营商",
        help_text="运营商"
    )
    area_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="区域代码",
        help_text="区域代码"
    )
    country_english = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="英文全称",
        help_text="英文全称"
    )
    country_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="简称",
        help_text="简称"
    )
    longitude = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="经度",
        help_text="经度"
    )
    latitude = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="纬度",
        help_text="纬度"
    )
    login_type = models.IntegerField(
        choices=[(1, '普通登录'), (2, '微信扫码登录')],
        default=1,
        verbose_name="登录类型",
        help_text="登录类型"
    )

    class Meta:
        db_table = table_prefix + "login_log"
        verbose_name = "登录日志"
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)

    def __str__(self):
        return self.username


def media_file_name(instance, filename):
    """文件上传路径生成函数"""
    import os
    from datetime import datetime
    ext = filename.split('.')[-1]
    date_path = datetime.now().strftime('%Y/%m/%d')
    return f'file/{date_path}/{uuid.uuid4().hex}.{ext}'


def media_file_name_downloadcenter(instance, filename):
    """下载中心文件上传路径生成函数"""
    import os
    from datetime import datetime
    ext = filename.split('.')[-1]
    date_path = datetime.now().strftime('%Y/%m/%d')
    return f'download/{date_path}/{uuid.uuid4().hex}.{ext}'


class FileList(CoreModel):
    """文件管理"""

    name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="名称",
        help_text="名称"
    )
    url = models.FileField(
        blank=True,
        null=True,
        upload_to=media_file_name
    )
    file_url = models.CharField(
        max_length=255,
        verbose_name="文件地址",
        help_text="文件地址"
    )
    engine = models.CharField(
        max_length=100,
        default='local',
        blank=True,
        verbose_name="引擎",
        help_text="引擎"
    )
    mime_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Mime类型",
        help_text="Mime类型"
    )
    size = models.CharField(
        max_length=36,
        blank=True,
        verbose_name="文件大小",
        help_text="文件大小"
    )
    md5sum = models.CharField(
        max_length=36,
        blank=True,
        verbose_name="文件md5",
        help_text="文件md5"
    )
    upload_method = models.SmallIntegerField(
        choices=[(0, '默认上传'), (1, '文件选择器上传')],
        default=0,
        null=True,
        blank=True,
        verbose_name="上传方式",
        help_text="上传方式"
    )
    file_type = models.SmallIntegerField(
        choices=[(0, '图片'), (1, '视频'), (2, '音频'), (3, '其他')],
        default=3,
        null=True,
        blank=True,
        verbose_name="文件类型",
        help_text="文件类型"
    )

    class Meta:
        db_table = table_prefix + "file_list"
        verbose_name = "文件管理"
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)


class MenuField(CoreModel):
    """菜单字段表"""

    model = models.CharField(max_length=64, verbose_name="表名", help_text="表名")
    field_name = models.CharField(
        max_length=64,
        verbose_name="模型表字段名",
        help_text="模型表字段名"
    )
    title = models.CharField(
        max_length=64,
        verbose_name="字段显示名",
        help_text="字段显示名"
    )
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        db_constraint=False,
        verbose_name="菜单",
        help_text="菜单"
    )

    class Meta:
        db_table = table_prefix + "menu_field"
        verbose_name = "菜单字段表"
        verbose_name_plural = verbose_name
        ordering = ('id',)


class FieldPermission(CoreModel):
    """字段权限表"""

    is_query = models.BooleanField(default=1, verbose_name="是否可查询", help_text="是否可查询")
    is_create = models.BooleanField(default=1, verbose_name="是否可创建", help_text="是否可创建")
    is_update = models.BooleanField(default=1, verbose_name="是否可更新", help_text="是否可更新")
    field = models.ForeignKey(
        MenuField,
        on_delete=models.CASCADE,
        db_constraint=False,
        related_name='menu_field',
        verbose_name="字段",
        help_text="字段"
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        db_constraint=False,
        verbose_name="角色",
        help_text="角色"
    )

    class Meta:
        db_table = table_prefix + "field_permission"
        verbose_name = "字段权限表"
        verbose_name_plural = verbose_name
        ordering = ('id',)


class DownloadCenter(CoreModel):
    """下载中心"""

    task_name = models.CharField(
        max_length=255,
        verbose_name="任务名称",
        help_text="任务名称"
    )
    task_status = models.SmallIntegerField(
        choices=[(0, '任务已创建'), (1, '任务进行中'), (2, '任务完成'), (3, '任务失败')],
        default=0,
        verbose_name="是否可下载",
        help_text="是否可下载"
    )
    file_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="文件名",
        help_text="文件名"
    )
    url = models.FileField(
        blank=True,
        null=True,
        upload_to=media_file_name_downloadcenter
    )
    size = models.BigIntegerField(default=0, verbose_name="文件大小", help_text="文件大小")
    md5sum = models.CharField(
        max_length=36,
        null=True,
        blank=True,
        verbose_name="文件md5",
        help_text="文件md5"
    )

    class Meta:
        db_table = table_prefix + "download_center"
        verbose_name = "下载中心"
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)

    def __str__(self):
        return self.task_name


class Dictionary(CoreModel):
    """字典表"""

    label = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="字典名称",
        help_text="字典名称"
    )
    value = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="字典编号/实际值",
        help_text="字典编号"
    )
    type = models.IntegerField(
        choices=[(0, 'text'), (1, 'number'), (2, 'date'), (3, 'datetime'),
                 (4, 'time'), (5, 'files'), (6, 'boolean'), (7, 'images')],
        default=0,
        verbose_name="数据值类型",
        help_text="数据值类型"
    )
    color = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="颜色",
        help_text="颜色"
    )
    is_value = models.BooleanField(
        default=False,
        verbose_name="是否为value值,用来做具体值存放",
        help_text="是否为value值"
    )
    status = models.BooleanField(default=True, verbose_name="状态", help_text="状态")
    sort = models.IntegerField(
        default=1,
        null=True,
        blank=True,
        verbose_name="显示排序",
        help_text="显示排序"
    )
    remark = models.CharField(
        max_length=2000,
        null=True,
        blank=True,
        verbose_name="备注",
        help_text="备注"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_constraint=False,
        related_name='sublist',
        verbose_name="父级",
        help_text="父级"
    )

    class Meta:
        db_table = table_prefix + "dictionary"
        verbose_name = "字典表"
        verbose_name_plural = verbose_name
        ordering = ('sort',)

    def __str__(self):
        return self.label


class Area(CoreModel):
    """地区表"""

    name = models.CharField(max_length=100, verbose_name="名称", help_text="名称")
    code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        verbose_name="地区编码",
        help_text="地区编码"
    )
    level = models.BigIntegerField(
        verbose_name="地区层级(1省份 2城市 3区县 4乡级)",
        help_text="地区层级(1省份 2城市 3区县 4乡级)"
    )
    pinyin = models.CharField(max_length=255, verbose_name="拼音", help_text="拼音")
    initials = models.CharField(max_length=20, verbose_name="首字母", help_text="首字母")
    enable = models.BooleanField(default=True, verbose_name="是否启用", help_text="是否启用")
    pcode = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_constraint=False,
        to_field='code',
        verbose_name="父地区编码",
        help_text="父地区编码"
    )

    class Meta:
        db_table = table_prefix + "area"
        verbose_name = "地区表"
        verbose_name_plural = verbose_name
        ordering = ('code',)

    def __str__(self):
        return self.name


class ApiWhiteList(CoreModel):
    """接口白名单"""

    url = models.CharField(max_length=200, verbose_name="url", help_text="url地址")
    method = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name="接口请求方法",
        help_text="接口请求方法"
    )
    enable_datasource = models.BooleanField(
        default=True,
        blank=True,
        verbose_name="激活数据权限",
        help_text="激活数据权限"
    )

    class Meta:
        db_table = table_prefix + "api_white_list"
        verbose_name = "接口白名单"
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)


class SystemConfig(CoreModel):
    """系统配置表"""

    title = models.CharField(max_length=50, verbose_name="标题", help_text="标题")
    key = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name="键",
        help_text="键"
    )
    value = models.JSONField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="值",
        help_text="值"
    )
    sort = models.IntegerField(
        default=0,
        blank=True,
        verbose_name="排序",
        help_text="排序"
    )
    status = models.BooleanField(default=True, verbose_name="启用状态", help_text="启用状态")
    data_options = models.JSONField(
        null=True,
        blank=True,
        verbose_name="数据options",
        help_text="数据options"
    )
    form_item_type = models.IntegerField(
        choices=[(0, 'text'), (1, 'datetime'), (2, 'date'), (3, 'textarea'), (4, 'select'),
                 (5, 'checkbox'), (6, 'radio'), (7, 'img'), (8, 'file'), (9, 'switch'),
                 (10, 'number'), (11, 'array'), (12, 'imgs'), (13, 'foreignkey'),
                 (14, 'manytomany'), (15, 'time')],
        default=0,
        blank=True,
        verbose_name="表单类型",
        help_text="表单类型"
    )
    rule = models.JSONField(
        null=True,
        blank=True,
        verbose_name="校验规则",
        help_text="校验规则"
    )
    placeholder = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="提示信息",
        help_text="提示信息"
    )
    setting = models.JSONField(
        null=True,
        blank=True,
        verbose_name="配置",
        help_text="配置"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_constraint=False,
        verbose_name="父级",
        help_text="父级"
    )

    class Meta:
        db_table = table_prefix + "system_config"
        verbose_name = "系统配置表"
        verbose_name_plural = verbose_name
        ordering = ('sort',)
        unique_together = (('key', 'parent_id'),)

    def __str__(self):
        return self.title


class MessageCenter(CoreModel):
    """消息中心"""

    title = models.CharField(max_length=100, verbose_name="标题", help_text="标题")
    content = models.TextField(verbose_name="内容", help_text="内容")
    target_type = models.IntegerField(default=0, verbose_name="目标类型", help_text="目标类型")
    target_dept = models.ManyToManyField(
        Dept,
        blank=True,
        db_constraint=False,
        verbose_name="目标部门",
        help_text="目标部门"
    )
    target_role = models.ManyToManyField(
        Role,
        blank=True,
        db_constraint=False,
        verbose_name="目标角色",
        help_text="目标角色"
    )
    target_user = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        through='MessageCenterTargetUser',
        through_fields=('messagecenter', 'users'),
        related_name='user',
        verbose_name="目标用户",
        help_text="目标用户"
    )

    class Meta:
        db_table = table_prefix + "message_center"
        verbose_name = "消息中心"
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)

    def __str__(self):
        return self.title


class MessageCenterTargetUser(CoreModel):
    """消息中心目标用户表"""

    is_read = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        verbose_name="是否已读",
        help_text="是否已读"
    )
    messagecenter = models.ForeignKey(
        'MessageCenter',
        on_delete=models.CASCADE,
        db_constraint=False,
        verbose_name="关联消息中心表",
        help_text="关联消息中心表"
    )
    users = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_constraint=False,
        related_name='target_user',
        verbose_name="关联用户表",
        help_text="关联用户表"
    )

    class Meta:
        db_table = table_prefix + "message_center_target_user"
        verbose_name = "消息中心目标用户表"
        verbose_name_plural = verbose_name


# 文档翻译状态选项
DOCXFILE_STATUS = [
    ('uploaded', '已上传'),
    ('processing', '处理中'),
    ('completed', '翻译完成'),
    ('failed', '翻译失败'),
    ('cancelled', '已取消'),
]


def docxfile_upload_path(instance, filename):
    """
    文档文件上传路径生成函数
    """
    # 生成唯一文件名
    ext = filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    
    # 按日期组织目录结构
    from datetime import datetime
    date_path = datetime.now().strftime('%Y/%m/%d')
    
    return f'docx/{date_path}/{unique_filename}'


def calculate_file_md5(file_path):
    """
    计算文件MD5值
    """
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return None


class Docxfile(CoreModel):
    """
    DOCX文档翻译管理
    """
    # 基本文件信息
    original_name = models.CharField(max_length=255, verbose_name="原始文件名", help_text="原始文件名")
    file_path = models.FileField(upload_to=docxfile_upload_path, verbose_name="文件路径", help_text="存储的文件路径")
    file_size = models.IntegerField(default=0, verbose_name="文件大小", help_text="文件大小(字节)")
    
    # 文档类型和支持格式
    DOCUMENT_TYPES = [
        ('docx', 'Word文档 (.docx)'),
        ('ppt', 'PowerPoint (.ppt/.pptx)'),
        ('pdf', 'PDF文档 (.pdf)'),
        ('txt', '纯文本 (.txt)'),
        ('other', '其他格式')
    ]
    type = models.CharField(
        max_length=10, 
        choices=DOCUMENT_TYPES, 
        default='docx', 
        verbose_name="文档类型", 
        help_text="文档文件类型"
    )
    
    # 文档简介
    about_text = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="文档简介", 
        help_text="文档内容简要描述"
    )
    
    # 功能开关
    transtask = models.BooleanField(
        default=True, 
        verbose_name="需要翻译", 
        help_text="是否需要进行翻译任务"
    )
    graphtask = models.BooleanField(
        default=False, 
        verbose_name="知识图谱", 
        help_text="是否生成知识图谱"
    )
    share = models.BooleanField(
        default=False, 
        verbose_name="是否分享", 
        help_text="是否允许分享给其他用户"
    )
    userversion = models.BooleanField(
        default=True, 
        verbose_name="版本控制", 
        help_text="是否启用版本控制功能"
    )
    
    # 翻译相关字段
    status = models.CharField(
        max_length=20, 
        choices=DOCXFILE_STATUS, 
        default="uploaded", 
        verbose_name="翻译状态", 
        help_text="文档翻译处理状态"
    )
    paragraph_count = models.IntegerField(default=0, verbose_name="段落数量", help_text="文档段落总数")
    word_count = models.IntegerField(default=0, verbose_name="字数统计", help_text="文档总字数")
    page_count = models.IntegerField(default=0, verbose_name="页数统计", help_text="文档页数")
    
    # 语言设置
    source_language = models.CharField(max_length=10, default="auto", verbose_name="源语言", help_text="原文语言代码")
    target_language = models.CharField(max_length=10, default="zh", verbose_name="目标语言", help_text="目标翻译语言代码")
    
    # 处理信息
    processing_time = models.FloatField(default=0, verbose_name="处理时间", help_text="翻译处理耗时(秒)")
    error_message = models.TextField(blank=True, null=True, verbose_name="错误信息", help_text="处理过程中的错误信息")
    
    # 翻译结果
    translated_path = models.CharField(max_length=500, blank=True, null=True, verbose_name="翻译后文件路径", help_text="翻译后文档存储路径")
    translated_filename = models.CharField(max_length=255, blank=True, null=True, verbose_name="翻译后文件名", help_text="翻译后文件名")
    
    class Meta:
        db_table = table_prefix + "docxfile"
        verbose_name = "DOCX文档翻译"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["type"]),
            models.Index(fields=["transtask", "graphtask", "share"]),
            models.Index(fields=["source_language", "target_language"]),
            models.Index(fields=["create_datetime"]),
        ]


class Docxpages(CoreModel):
    """
    文档页面内容管理
    用于存储文档中每个页面的详细内容和翻译结果
    """
    # 关联文档
    docxfile = models.ForeignKey(
        Docxfile,
        on_delete=models.CASCADE,
        related_name='pages',
        verbose_name="所属文档",
        help_text="关联的文档文件"
    )
    
    # 页面基本信息
    page_number = models.IntegerField(
        verbose_name="页码",
        help_text="文档中的页码序号"
    )
    
    # 原始页面内容
    original_title = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="原始标题",
        help_text="页面标题或章节标题"
    )
    
    original_content = models.TextField(
        blank=True,
        null=True,
        verbose_name="原始内容",
        help_text="页面原始文本内容"
    )
    
    # 翻译后内容
    translated_title = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="翻译后标题",
        help_text="翻译后的页面标题"
    )
    
    translated_content = models.TextField(
        blank=True,
        null=True,
        verbose_name="翻译后内容",
        help_text="翻译后的页面内容"
    )
    
    # 内容统计
    char_count = models.IntegerField(
        default=0,
        verbose_name="字符数",
        help_text="原始内容字符数量"
    )
    
    translated_char_count = models.IntegerField(
        default=0,
        verbose_name="翻译后字符数",
        help_text="翻译后内容字符数量"
    )
    
    paragraph_count = models.IntegerField(
        default=0,
        verbose_name="段落数",
        help_text="页面内段落数量"
    )
    
    # 处理状态
    PAGE_STATUS = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '处理完成'),
        ('failed', '处理失败'),
        ('skipped', '跳过')
    ]
    
    status = models.CharField(
        max_length=20,
        choices=PAGE_STATUS,
        default='pending',
        verbose_name="处理状态",
        help_text="页面内容处理状态"
    )
    
    # 处理信息
    processing_order = models.IntegerField(
        default=0,
        verbose_name="处理顺序",
        help_text="页面处理的先后顺序"
    )
    
    processing_time = models.FloatField(
        default=0,
        verbose_name="处理时间",
        help_text="页面处理耗时(秒)"
    )
    
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name="错误信息",
        help_text="页面处理过程中的错误信息"
    )
    
    # 内容预览和索引
    preview_text = models.TextField(
        blank=True,
        null=True,
        verbose_name="预览文本",
        help_text="内容预览片段，用于快速浏览"
    )
    
    content_hash = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name="内容哈希",
        help_text="内容MD5哈希值，用于去重和完整性校验"
    )
    
    # 知识图谱相关数据
    entities = models.JSONField(
        blank=True,
        null=True,
        verbose_name="实体列表",
        help_text="页面中提取的实体信息(JSON格式)"
    )
    
    keywords = models.JSONField(
        blank=True,
        null=True,
        verbose_name="关键词",
        help_text="页面关键词列表(JSON格式)"
    )
    
    summary = models.TextField(
        blank=True,
        null=True,
        verbose_name="摘要",
        help_text="页面内容摘要"
    )
    
    # 版本控制
    version = models.IntegerField(
        default=1,
        verbose_name="版本号",
        help_text="内容版本号"
    )
    
    parent_page = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='versions',
        verbose_name="父版本",
        help_text="上一版本页面，用于版本追踪"
    )
    
    # 元数据
    page_metadata = models.JSONField(
        blank=True,
        null=True,
        verbose_name="页面元数据",
        help_text="页面相关的元数据信息(JSON格式)"
    )
    
    class Meta:
        db_table = table_prefix + "docxpages"
        verbose_name = "文档页面内容"
        verbose_name_plural = verbose_name
        ordering = ["docxfile", "page_number", "-create_datetime"]
        unique_together = [["docxfile", "page_number", "version"]]
        indexes = [
            models.Index(fields=["docxfile", "page_number"]),
            models.Index(fields=["docxfile", "status"]),
            models.Index(fields=["status", "processing_order"]),
            models.Index(fields=["content_hash"]),
            models.Index(fields=["create_datetime"]),
            models.Index(fields=["version"]),
        ]
    
    def __str__(self):
        return f"{self.docxfile.original_name} - 第{self.page_number}页"
    
    def save(self, *args, **kwargs):
        """
        重写save方法，自动计算字符数和生成哈希值
        """
        # 计算字符数
        if self.original_content:
            self.char_count = len(self.original_content)
        
        if self.translated_content:
            self.translated_char_count = len(self.translated_content)
        
        # 生成内容哈希
        if self.original_content and not self.content_hash:
            self.content_hash = hashlib.md5(self.original_content.encode('utf-8')).hexdigest()
        
        # 生成预览文本
        if self.original_content and not self.preview_text:
            # 取前200个字符作为预览
            preview = self.original_content[:200]
            if len(self.original_content) > 200:
                preview += "..."
            self.preview_text = preview
        
        super().save(*args, **kwargs)
    
    def get_content_preview(self, length=100):
        """
        获取内容预览
        """
        content = self.translated_content or self.original_content or ""
        if len(content) <= length:
            return content
        return content[:length] + "..."
    
    def is_translated(self):
        """
        检查页面是否已翻译
        """
        return bool(self.translated_content and self.status == 'completed')
    
    def get_processing_progress(self):
        """
        获取处理进度信息
        """
        return {
            'page_number': self.page_number,
            'status': self.status,
            'char_count': self.char_count,
            'translated_char_count': self.translated_char_count,
            'paragraph_count': self.paragraph_count,
            'processing_time': self.processing_time,
            'has_entities': bool(self.entities),
            'has_keywords': bool(self.keywords),
            'has_summary': bool(self.summary)
        }


class Transdicts(CoreModel):
    CATEGORY_CHOICES = (
        ('通用', '通用'),
        ('飞行', '飞行'),
        ('行业', '行业'),
        ('机械', '机械'),
        ('维保', '维保'),
        ('文档', '文档'),
        ('其他', '其他'),
    )
    pcate = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="类别", default='通用', null=False, blank=False, help_text="词条类别")
    cn = models.CharField(max_length=200, verbose_name="中文", help_text="词条中文")
    en = models.CharField(max_length=200, verbose_name="英文", help_text="词条英文")
    infos = models.CharField(max_length=200, verbose_name="信息", null=True, blank=True, help_text="额外信息")
    note = models.CharField(max_length=200, verbose_name="备注", null=True, blank=True, help_text="备注信息")
    ainote = models.CharField(max_length=200, verbose_name="AI备注", null=True, blank=True, help_text="备注信息")
    weight = models.FloatField(verbose_name="权重", default=3.0, help_text="权重")

    class Meta:
        db_table = table_prefix + "transdicts"
        verbose_name = "翻译字典"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)


def pptfile_upload_path(instance, filename):
    """
    PPT文件上传路径生成函数
    """
    ext = filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4().hex}.{ext}"

    # 按日期组织目录结构
    from datetime import datetime
    date_path = datetime.now().strftime('%Y/%m/%d')

    return f'ppt/{date_path}/{unique_filename}'


class PPTFile(CoreModel):
    """
    PPT文件管理模型 - 用于存储上传的网页内容和生成的PPT文件
    """
    # PPT基本信息
    title = models.CharField(
        max_length=500,
        verbose_name="PPT标题",
        help_text="演示文稿标题"
    )

    original_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="原始文件名",
        help_text="上传的原始文件名"
    )

    # 文件信息
    file_path = models.FileField(
        upload_to=pptfile_upload_path,
        blank=True,
        null=True,
        verbose_name="PPT文件路径",
        help_text="生成的PPT文件存储路径"
    )

    file_size = models.IntegerField(
        default=0,
        verbose_name="文件大小",
        help_text="PPT文件大小(字节)"
    )

    # 内容相关
    source_type = models.CharField(
        max_length=20,
        choices=[
            ('text', '文本输入'),
            ('file', '文件上传'),
            ('web', '网页抓取')
        ],
        default='text',
        verbose_name="来源类型",
        help_text="内容来源方式"
    )

    source_url = models.URLField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name="来源URL",
        help_text="网页抓取时的URL地址"
    )

    content_text = models.TextField(
        blank=True,
        null=True,
        verbose_name="原始内容",
        help_text="用于生成PPT的原始文本内容"
    )

    content_summary = models.TextField(
        blank=True,
        null=True,
        verbose_name="内容摘要",
        help_text="内容简要描述"
    )

    # PPT生成参数
    theme = models.CharField(
        max_length=20,
        choices=[
            ('business', '商务简约'),
            ('tech', '科技现代'),
            ('education', '教育培训'),
            ('creative', '创意活泼'),
            ('academic', '学术正式')
        ],
        default='business',
        verbose_name="主题风格",
        help_text="PPT主题风格"
    )

    slide_count = models.IntegerField(
        default=10,
        verbose_name="幻灯片数量",
        help_text="生成的幻灯片数量"
    )

    include_charts = models.BooleanField(
        default=True,
        verbose_name="包含图表",
        help_text="是否包含数据图表"
    )

    language = models.CharField(
        max_length=10,
        choices=[
            ('zh', '中文'),
            ('en', '英文')
        ],
        default='zh',
        verbose_name="语言",
        help_text="PPT语言"
    )

    # 生成状态
    GENERATION_STATUS = [
        ('pending', '待生成'),
        ('processing', '生成中'),
        ('completed', '生成完成'),
        ('failed', '生成失败')
    ]

    status = models.CharField(
        max_length=20,
        choices=GENERATION_STATUS,
        default='pending',
        verbose_name="生成状态",
        help_text="PPT生成状态"
    )

    # 统计信息
    view_count = models.IntegerField(
        default=0,
        verbose_name="查看次数",
        help_text="PPT查看次数"
    )

    download_count = models.IntegerField(
        default=0,
        verbose_name="下载次数",
        help_text="PPT下载次数"
    )

    # 分享设置
    is_public = models.BooleanField(
        default=False,
        verbose_name="公开分享",
        help_text="是否允许公开分享"
    )

    share_code = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        unique=True,
        verbose_name="分享码",
        help_text="分享唯一标识码"
    )

    # 标签和分类
    tags = models.JSONField(
        blank=True,
        null=True,
        verbose_name="标签",
        help_text="PPT标签列表(JSON格式)"
    )

    category = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="分类",
        help_text="PPT分类"
    )

    # 额外信息
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name="错误信息",
        help_text="生成失败时的错误信息"
    )

    preview_data = models.JSONField(
        blank=True,
        null=True,
        verbose_name="预览数据",
        help_text="PPT预览信息(JSON格式)"
    )

    def generate_share_code(self):
        """生成分享码"""
        import hashlib
        import random
        code = hashlib.md5(f"{self.id}{random.random()}".encode()).hexdigest()[:16]
        return code

    def save(self, *args, **kwargs):
        # 保存前生成分享码
        if not self.share_code:
            self.share_code = self.generate_share_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        db_table = table_prefix + "pptfile"
        verbose_name = "PPT文件管理"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)