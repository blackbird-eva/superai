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




class PPTFileViewSet(CustomModelViewSet):
    """
    PPT文件管理接口 - 完整的CRUD操作
    list: 查询列表
    create: 新增PPT记录
    retrieve: 查询单个详情
    update: 更新PPT记录
    destroy: 删除PPT记录
    """
    queryset = PPTFile.objects.all()
    serializer_class = PPTFileSerializer
    list_serializer_class = PPTFileListSerializer
    create_serializer_class = PPTFileCreateSerializer
    update_serializer_class = PPTFileUpdateSerializer
    extra_filter_class = []
    search_fields = ['title', 'content_text', 'content_summary']

    def get_queryset(self):
        """自定义查询集"""
        queryset = self.queryset
        params = self.request.query_params

        # 按状态筛选
        status = params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)

        # 按主题筛选
        theme = params.get('theme', None)
        if theme:
            queryset = queryset.filter(theme=theme)

        # 按来源类型筛选
        source_type = params.get('source_type', None)
        if source_type:
            queryset = queryset.filter(source_type=source_type)

        # 按分类筛选
        category = params.get('category', None)
        if category:
            queryset = queryset.filter(category__icontains=category)

        # 按是否公开筛选
        is_public = params.get('is_public', None)
        if is_public is not None:
            queryset = queryset.filter(is_public=is_public.lower() == 'true')

        return queryset

    def list(self, request, *args, **kwargs):
        """
        查询PPT列表
        支持分页、搜索、排序、筛选
        """
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        新增PPT记录
        接收网页内容或文件信息，创建PPT生成任务
        """
        # 使用创建序列化器验证数据
        serializer = self.create_serializer_class(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=f"验证失败: {serializer.errors}", code=400)

        try:
            # 创建PPT记录，初始状态为待生成
            pptfile = serializer.save(
                status='pending',
                view_count=0,
                download_count=0
            )

            # 调用PPT生成逻辑
            pptm = genPPT()
            ppt_result = pptm.create_pptx_file(
                text_content=pptfile.content_text or '',
                theme=pptfile.theme,
                slide_count=pptfile.slide_count,
                include_charts=pptfile.include_charts,
                language=pptfile.language,
                paragraphs=self.parse_text(pptfile.content_text or '')
            )

            # 更新PPT文件路径和大小
            if ppt_result['file_path']:
                # 构建完整文件路径
                full_file_path = os.path.join(settings.MEDIA_ROOT, ppt_result['file_path'])

                # 获取文件大小
                if os.path.exists(full_file_path):
                    file_size = os.path.getsize(full_file_path)
                else:
                    file_size = 0

                pptfile.file_path = ppt_result['file_path']
                pptfile.file_size = file_size
                pptfile.status = 'completed'

                # 保存预览数据
                pptfile.preview_data = self.generate_ppt_preview_data(
                    text_content=pptfile.content_text or '',
                    theme=pptfile.theme,
                    slide_count=pptfile.slide_count,
                    include_charts=pptfile.include_charts,
                    language=pptfile.language,
                    paragraphs=self.parse_text(pptfile.content_text or '')
                )

            pptfile.save()

            # 返回成功响应
            return SuccessResponse(
                data=PPTFileSerializer(pptfile).data,
                msg="PPT创建成功"
            )

        except Exception as e:
            # 更新状态为失败
            if 'pptfile' in locals():
                pptfile.status = 'failed'
                pptfile.error_message = str(e)
                pptfile.save()

            return ErrorResponse(msg=f"创建失败: {str(e)}", code=500)

    def retrieve(self, request, *args, **kwargs):
        """
        查询单个PPT详情
        同时增加查看次数
        """
        instance = self.get_object()

        # 增加查看次数
        instance.view_count += 1
        instance.save(update_fields=['view_count'])

        serializer = self.get_serializer(instance)
        return SuccessResponse(data=serializer.data, msg="查询成功")

    def update(self, request, *args, **kwargs):
        """
        更新PPT记录
        允许修改标题、主题、标签、分类等信息
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # 检查是否允许修改（已完成的PPT不允许修改生成参数）
        if instance.status == 'processing':
            return ErrorResponse(msg="PPT正在生成中，无法修改", code=400)

        serializer = self.update_serializer_class(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            return ErrorResponse(msg=f"验证失败: {serializer.errors}", code=400)

        serializer.save()

        return SuccessResponse(data=PPTFileSerializer(instance).data, msg="更新成功")

    def destroy(self, request, *args, **kwargs):
        """
        删除PPT记录
        同时删除关联的文件
        """
        instance = self.get_object()

        # 删除文件
        if instance.file_path:
            full_file_path = os.path.join(settings.MEDIA_ROOT, instance.file_path.name)
            if os.path.exists(full_file_path):
                try:
                    os.remove(full_file_path)
                except Exception as e:
                    # 文件删除失败不影响记录删除
                    pass

        # 删除记录
        self.perform_destroy(instance)

        return SuccessResponse(data={}, msg="删除成功")

    @action(methods=['get'], detail=True, url_path='download')
    def download(self, request, pk=None):
        """
        下载PPT文件
        同时增加下载次数
        """
        try:
            pptfile = self.get_object()

            # 检查文件是否存在
            if not pptfile.file_path or not pptfile.file_path.name:
                return ErrorResponse(msg="PPT文件不存在", code=404)

            # 构建完整文件路径
            full_file_path = os.path.join(settings.MEDIA_ROOT, pptfile.file_path.name)

            if not os.path.exists(full_file_path):
                return ErrorResponse(msg="文件不存在", code=404)

            # 增加下载次数
            pptfile.download_count += 1
            pptfile.save(update_fields=['download_count'])

            # 返回文件
            with open(full_file_path, 'rb') as file:
                response = HttpResponse(
                    file.read(),
                    content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation'
                )
                filename = pptfile.original_name or f"{pptfile.title}.pptx"
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response

        except Exception as e:
            return ErrorResponse(msg=f"下载失败: {str(e)}", code=500)

    @action(methods=['post'], detail=True, url_path='share')
    def share(self, request, pk=None):
        """
        生成或更新分享链接
        """
        try:
            pptfile = self.get_object()

            # 设置为公开
            pptfile.is_public = True

            # 生成新的分享码
            pptfile.share_code = pptfile.generate_share_code()
            pptfile.save(update_fields=['is_public', 'share_code'])

            # 返回分享链接
            share_url = request.build_absolute_uri(f'/api/system/pptfile/{pptfile.id}/share/{pptfile.share_code}/')

            return SuccessResponse(
                data={
                    'share_code': pptfile.share_code,
                    'share_url': share_url
                },
                msg="分享链接生成成功"
            )

        except Exception as e:
            return ErrorResponse(msg=f"生成分享链接失败: {str(e)}", code=500)

    @action(methods=['get'], detail=False, url_path='stats')
    def statistics(self, request):
        """
        获取PPT统计信息
        """
        total = PPTFile.objects.count()
        completed = PPTFile.objects.filter(status='completed').count()
        pending = PPTFile.objects.filter(status='pending').count()
        processing = PPTFile.objects.filter(status='processing').count()
        failed = PPTFile.objects.filter(status='failed').count()

        # 按主题统计
        theme_stats = {}
        for choice in PPTFile._meta.get_field('theme').choices:
            theme_stats[choice[0]] = PPTFile.objects.filter(theme=choice[0]).count()

        # 按来源类型统计
        source_type_stats = {}
        for choice in PPTFile._meta.get_field('source_type').choices:
            source_type_stats[choice[0]] = PPTFile.objects.filter(source_type=choice[0]).count()

        return SuccessResponse(
            data={
                'total': total,
                'completed': completed,
                'pending': pending,
                'processing': processing,
                'failed': failed,
                'theme_statistics': theme_stats,
                'source_type_statistics': source_type_stats
            },
            msg="获取统计信息成功"
        )

    @action(methods=['get'], detail=True, url_path='preview')
    def preview(self, request, pk=None):
        """
        获取PPT预览数据
        """
        try:
            pptfile = self.get_object()

            return SuccessResponse(
                data=pptfile.preview_data or {},
                msg="获取预览数据成功"
            )

        except Exception as e:
            return ErrorResponse(msg=f"获取预览失败: {str(e)}", code=500)


