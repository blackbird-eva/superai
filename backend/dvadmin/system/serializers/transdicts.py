# -*- coding: utf-8 -*-
"""
翻译字典和文档翻译序列化器
"""
from rest_framework import serializers
from dvadmin.system.models import Transdicts, Docxfile, PPTFile
from dvadmin.utils.serializers import CustomModelSerializer


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


# ============================================
# Docxfile 序列化器
# ============================================

class DocxfileSerializer(CustomModelSerializer):
    """
    Docxfile 完整序列化器
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Docxfile
        fields = [
            "id", "original_name", "file_path", "file_size", "type", "type_display",
            "about_text", "transtask", "graphtask", "share", "userversion",
            "status", "status_display", "paragraph_count", "word_count", "page_count",
            "source_language", "target_language", "processing_time", "error_message",
            "translated_path", "translated_filename", "create_datetime", "update_datetime"
        ]
        read_only_fields = ["id", "create_datetime", "update_datetime", "file_size"]


class DocxfileUploadSerializer(CustomModelSerializer):
    """
    Docxfile 上传专用序列化器
    """
    
    class Meta:
        model = Docxfile
        fields = [
            "original_name", "file_path", "type", "about_text", 
            "transtask", "graphtask", "share", "userversion",
            "source_language", "target_language"
        ]


class DocxfileTranslateSerializer(CustomModelSerializer):
    """
    Docxfile 翻译处理专用序列化器
    """
    
    class Meta:
        model = Docxfile
        fields = ['id', 'transtask', 'graphtask', 'source_language', 'target_language']


class DocxfileCreateUpdateSerializer(CustomModelSerializer):
    """
    Docxfile 创建/更新序列化器
    """
    
    def validate_original_name(self, value):
        """
        验证文件名
        """
        if not value or not value.strip():
            raise serializers.ValidationError("文件名不能为空")
        return value.strip()
    
    def validate_about_text(self, value):
        """
        验证文档简介长度
        """
        if value and len(value) > 1000:
            raise serializers.ValidationError("文档简介不能超过1000个字符")
        return value

    class Meta:
        model = Docxfile
        fields = [
            "original_name", "file_path", "type", "about_text",
            "transtask", "graphtask", "share", "userversion",
            "source_language", "target_language"
        ]


# ============================================
# 视图集
# ============================================

from dvadmin.utils.viewset import CustomModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.conf import settings
import os


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


class DocxfileViewSet(CustomModelViewSet):
    """
    Docxfile 文档翻译管理接口
    """
    queryset = Docxfile.objects.all()
    serializer_class = DocxfileSerializer
    create_serializer_class = DocxfileCreateUpdateSerializer
    update_serializer_class = DocxfileCreateUpdateSerializer
    extra_filter_class = []
    search_fields = ['original_name', 'about_text']

    def get_queryset(self):
        queryset = self.queryset
        params = self.request.query_params
        
        # 按状态筛选
        status = params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
            
        # 按文档类型筛选
        type = params.get('type', None)
        if type:
            queryset = queryset.filter(type=type)
            
        # 按功能开关筛选
        transtask = params.get('transtask', None)
        if transtask is not None:
            queryset = queryset.filter(transtask=transtask.lower() == 'true')
            
        graphtask = params.get('graphtask', None)
        if graphtask is not None:
            queryset = queryset.filter(graphtask=graphtask.lower() == 'true')
            
        share = params.get('share', None)
        if share is not None:
            queryset = queryset.filter(share=share.lower() == 'true')

        return queryset

    @action(methods=['post'], detail=False, url_path='upload')
    def upload_document(self, request):
        """
        文档上传接口
        """
        serializer = DocxfileUploadSerializer(data=request.data)
        if serializer.is_valid():
            # 保存文档记录
            docxfile = serializer.save(
                status='uploaded',
                file_size=request.data.get('file_path').size if request.data.get('file_path') else 0
            )
            
            return Response({
                'code': 200,
                'msg': '上传成功',
                'data': {
                    'id': docxfile.id,
                    'original_name': docxfile.original_name,
                    'type': docxfile.type,
                    'status': docxfile.status
                }
            })
        else:
            return Response({
                'code': 400,
                'msg': '上传失败',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True, url_path='translate')
    def translate_document(self, request, pk=None):
        """
        文档翻译接口
        """
        try:
            docxfile = self.get_object()
            
            # 检查是否需要翻译
            if not docxfile.transtask:
                return Response({
                    'code': 400,
                    'msg': '该文档未启用翻译任务'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 更新状态为处理中
            docxfile.status = 'processing'
            docxfile.save()
            
            # TODO: 这里添加实际的文档翻译逻辑
            # 包括：解析文档、调用翻译服务、生成翻译后的文档
            
            # 模拟翻译完成
            docxfile.status = 'completed'
            docxfile.paragraph_count = 10  # 模拟段落数
            docxfile.word_count = 1000     # 模拟字数
            docxfile.processing_time = 5.5  # 模拟处理时间
            docxfile.save()
            
            return Response({
                'code': 200,
                'msg': '翻译完成',
                'data': {
                    'id': docxfile.id,
                    'status': docxfile.status,
                    'paragraph_count': docxfile.paragraph_count,
                    'word_count': docxfile.word_count,
                    'processing_time': docxfile.processing_time
                }
            })
            
        except Exception as e:
            # 更新状态为失败
            if 'docxfile' in locals():
                docxfile.status = 'failed'
                docxfile.error_message = str(e)
                docxfile.save()
            
            return Response({
                'code': 500,
                'msg': f'翻译失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['get'], detail=True, url_path='download')
    def download_document(self, request, pk=None):
        """
        文档下载接口
        """
        try:
            docxfile = self.get_object()
            
            if not docxfile.translated_path:
                return Response({
                    'code': 404,
                    'msg': '翻译后的文档不存在'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 构建文件路径
            file_path = os.path.join(settings.MEDIA_ROOT, docxfile.translated_path)
            
            if not os.path.exists(file_path):
                return Response({
                    'code': 404,
                    'msg': '文件不存在'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 返回文件响应
            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{docxfile.translated_filename}"'
                return response
                
        except Exception as e:
            return Response({
                'code': 500,
                'msg': f'下载失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['get'], detail=False, url_path='stats')
    def statistics(self, request):
        """
        获取文档翻译统计信息
        """
        total = Docxfile.objects.count()
        completed = Docxfile.objects.filter(status='completed').count()
        processing = Docxfile.objects.filter(status='processing').count()
        failed = Docxfile.objects.filter(status='failed').count()
        
        # 按类型统计
        type_stats = {}
        for choice in Docxfile.DOCUMENT_TYPES:
            type_stats[choice[0]] = Docxfile.objects.filter(type=choice[0]).count()
        
        return Response({
            'code': 200,
            'msg': '获取成功',
            'data': {
                'total': total,
                'completed': completed,
                'processing': processing,
                'failed': failed,
                'type_statistics': type_stats
            }
        })


# ============================================
# PPTFile 序列化器
# ============================================

class PPTFileSerializer(CustomModelSerializer):
    """
    PPTFile 完整序列化器
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    source_type_display = serializers.CharField(source='get_source_type_display', read_only=True)
    theme_display = serializers.CharField(source='get_theme_display', read_only=True)
    language_display = serializers.CharField(source='get_language_display', read_only=True)
    file_url = serializers.SerializerMethodField()

    def get_file_url(self, obj):
        """获取文件下载URL"""
        if obj.file_path:
            return f'/api/system/pptfile/{obj.id}/download/'
        return None

    class Meta:
        model = PPTFile
        fields = [
            "id", "title", "original_name", "file_path", "file_url", "file_size",
            "source_type", "source_type_display", "source_url",
            "content_text", "content_summary",
            "theme", "theme_display", "slide_count", "include_charts", "language", "language_display",
            "status", "status_display",
            "view_count", "download_count",
            "is_public", "share_code",
            "tags", "category",
            "error_message", "preview_data",
            "create_datetime", "update_datetime"
        ]
        read_only_fields = [
            "id", "create_datetime", "update_datetime",
            "file_size", "status", "share_code", "view_count", "download_count"
        ]


class PPTFileCreateSerializer(CustomModelSerializer):
    """
    PPTFile 创建序列化器
    """

    def validate_title(self, value):
        """验证标题"""
        if not value or not value.strip():
            raise serializers.ValidationError("PPT标题不能为空")
        if len(value) > 500:
            raise serializers.ValidationError("PPT标题不能超过500个字符")
        return value.strip()

    def validate_content_text(self, value):
        """验证内容文本长度"""
        if value and len(value) > 50000:
            raise serializers.ValidationError("内容文本不能超过50000个字符")
        return value

    def validate_content_summary(self, value):
        """验证内容摘要长度"""
        if value and len(value) > 2000:
            raise serializers.ValidationError("内容摘要不能超过2000个字符")
        return value

    def validate_slide_count(self, value):
        """验证幻灯片数量"""
        if not (5 <= value <= 30):
            raise serializers.ValidationError("幻灯片数量必须在5-30之间")
        return value

    def validate_source_url(self, value):
        """验证URL"""
        if value:
            from urllib.parse import urlparse
            try:
                result = urlparse(value)
                if not all([result.scheme, result.netloc]):
                    raise serializers.ValidationError("URL格式不正确")
            except Exception:
                raise serializers.ValidationError("URL格式不正确")
        return value

    class Meta:
        model = PPTFile
        fields = [
            "title", "original_name",
            "source_type", "source_url",
            "content_text", "content_summary",
            "theme", "slide_count", "include_charts", "language",
            "tags", "category", "is_public"
        ]


class PPTFileUpdateSerializer(CustomModelSerializer):
    """
    PPTFile 更新序列化器
    """

    def validate_title(self, value):
        """验证标题"""
        if not value or not value.strip():
            raise serializers.ValidationError("PPT标题不能为空")
        if len(value) > 500:
            raise serializers.ValidationError("PPT标题不能超过500个字符")
        return value.strip()

    def validate_content_summary(self, value):
        """验证内容摘要长度"""
        if value and len(value) > 2000:
            raise serializers.ValidationError("内容摘要不能超过2000个字符")
        return value

    class Meta:
        model = PPTFile
        fields = [
            "title", "content_summary",
            "theme", "slide_count", "include_charts", "language",
            "tags", "category", "is_public"
        ]


class PPTFileListSerializer(CustomModelSerializer):
    """
    PPTFile 列表序列化器（精简版）
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    theme_display = serializers.CharField(source='get_theme_display', read_only=True)
    file_url = serializers.SerializerMethodField()

    def get_file_url(self, obj):
        """获取文件下载URL"""
        if obj.file_path:
            return f'/api/system/pptfile/{obj.id}/download/'
        return None

    class Meta:
        model = PPTFile
        fields = [
            "id", "title", "original_name", "file_url", "file_size",
            "theme", "theme_display", "slide_count",
            "status", "status_display",
            "view_count", "download_count", "is_public",
            "tags", "category",
            "create_datetime"
        ]
