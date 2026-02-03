# -*- coding: utf-8 -*-
"""
翻译字典管理
Created on: 2026-01-27
"""
from rest_framework.permissions import AllowAny
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import action
import openpyxl
import os
import uuid
import re
from datetime import datetime

from dvadmin.system.models import Transdicts, Docxfile, PPTFile
from dvadmin.system.serializers.transdicts import (
    DocxfileSerializer, DocxfileUploadSerializer,
    PPTFileSerializer, PPTFileCreateSerializer,
    PPTFileUpdateSerializer, PPTFileListSerializer
)
from dvadmin.utils.json_response import SuccessResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from django.http import HttpResponse
from django.conf import settings

from .genppt import genPPT

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


class TranslateView(APIView):
    """
    文本翻译接口
    """
    authentication_classes = []
    permission_classes = []
    renderer_classes = [JSONRenderer]

    def post(self, request):
        """
        执行翻译
        """
        text = request.data.get('text', '')
        source_lang = request.data.get('source_lang', 'auto')
        target_lang = request.data.get('target_lang', 'en')

        if not text:
            return SuccessResponse(data={}, msg="请输入需要翻译的文本")

        try:
            # 如果源语言是自动检测，尝试检测语言
            if source_lang == 'auto':
                detected_lang = self.detect_language(text)
                source_lang = detected_lang

            # 尝试从数据库中查找翻译
            translated_text = self.translate_from_db(text, source_lang, target_lang)

            # 如果数据库中没有找到，返回原文（可以根据需求集成其他翻译服务）
            if not translated_text:
                translated_text = f"[翻译结果] {text}"

            result = {
                'source_text': text,
                'translated_text': translated_text,
                'source_lang': source_lang,
                'target_lang': target_lang
            }

            return SuccessResponse(data=result, msg="翻译成功")

        except Exception as e:
            return SuccessResponse(data={}, msg=f"翻译失败: {str(e)}")

    def detect_language(self, text):
        """
        简单的语言检测
        """
        text = text.lower()
        if any('\u4e00' <= char <= '\u9fa5' for char in text):
            return 'zh'
        elif any('\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff' for char in text):
            return 'ja'
        elif any('\uac00' <= char <= '\ud7af' for char in text):
            return 'ko'
        else:
            return 'en'

    def translate_from_db(self, text, source_lang, target_lang):
        """
        从翻译字典中查找翻译
        """
        try:
            # 根据源语言查找对应的字段
            if source_lang == 'zh':
                transdict = Transdicts.objects.filter(cn=text).first()
                if transdict:
                    # 根据目标语言返回对应字段
                    if target_lang == 'en':
                        return transdict.en
                    # 可以添加更多语言的字段
            elif source_lang == 'en':
                transdict = Transdicts.objects.filter(en=text).first()
                if transdict and target_lang == 'zh':
                    return transdict.cn

            # 如果没有找到完全匹配，尝试包含匹配
            if source_lang == 'zh':
                transdict = Transdicts.objects.filter(cn__icontains=text).first()
                if transdict and target_lang == 'en':
                    return transdict.en
            elif source_lang == 'en':
                transdict = Transdicts.objects.filter(en__icontains=text).first()
                if transdict and target_lang == 'zh':
                    return transdict.cn

            return None

        except Exception as e:
            print(f"翻译查询错误: {str(e)}")
            return None


# =============================================================================
# 文档翻译相关 API 视图
# =============================================================================

class DocumentUploadView(APIView):
    """
    文档上传接口
    """
    authentication_classes = []
    permission_classes = []
    renderer_classes = [JSONRenderer]

    def post(self, request):
        """
        上传文档
        """
        try:
            file = request.FILES.get('file')
            if not file:
                return ErrorResponse(msg="请选择要上传的文件", code=400)
            
            # 验证文件类型
            allowed_types = ['docx', 'ppt', 'pptx', 'pdf', 'txt']
            file_ext = file.name.split('.')[-1].lower()
            if file_ext not in allowed_types:
                return ErrorResponse(msg=f"不支持的文件类型，支持: {', '.join(allowed_types)}", code=400)
            
            # 验证文件大小 (50MB)
            if file.size > 50 * 1024 * 1024:
                return ErrorResponse(msg="文件大小不能超过50MB", code=400)
            
            # 生成唯一文件名
            unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
            date_path = datetime.now().strftime('%Y/%m/%d')
            file_path = f"docxfile/{date_path}/{unique_filename}"
            
            # 确保目录存在
            full_dir_path = os.path.join(settings.MEDIA_ROOT, f"docxfile/{date_path}")
            os.makedirs(full_dir_path, exist_ok=True)
            
            # 保存文件
            full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)
            with open(full_file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            
            # 创建 Docxfile 记录
            docxfile = Docxfile.objects.create(
                original_name=file.name,
                file_path=file_path,
                file_size=file.size,
                type=file_ext,
                about_text=request.data.get('about_text', ''),
                transtask=request.data.get('transtask', True),
                graphtask=request.data.get('graphtask', False),
                share=request.data.get('share', False),
                userversion=request.data.get('userversion', True),
                source_language=request.data.get('source_lang', 'auto'),
                target_language=request.data.get('target_lang', 'zh'),
                status='uploaded'
            )
            
            return SuccessResponse(
                data={
                    'id': docxfile.id,
                    'original_name': docxfile.original_name,
                    'type': docxfile.type,
                    'type_display': dict(Docxfile.DOCUMENT_TYPES).get(docxfile.type, '未知'),
                    'file_size': docxfile.file_size,
                    'status': docxfile.status,
                    'transtask': docxfile.transtask,
                    'graphtask': docxfile.graphtask,
                    'share': docxfile.share,
                    'userversion': docxfile.userversion,
                    'about_text': docxfile.about_text,
                    'source_language': docxfile.source_language,
                    'target_language': docxfile.target_language
                },
                msg="上传成功"
            )
            
        except Exception as e:
            return ErrorResponse(msg=f"上传失败: {str(e)}", code=500)


class DocumentTranslateView(APIView):
    """
    文档翻译接口
    """
    authentication_classes = []
    permission_classes = []
    renderer_classes = [JSONRenderer]

    def post(self, request):
        """
        执行文档翻译
        """
        try:
            file = request.FILES.get('file')
            source_lang = request.data.get('source_lang', 'auto')
            target_lang = request.data.get('target_lang', 'zh')
            
            if not file:
                return ErrorResponse(msg="请选择要翻译的文件", code=400)
            
            # 验证文件类型
            allowed_types = ['docx']
            file_ext = file.name.split('.')[-1].lower()
            if file_ext not in allowed_types:
                return ErrorResponse(msg=f"当前仅支持DOCX格式文档翻译", code=400)
            
            # 检查 python-docx 是否可用
            try:
                import docx
                need_install = False
            except ImportError:
                need_install = True
                return SuccessResponse(
                    data={'need_install': True},
                    msg="需要安装 python-docx 库: pip install python-docx"
                )
            
            # 保存上传的文件
            unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
            date_path = datetime.now().strftime('%Y/%m/%d')
            upload_path = f"docxfile/{date_path}/{unique_filename}"
            
            full_dir_path = os.path.join(settings.MEDIA_ROOT, f"docxfile/{date_path}")
            os.makedirs(full_dir_path, exist_ok=True)
            
            full_file_path = os.path.join(settings.MEDIA_ROOT, upload_path)
            with open(full_file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            
            # 解析文档并翻译
            from docx import Document
            doc = Document(full_file_path)
            
            translated_paragraphs = []
            preview_data = []
            
            for i, paragraph in enumerate(doc.paragraphs):
                text = paragraph.text.strip()
                if text:
                    # 这里应该调用翻译服务，现在只是模拟
                    translated_text = f"[译文] {text}"
                    translated_paragraphs.append(translated_text)
                    
                    # 收集预览数据（前5段）
                    if len(preview_data) < 5:
                        preview_data.append({
                            'original': text,
                            'translated': translated_text
                        })
            
            # 创建翻译后的文档
            translated_filename = f"translated_{unique_filename}"
            translated_path = f"docxfile/{date_path}/{translated_filename}"
            translated_full_path = os.path.join(settings.MEDIA_ROOT, translated_path)
            
            # 创建新文档
            translated_doc = Document()
            for para in translated_paragraphs:
                translated_doc.add_paragraph(para)
            
            translated_doc.save(translated_full_path)
            
            # 计算统计信息
            paragraph_count = len([p for p in doc.paragraphs if p.text.strip()])
            word_count = sum(len(p.text.split()) for p in doc.paragraphs if p.text.strip())
            
            result = {
                'paragraph_count': paragraph_count,
                'word_count': word_count,
                'translated_path': translated_path,
                'translated_filename': translated_filename,
                'preview': preview_data,
                'source_lang': source_lang,
                'target_lang': target_lang,
                'need_install': False
            }
            
            return SuccessResponse(data=result, msg="翻译完成")
            
        except Exception as e:
            return ErrorResponse(msg=f"翻译失败: {str(e)}", code=500)


class DocumentDownloadView(APIView):
    """
    文档下载接口
    """
    authentication_classes = []
    permission_classes = []
    renderer_classes = [JSONRenderer]

    def get(self, request):
        """
        下载翻译后的文档
        """
        try:
            file_path = request.GET.get('file_path')
            if not file_path:
                return ErrorResponse(msg="文件路径不能为空", code=400)
            
            # 安全检查：确保文件路径在允许的目录下
            if not file_path.startswith('docxfile/'):
                return ErrorResponse(msg="无效的文件路径", code=400)
            
            full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)
            
            if not os.path.exists(full_file_path):
                return ErrorResponse(msg="文件不存在", code=404)
            
            # 返回文件
            with open(full_file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                filename = os.path.basename(file_path)
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
                
        except Exception as e:
            return ErrorResponse(msg=f"下载失败: {str(e)}", code=500)

