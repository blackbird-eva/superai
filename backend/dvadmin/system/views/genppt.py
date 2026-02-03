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


class genPPT():
    def create_pptx_file(self, text_content, theme, slide_count, include_charts, language, paragraphs):
        """
        使用python-pptx创建实际的PPT文件
        """
        from pptx import Presentation
        from pptx.util import Pt, Inches
        from pptx.enum.text import PP_ALIGN
        from pptx.dml.color import RGBColor
        from pptx.enum.shapes import MSO_SHAPE
        import platform

        # 检测操作系统，设置兼容字体
        def get_compatible_font(preferred_font):
            """根据操作系统返回兼容字体"""
            system = platform.system()
            if system == 'Windows':
                font_map = {
                    '微软雅黑': '微软雅黑',
                    '思源黑体': '思源黑体',
                    '宋体': '宋体',
                    '黑体': '黑体',
                    '楷体': '楷体'
                }
            elif system == 'Darwin':  # macOS
                font_map = {
                    '微软雅黑': 'PingFang SC',
                    '思源黑体': 'PingFang SC',
                    '宋体': 'STSong',
                    '黑体': 'Heiti SC',
                    '楷体': 'Kaiti SC'
                }
            else:  # Linux
                font_map = {
                    '微软雅黑': 'Noto Sans CJK SC',
                    '思源黑体': 'Noto Sans CJK SC',
                    '宋体': 'Noto Serif CJK SC',
                    '黑体': 'SimHei',
                    '楷体': 'KaiTi'
                }
            return font_map.get(preferred_font, 'Arial')

        # 主题配置
        themes_config = {
            'business': {
                'name': '商务简约',
                'primary_color': RGBColor(64, 158, 255),
                'secondary_color': RGBColor(240, 240, 240),
                'text_color': RGBColor(51, 51, 51),
                'accent_color': RGBColor(103, 194, 58),
                'preferred_font': '微软雅黑',
                'bg_color': RGBColor(245, 245, 245)
            },
            'tech': {
                'name': '科技现代',
                'primary_color': RGBColor(0, 212, 170),
                'secondary_color': RGBColor(245, 245, 255),
                'text_color': RGBColor(30, 30, 30),
                'accent_color': RGBColor(67, 56, 202),
                'preferred_font': '思源黑体',
                'bg_color': RGBColor(250, 250, 255)
            },
            'education': {
                'name': '教育培训',
                'primary_color': RGBColor(255, 152, 0),
                'secondary_color': RGBColor(255, 253, 240),
                'text_color': RGBColor(60, 60, 60),
                'accent_color': RGBColor(233, 30, 99),
                'preferred_font': '宋体',
                'bg_color': RGBColor(255, 253, 240)
            },
            'creative': {
                'name': '创意活泼',
                'primary_color': RGBColor(233, 30, 99),
                'secondary_color': RGBColor(255, 240, 245),
                'text_color': RGBColor(40, 40, 40),
                'accent_color': RGBColor(156, 39, 176),
                'preferred_font': '黑体',
                'bg_color': RGBColor(255, 240, 245)
            },
            'academic': {
                'name': '学术正式',
                'primary_color': RGBColor(103, 58, 183),
                'secondary_color': RGBColor(245, 245, 250),
                'text_color': RGBColor(45, 45, 45),
                'accent_color': RGBColor(0, 96, 100),
                'preferred_font': '楷体',
                'bg_color': RGBColor(245, 245, 250)
            }
        }

        theme_colors = themes_config.get(theme, themes_config['business'])
        font_name = get_compatible_font(theme_colors['preferred_font'])

        # 创建Presentation对象
        prs = Presentation()
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(5.625)

        # 幻灯片标题
        title = paragraphs[0] if paragraphs else "演示文稿"

        # ===================== 1. 创建封面页（版式0：标题页） =====================
        title_slide_layout = prs.slide_layouts[0]  # 标题页
        slide1 = prs.slides.add_slide(title_slide_layout)

        # 设置纯色背景
        slide1.background.fill.solid()
        slide1.background.fill.fore_color.rgb = theme_colors['bg_color']

        # 设置主标题
        title1 = slide1.shapes.title
        title1.text = title
        title1_text_frame = title1.text_frame.paragraphs[0]
        title1_text_frame.font.name = font_name
        title1_text_frame.font.size = Pt(46)
        title1_text_frame.font.bold = True
        title1_text_frame.font.color.rgb = theme_colors['primary_color']
        title1_text_frame.alignment = PP_ALIGN.CENTER

        # 设置副标题
        subtitle1 = slide1.placeholders[1]
        subtitle1.text = f"专业术语详解 | {theme_colors['name']}\n{datetime.now().strftime('%Y年%m月')}"
        subtitle1_text_frame = subtitle1.text_frame.paragraphs[0]
        subtitle1_text_frame.font.name = font_name
        subtitle1_text_frame.font.size = Pt(18)
        subtitle1_text_frame.font.color.rgb = RGBColor(102, 102, 102)
        subtitle1_text_frame.alignment = PP_ALIGN.CENTER
        subtitle1_text_frame.line_spacing = 1.6

        # 添加顶部装饰形状
        top_deco = slide1.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(2), Inches(0.2), Inches(6), Inches(0.1)
        )
        top_deco.fill.solid()
        top_deco.fill.fore_color.rgb = theme_colors['accent_color']
        top_deco.line.fill.background()

        # 添加底部装饰形状
        deco_shape = slide1.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(2), Inches(5.2), Inches(6), Inches(0.25)
        )
        deco_shape.fill.solid()
        deco_shape.fill.fore_color.rgb = theme_colors['primary_color']
        deco_shape.line.fill.background()

        # 添加备注
        if hasattr(slide1, 'notes_slide') and slide1.notes_slide:
            note = slide1.notes_slide.notes_text_frame
            note.text = "封面页：演示PPT的主标题和基本信息。"
        else:
            # 如果没有备注页，手动添加
            notes_slide = slide1.notes_slide
            if notes_slide:
                note = notes_slide.notes_text_frame
                note.text = "封面页：演示PPT的主标题和基本信息。"

        # ===================== 2. 创建目录页（版式6：空白页，自由布局） =====================
    

        ## 

        # ===================== 6. 保存PPT文件 =====================
        date_path = datetime.now().strftime('%Y/%m/%d')
        save_dir = os.path.join(settings.MEDIA_ROOT, f'pptfile/{date_path}')

        if not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)

        file_name = f"AI生成PPT_{uuid.uuid4().hex[:8]}.pptx"
        file_path = os.path.join(save_dir, file_name)
        relative_path = f'pptfile/{date_path}/{file_name}'

        # 保存PPT文件
        try:
            prs.save(file_path)
        except Exception as save_error:
            # 如果保存失败，尝试使用临时目录
            import tempfile
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, file_name)
            prs.save(file_path)

        # 返回文件信息
        return {
            'file_path': relative_path,
            'file_name': file_name,
            'download_url': f'/api/system/transdicts/ppt/download/?file_path={relative_path}'
        }