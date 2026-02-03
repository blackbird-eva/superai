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
 
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from django.http import HttpResponse
from django.conf import settings

from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from .genppt import genPPT

class GeneratePPTView(APIView):
    """
    PPT生成接口 - 接收文本内容生成PPT
    """
    authentication_classes = []
    permission_classes = []
    renderer_classes = [JSONRenderer]

    def post(self, request):
        """
        根据文本内容生成PPT
        """
        try:
            # 获取文本内容
            text_content = request.data.get('text', '')
            if not text_content or not text_content.strip():
                return ErrorResponse(msg="请输入文本内容", code=400)

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

            # 解析文本内容
            paragraphs = self.parse_text(text_content)

            pptm = genPPT()
            # 生成PPT文件
            ppt_file_info = pptm.create_pptx_file(text_content, theme, slide_count, include_charts, language, paragraphs)

            # 生成预览数据
            ppt_data = self.generate_ppt_preview_data(text_content, theme, slide_count, include_charts, language, paragraphs)

            # 合并文件信息和预览数据
            ppt_data.update({
                'ppt_file_path': ppt_file_info['file_path'],
                'ppt_file_name': ppt_file_info['file_name'],
                'ppt_download_url': ppt_file_info['download_url']
            })

            return SuccessResponse(data=ppt_data, msg="PPT生成成功")

        except Exception as e:
            import traceback
            traceback.print_exc()
            return ErrorResponse(msg=f"生成失败: {str(e)}", code=500)

    

    def generate_ppt_preview_data(self, text_content, theme, slide_count, include_charts, language, paragraphs):
        """
        生成PPT预览数据（用于前端显示）
        """
        import re
        themes_config = {
            'business': '商务简约',
            'tech': '科技现代',
            'education': '教育培训',
            'creative': '创意活泼',
            'academic': '学术正式'
        }

        theme_name = themes_config.get(theme, '商务简约')

        # 生成幻灯片预览列表
        slides = []

        # 封面页
        title = paragraphs[0] if paragraphs else "演示文稿"
        slides.append({
            'layout': 'title',
            'title': title,
            'content': f"专业术语详解 | {theme_name}\n{datetime.now().strftime('%Y年%m月')}",
            'note': '封面页：演示PPT的主标题和基本信息'
        })

        # 目录页
        if len(paragraphs) > 1:
            bullets_list = []
            content_count = slide_count - 2
            for i, item in enumerate(paragraphs[1:]):
                if i >= content_count:
                    break
                bullets_list.append(item[:30] if len(item) > 30 else item)

            slides.append({
                'layout': 'title-bullets',
                'title': '目录',
                'bullets': bullets_list,
                'note': '目录页：展示PPT的主要章节和内容概览'
            })

        # 内容页
        content_count = slide_count - 2
        for i in range(content_count):
            if i < len(paragraphs) - 1:
                para = paragraphs[i + 1]
                bullets = self.extract_bullets(para)

                # 检测是否为术语定义格式
                term_match = re.match(r'^([^：\-]+)[：\-]\s*(.+)$', para.strip())

                if term_match and len(para.strip()) < 200:
                    # 术语定义页
                    term = term_match.group(1).strip()
                    definition = term_match.group(2).strip()
                    slides.append({
                        'layout': 'term-definition',
                        'title': term,
                        'content': definition,
                        'note': f'内容页：术语定义 - {term}'
                    })
                elif bullets:
                    # 要点列表页
                    slides.append({
                        'layout': 'title-bullets',
                        'title': para.replace('#', '').strip() if para.startswith('#') else f'内容 {i + 1}',
                        'bullets': bullets[:5],
                        'note': f'内容页{i + 2}：详细展示相关内容'
                    })
                else:
                    # 普通内容页
                    slides.append({
                        'layout': 'title-content',
                        'title': para.replace('#', '').strip() if para.startswith('#') else f'内容 {i + 1}',
                        'content': para[:300] if len(para) > 300 else para,
                        'note': f'内容页{i + 2}：详细展示相关内容'
                    })
            else:
                slides.append({
                    'layout': 'title-content',
                    'title': f'内容 {i + 1}',
                    'content': '根据输入的文本内容自动生成的演示文稿',
                    'note': f'内容页{i + 2}：补充说明'
                })

        # 术语分类汇总页（表格页）
        if include_charts and slide_count >= 5:
            slides.append({
                'layout': 'title-table',
                'title': '术语分类汇总',
                'bullets': ['基础术语：核心概念与基本定义', '技术参数：规格数据与技术指标', 
                           '操作规范：使用方法与注意事项', '维护保养：日常维护与故障排除'],
                'note': '术语分类汇总页：展示主要术语类别及其内容概览'
            })

        # 结束页
        if slide_count >= 7:
            slides.append({
                'layout': 'section-title',
                'title': '谢谢观看',
                'content': f'AI智能生成演示文稿\n{theme_name}\n{datetime.now().strftime("%Y年%m月")}',
                'note': '结束页：演示文稿结束，感谢您的观看与聆听'
            })

        return {
            'title': title,
            'description': f'基于文本内容生成的{theme_name}风格专业术语详解PPT',
            'theme': theme_name,
            'slide_count': slide_count,
            'create_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'slides': slides,
            'include_charts': include_charts,
            'language': language
        }

    def parse_text(self, text):
        """
        解析文本内容，提取段落和标题
        """
        import re

        # 按行分割
        lines = text.split('\n')

        # 过滤空行和提取有内容的行
        paragraphs = []
        for line in lines:
            line = line.strip()
            if line:
                # 处理Markdown标题
                if line.startswith('#'):
                    title = re.sub(r'^#+\s*', '', line).strip()
                    if title:
                        paragraphs.append(title)
                # 处理列表项
                elif line.startswith('-') or line.startswith('*') or line.startswith('•'):
                    item = re.sub(r'^[-*•]\s*', '', line).strip()
                    if item:
                        paragraphs.append(item)
                # 普通段落
                else:
                    paragraphs.append(line)

        return paragraphs[:30]  # 最多30个段落

    def extract_bullets(self, text):
        """
        从文本中提取要点
        """
        bullets = []

        # 按句号、问号、感叹号分割
        sentences = re.split(r'[。！？\n]', text)

        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 3:
                bullets.append(sentence)
                if len(bullets) >= 6:
                    break

        return bullets

 

