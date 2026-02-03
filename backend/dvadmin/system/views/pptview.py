# -*- coding: utf-8 -*-
"""
PPT文件上传和生成视图
独立文件存放PPT上传生成相关视图类
"""
import os
import uuid
import logging
from datetime import datetime

from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer

from dvadmin.utils.json_response import SuccessResponse, ErrorResponse
from django.conf import settings

logger = logging.getLogger(__name__)


class UploadFilesAndGeneratePPTView(APIView):
    """
    多文件上传并生成PPT接口
    """
    authentication_classes = []
    permission_classes = []
    renderer_classes = [JSONRenderer]

    def post(self, request):
        """
        上传多个文件并根据文件内容生成PPT
        """
        try:
            # 获取上传的文件列表
            files = request.FILES.getlist('files')
            if not files:
                return ErrorResponse(msg="请选择要上传的文件", code=400)

            # 获取生成选项
            theme = request.data.get('theme', 'business')
            slide_count = int(request.data.get('slide_count', 10))
            include_charts = request.data.get('include_charts', True)
            language = request.data.get('language', 'zh')

            # 验证幻灯片数量
            if slide_count < 5 or slide_count > 30:
                return ErrorResponse(msg="幻灯片数量必须在5-30之间", code=400)

            # 检查 python-pptx 是否可用
            try:
                from pptx import Presentation
                from pptx.util import Pt, Inches
                from pptx.enum.text import PP_ALIGN
            except ImportError:
                return SuccessResponse(
                    data={'need_install': True},
                    msg="需要安装 python-pptx 库: pip install python-pptx"
                )

            # 读取所有文本文件内容并合并
            combined_text = ""
            processed_files = []
            
            for file in files:
                # 检查文件类型
                file_ext = os.path.splitext(file.name)[1].lower()
                if file_ext not in ['.txt', '.md', '.rst', '.docx']:
                    continue  # 跳过非文本文件
                
                try:
                    # 读取文件内容
                    file_content = file.read().decode('utf-8')
                    combined_text += f"\n\n=== 文件: {file.name} ===\n{file_content}"
                    processed_files.append({
                        'name': file.name,
                        'size': file.size,
                        'type': file_ext
                    })
                except Exception as e:
                    logger.warning(f"读取文件 {file.name} 失败: {str(e)}")
                    continue

            if not combined_text.strip():
                return ErrorResponse(msg="没有有效的文本文件内容可供生成PPT", code=400)

            # 解析合并后的文本内容
            paragraphs = self.parse_text(combined_text)

            # 生成PPT文件
            ppt_file_info = self.create_pptx_file(combined_text, theme, slide_count, include_charts, language, paragraphs)

            # 生成预览数据
            ppt_data = self.generate_ppt_preview_data(combined_text, theme, slide_count, include_charts, language, paragraphs)

            # 合并文件信息和预览数据
            ppt_data.update({
                'ppt_file_path': ppt_file_info['file_path'],
                'ppt_file_name': ppt_file_info['file_name'],
                'ppt_download_url': ppt_file_info['download_url'],
                'processed_files': processed_files,
                'total_files': len(processed_files),
                'combined_text_length': len(combined_text)
            })

            return SuccessResponse(data=ppt_data, msg="PPT生成成功")

        except Exception as e:
            import traceback
            traceback.print_exc()
            return ErrorResponse(msg=f"生成失败: {str(e)}", code=500)

    def parse_text(self, text_content):
        """
        解析文本内容，提取段落
        """
        # 按双换行分割段落
        paragraphs = [p.strip() for p in text_content.split('\n\n') if p.strip()]
        
        # 过滤掉太短的段落（少于10个字符）
        paragraphs = [p for p in paragraphs if len(p) >= 10]
        
        # 如果段落太多，截取前20个
        if len(paragraphs) > 20:
            paragraphs = paragraphs[:20]
            
        return paragraphs

    def generate_ppt_preview_data(self, text_content, theme, slide_count, include_charts, language, paragraphs):
        """
        生成PPT预览数据
        """
        # 简单的预览数据结构
        preview_data = {
            'theme': theme,
            'slide_count': slide_count,
            'include_charts': include_charts,
            'language': language,
            'estimated_slides': min(len(paragraphs) + 2, slide_count),  # 封面 + 内容页 + 结束页
            'content_summary': {
                'total_paragraphs': len(paragraphs),
                'total_characters': len(text_content),
                'estimated_words': len(text_content.replace(' ', '')) // 2  # 粗略估算
            },
            'slide_structure': [
                {'type': 'cover', 'title': '演示文稿标题', 'content': '自动生成的封面页'},
                {'type': 'content', 'title': '内容概览', 'content': f'基于 {len(paragraphs)} 个段落生成'}
            ]
        }
        
        # 添加内容段落预览
        for i, para in enumerate(paragraphs[:5]):  # 只显示前5段作为预览
            preview_data['slide_structure'].append({
                'type': 'content',
                'title': f'内容 {i+1}',
                'content': para[:100] + '...' if len(para) > 100 else para
            })
            
        if len(paragraphs) > 5:
            preview_data['slide_structure'].append({
                'type': 'content',
                'title': '更多内容',
                'content': f'还有 {len(paragraphs) - 5} 个段落...'
            })
            
        preview_data['slide_structure'].append({
            'type': 'end',
            'title': '谢谢观看',
            'content': '演示结束'
        })
        
        return preview_data

    def create_pptx_file(self, text_content, theme, slide_count, include_charts, language, paragraphs):
        pass
        