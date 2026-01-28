# -*- coding: utf-8 -*-

"""
翻译字典管理
Created on: 2026-01-27
"""
from rest_framework.permissions import AllowAny
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
import openpyxl
import os

from dvadmin.system.models import Transdicts
from dvadmin.utils.json_response import SuccessResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class TransdictsSerializer(CustomModelSerializer):
    """
    翻译字典-序列化器
    """
    pcate_display = serializers.CharField(source='get_pcate_display', read_only=True)

    class Meta:
        model = Transdicts
        fields = "__all__"
        read_only_fields = ["id"]


class TransdictsCreateUpdateSerializer(CustomModelSerializer):
    """
    翻译字典 创建/更新时的序列化器
    """

    def validate_cn(self, value):
        """
        验证中文词条
        """
        if not value or not value.strip():
            raise serializers.ValidationError("中文词条不能为空")
        return value.strip()

    def validate_en(self, value):
        """
        验证英文词条
        """
        if not value or not value.strip():
            raise serializers.ValidationError("英文词条不能为空")
        return value.strip()

    class Meta:
        model = Transdicts
        fields = '__all__'


class TransdictsViewSet(CustomModelViewSet):
    """
    翻译字典管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = Transdicts.objects.all()
    serializer_class = TransdictsSerializer
    create_serializer_class = TransdictsCreateUpdateSerializer
    update_serializer_class = TransdictsCreateUpdateSerializer
    extra_filter_class = []
    search_fields = ['cn', 'en']

    def get_queryset(self):
        queryset = self.queryset
        params = self.request.query_params

        # 按类别筛选
        pcate = params.get('pcate', None)
        if pcate:
            queryset = queryset.filter(pcate=pcate)

        return queryset

    def list(self, request, *args, **kwargs):
        """
        列表查询
        """
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        新增翻译字典
        """
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        更新翻译字典
        """
        return super().update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        单例查询
        """
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        删除翻译字典
        """
        return super().destroy(request, *args, **kwargs)


 

class GetTransdictsCategoriesView(APIView):
    """
    获取翻译字典分类列表
    """
    from dvadmin.system.models import Transdicts
    authentication_classes = []
    permission_classes = []
    renderer_classes = [JSONRenderer]

    def get(self, request):
        """
        获取所有分类选项
        """
        categories = [
            {'value': '通用', 'label': '通用'},
            {'value': '飞行', 'label': '飞行'},
            {'value': '行业', 'label': '行业'},
            {'value': '机械', 'label': '机械'},
            {'value': '维保', 'label': '维保'},
            {'value': '文档', 'label': '文档'},
            {'value': '其他', 'label': '其他'},
        ]
        return SuccessResponse(data=categories, msg="获取成功")


class MyTaskHelloView(APIView):
    """
    我的任务 - Hello 测试接口
    """
    authentication_classes = []
    permission_classes = []
    renderer_classes = [JSONRenderer]

    def get(self, request):
        """
        返回 Hello 信息
        """
        return SuccessResponse(data="hello", msg="成功")


class ReadExcelView(APIView):
    """
    读取 Excel 文件前两列内容并导入到数据库
    """
    authentication_classes = []
    permission_classes = []
    renderer_classes = [JSONRenderer]

    def get(self, request):
        """
        读取 data.xlsx 文件的前两列
        """
        # Excel 文件路径
        excel_file = os.path.join(os.path.dirname(__file__), '../../../data.xlsx')

        try:
            # 加载 Excel 文件
            workbook = openpyxl.load_workbook(excel_file)

            # 获取第一个工作表
            sheet = workbook.active

            # 读取前两列数据
            data = []
            for row in sheet.iter_rows(min_row=1, values_only=True):
                if len(row) >= 2 and row[0] and row[1]:  # 确保前两列都有值
                    data.append({
                        'cn': str(row[0]).strip(),
                        'en': str(row[1]).strip()
                    })
            data = data[1:]  # 跳过表头

            return SuccessResponse(data=data, msg=f"读取成功，共 {len(data)} 条数据")

        except FileNotFoundError:
            return SuccessResponse(data=[], msg="Excel 文件不存在")
        except Exception as e:
            return SuccessResponse(data=[], msg=f"读取失败: {str(e)}")

    def post(self, request):
        """
        导入 Excel 数据到数据库（对 cn 字段查重）
        """
        # Excel 文件路径
        return "" 
        
        excel_file = os.path.join(os.path.dirname(__file__), '../../../data.xlsx')

        try:
            # 加载 Excel 文件
            workbook = openpyxl.load_workbook(excel_file)

            # 获取第一个工作表
            sheet = workbook.active

            # 读取前两列数据
            data = []
            for row in sheet.iter_rows(min_row=1, values_only=True):
                if len(row) >= 2 and row[0] and row[1]:  # 确保前两列都有值
                    data.append({
                        'cn': str(row[0]).strip(),
                        'en': str(row[1]).strip()
                    })
            data = data[1:]  # 跳过表头

            # 导入数据到数据库
            success_count = 0
            skip_count = 0
            error_count = 0
            error_list = []

            for item in data:
                cn = item['cn']
                en = item['en']

                try:
                    # 检查 cn 是否已存在
                    if Transdicts.objects.filter(cn=cn).exists():
                        skip_count += 1
                        error_list.append(f"{cn} - 已存在，跳过")
                        continue

                    # 创建新记录
                    Transdicts.objects.create(
                        cn=cn,
                        en=en,
                        pcate='通用'  # 默认类别
                    )
                    success_count += 1

                except Exception as e:
                    error_count += 1
                    error_list.append(f"{cn} - 错误: {str(e)}")

            result = {
                'total': len(data),
                'success': success_count,
                'skip': skip_count,
                'error': error_count,
                'errors': error_list
            }

            return SuccessResponse(data=result, msg=f"导入完成！成功 {success_count} 条，跳过 {skip_count} 条，失败 {error_count} 条")

        except FileNotFoundError:
            return SuccessResponse(data={}, msg="Excel 文件不存在")
        except Exception as e:
            return SuccessResponse(data={}, msg=f"导入失败: {str(e)}")
