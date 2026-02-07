# -*- coding: utf-8 -*-
"""
文件上传管理
Created on: 2026-02-03
"""
import logging
import os
import uuid
from datetime import datetime

from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from django.conf import settings
from django.http import HttpResponse

from dvadmin.utils.json_response import SuccessResponse, ErrorResponse
from dvadmin.system.models import Docxfile

# 导入Word文档处理模块
from .word_process import wordwork

logger = logging.getLogger(__name__)


class FileUploadView(APIView):
    """
    通用文件上传接口
    支持多种文件类型上传
    """
    authentication_classes = []
    permission_classes = []
    renderer_classes = [JSONRenderer]

    @staticmethod
    def str2bool(s):
        """
        将字符串转换为布尔值
        支持: 'true', '1', 'yes', 'y' -> True
             'false', '0', 'no', 'n' -> False
        """
        if isinstance(s, bool):
            return s
        if isinstance(s, str):
            return s.lower() in ('true', '1', 'yes', 'y')
        return bool(s)

    @staticmethod
    def safe_str(value):
        """
        安全地转换值为可 JSON 序列化的字符串
        处理 None、非 UTF-8 编码的字节等问题
        """
        if value is None:
            return ''
        try:
            # 尝试转换为字符串并确保是有效的 UTF-8
            if isinstance(value, bytes):
                # 如果是字节，尝试解码
                try:
                    return value.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果 UTF-8 解码失败，尝试其他编码
                    try:
                        return value.decode('gbk')
                    except:
                        return str(value, errors='ignore')
            elif isinstance(value, str):
                # 如果已经是字符串，确保它不包含无效的 UTF-8 序列
                try:
                    value.encode('utf-8')
                    return value
                except UnicodeEncodeError:
                    # 移除无效的字符
                    return value.encode('utf-8', errors='ignore').decode('utf-8')
            else:
                # 其他类型，直接转为字符串
                return str(value)
        except Exception as e:
            logger.warning(f"字符串转换失败: {value}, 错误: {str(e)}")
            return str(value) if value is not None else ''

    def post(self, request):
        """
        文件上传处理
        支持文件类型：docx, ppt, pptx, pdf, txt
        文件大小限制：50MB
        """
        try:
            file = request.FILES.get('file')
            if not file:
                return ErrorResponse(msg="请选择要上传的文件", code=400)

            # 验证文件类型
            allowed_types = ['docx', 'ppt', 'pptx', 'pdf', 'txt']
            file_ext = file.name.split('.')[-1].lower()
            if file_ext not in allowed_types:
                return ErrorResponse(
                    msg=f"不支持的文件类型，支持: {', '.join(allowed_types)}",
                    code=400
                )

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
                original_name=self.safe_str(file.name),
                file_path=file_path,
                file_size=file.size,
                type=file_ext,
                about_text=self.safe_str(request.data.get('about_text', '')),
                transtask=self.str2bool(request.data.get('transtask', 'true')),
                graphtask=self.str2bool(request.data.get('graphtask', 'false')),
                share=self.str2bool(request.data.get('share', 'false')),
                userversion=self.str2bool(request.data.get('userversion', 'true')),
                source_language=self.safe_str(request.data.get('source_lang', 'auto')),
                target_language=self.safe_str(request.data.get('target_lang', 'zh')),
                status='uploaded'
            )

            # 如果是Word文档且需要处理，则调用wordwork函数处理
            processed_file_path = None
            if file_ext == 'docx' and docxfile.transtask:
                try:
                    # 获取完整文件路径
                    full_input_path = os.path.join(settings.MEDIA_ROOT, file_path)
                    # 调用wordwork处理函数，传入源语言和目标语言
                    processed_full_path = wordwork(full_input_path, docxfile.source_language, docxfile.target_language)
                    # 获取相对路径
                    processed_file_path = os.path.relpath(processed_full_path, settings.MEDIA_ROOT)
                    logger.info(f"Word文档处理完成: {file.name} -> {os.path.basename(processed_full_path)}")
                except Exception as e:
                    logger.error(f"Word文档处理失败: {str(e)}")
                    # 如果处理失败，继续执行而不抛出异常

            logger.info(f"文件上传成功: {file.name} ({file.size} bytes)")

            # 准备响应数据
            response_data = {
                'id': int(docxfile.id),
                'original_name': self.safe_str(docxfile.original_name),
                'type': self.safe_str(docxfile.type),
                'type_display': self.safe_str(dict(Docxfile.DOCUMENT_TYPES).get(docxfile.type, '未知')),
                'file_size': int(docxfile.file_size),
                'file_path': file_path,  # 使用变量而不是模型字段
                'status': self.safe_str(docxfile.status),
                'transtask': bool(docxfile.transtask),
                'graphtask': bool(docxfile.graphtask),
                'share': bool(docxfile.share),
                'userversion': bool(docxfile.userversion),
                'about_text': self.safe_str(docxfile.about_text),
                'source_language': self.safe_str(docxfile.source_language),
                'target_language': self.safe_str(docxfile.target_language),
                'upload_time': docxfile.create_datetime.strftime('%Y-%m-%d %H:%M:%S') if docxfile.create_datetime else None
            }

            # 如果有处理过的文件，添加到响应数据中
            if processed_file_path:
                response_data['processed_file_path'] = processed_file_path
                response_data['processed_file_name'] = os.path.basename(processed_file_path)

            logger.info(f"准备返回响应数据，字段类型检查:")
            for key, value in response_data.items():
                value_str = str(value)
                if len(value_str) > 100:
                    value_str = value_str[:100] + '...'
                logger.info(f"  {key}: {type(value).__name__} = {value_str}")

            # 预先验证 JSON 序列化
            try:
                import json
                json.dumps(response_data, ensure_ascii=False)
                logger.info("JSON 序列化测试通过")
            except Exception as e:
                logger.error(f"JSON 序列化失败: {str(e)}")
                # 尝试找出问题字段
                for key, value in response_data.items():
                    try:
                        json.dumps(value, ensure_ascii=False)
                    except Exception as e2:
                        logger.error(f"  问题字段 {key}: {type(value).__name__} = {value}")
                        response_data[key] = str(value) if value is not None else ''

            return SuccessResponse(
                data=response_data,
                msg="文件上传成功"
            )

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            logger.error(f"文件上传失败: {str(e)}\n{error_detail}")
            return ErrorResponse(msg=f"上传失败: {str(e)}", code=500)


class FileDownloadView(APIView):
    """
    文件下载接口
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        """
        下载文件
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
                content = file.read()

                # 根据文件类型设置正确的 MIME 类型
                content_type_map = {
                    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                    'ppt': 'application/vnd.ms-powerpoint',
                    'pdf': 'application/pdf',
                    'txt': 'text/plain'
                }
                file_ext = file_path.split('.')[-1].lower()
                content_type = content_type_map.get(file_ext, 'application/octet-stream')

                response = HttpResponse(content, content_type=content_type)
                filename = os.path.basename(file_path)
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response

        except Exception as e:
            logger.error(f"文件下载失败: {str(e)}")
            return ErrorResponse(msg=f"下载失败: {str(e)}", code=500)