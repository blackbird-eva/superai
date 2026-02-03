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
        if len(paragraphs) > 1:
            blank_layout = prs.slide_layouts[6]  # 空白页
            slide2 = prs.slides.add_slide(blank_layout)

            # 设置背景色
            slide2.background.fill.solid()
            slide2.background.fill.fore_color.rgb = theme_colors['bg_color']

            # 添加标题框
            title_box = slide2.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(9), Inches(1))
            tf_title = title_box.text_frame
            tf_title.text = "目录"
            title_paragraph = tf_title.paragraphs[0]
            title_paragraph.font.name = font_name
            title_paragraph.font.size = Pt(36)
            title_paragraph.font.bold = True
            title_paragraph.font.color.rgb = theme_colors['primary_color']
            title_paragraph.alignment = PP_ALIGN.CENTER

            # 添加装饰线
            line_shape = slide2.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(0.5), Inches(1.6), Inches(9), Inches(0.08)
            )
            line_shape.fill.solid()
            line_shape.fill.fore_color.rgb = theme_colors['accent_color']
            line_shape.line.fill.background()

            # 添加目录项
            top = Inches(2.2)
            for i, item in enumerate(paragraphs[1:7]):
                if i >= slide_count - 2:
                    break

                # 添加序号圆圈
                circle = slide2.shapes.add_shape(
                    MSO_SHAPE.OVAL,
                    Inches(1.2), top, Inches(0.45), Inches(0.45)
                )
                circle.fill.solid()
                circle.fill.fore_color.rgb = theme_colors['primary_color']
                circle.line.fill.background()

                # 添加序号文本
                circle_text = circle.text_frame
                circle_text.text = str(i + 1)
                circle_text.paragraphs[0].font.name = font_name
                circle_text.paragraphs[0].font.size = Pt(16)
                circle_text.paragraphs[0].font.bold = True
                circle_text.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
                circle_text.paragraphs[0].alignment = PP_ALIGN.CENTER

                # 添加目录项文本
                text_box = slide2.shapes.add_textbox(Inches(2), top, Inches(7), Inches(0.45))
                text_frame = text_box.text_frame
                text_frame.text = item[:30] if len(item) > 30 else item
                text_frame.paragraphs[0].font.name = font_name
                text_frame.paragraphs[0].font.size = Pt(18)
                text_frame.paragraphs[0].font.color.rgb = theme_colors['text_color']
                text_frame.paragraphs[0].space_before = Pt(6)

                top += Inches(0.55)

            # 添加备注
            notes_slide2 = slide2.notes_slide
            if notes_slide2:
                note = notes_slide2.notes_text_frame
                note.text = "目录页：展示PPT的主要章节和内容概览。"

        # ===================== 3. 创建内容页（版式6：空白页） =====================
        content_count = slide_count - 2
        for i in range(content_count):
            blank_layout = prs.slide_layouts[6]
            slide = prs.slides.add_slide(blank_layout)

            # 设置背景色
            slide.background.fill.solid()
            slide.background.fill.fore_color.rgb = theme_colors['bg_color']

            # 添加标题背景框（圆角矩形）
            title_box = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(0.5), Inches(0.3), Inches(9), Inches(0.9)
            )
            title_box.fill.solid()
            title_box.fill.fore_color.rgb = theme_colors['primary_color']
            title_box.line.fill.background()

            # 设置幻灯片标题
            if i < len(paragraphs) - 1:
                para = paragraphs[i + 1]
                if para.startswith('#'):
                    slide_title = re.sub(r'^#+\s*', '', para).strip()
                else:
                    slide_title = para[:20] if len(para) > 20 else para
            else:
                slide_title = f"内容 {i + 1}"

            title_text_frame = title_box.text_frame
            title_text_frame.text = slide_title
            title_paragraph = title_text_frame.paragraphs[0]
            title_paragraph.font.name = font_name
            title_paragraph.font.size = Pt(28)
            title_paragraph.font.bold = True
            title_paragraph.font.color.rgb = RGBColor(255, 255, 255)
            title_paragraph.alignment = PP_ALIGN.CENTER

            # 检测是否为术语定义格式（术语：解释 或 术语 - 解释）
            if i < len(paragraphs) - 1:
                para = paragraphs[i + 1]
                term_match = re.match(r'^([^：\-]+)[：\-]\s*(.+)$', para.strip())

                # 如果是术语定义，使用双栏布局
                if term_match and len(para.strip()) < 200:
                    term = term_match.group(1).strip()
                    definition = term_match.group(2).strip()

                    # 左栏 - 术语
                    term_box = slide.shapes.add_shape(
                        MSO_SHAPE.ROUNDED_RECTANGLE,
                        Inches(0.7), Inches(1.5), Inches(3.5), Inches(3.5)
                    )
                    term_box.fill.solid()
                    term_box.fill.fore_color.rgb = theme_colors['secondary_color']
                    term_box.line.fill.background()

                    term_text_frame = term_box.text_frame
                    term_text_frame.word_wrap = True
                    term_paragraph = term_text_frame.paragraphs[0]
                    term_paragraph.text = term
                    term_paragraph.font.name = font_name
                    term_paragraph.font.size = Pt(22)
                    term_paragraph.font.bold = True
                    term_paragraph.font.color.rgb = theme_colors['primary_color']
                    term_paragraph.alignment = PP_ALIGN.CENTER

                    # 右栏 - 解释
                    defn_box = slide.shapes.add_textbox(Inches(4.5), Inches(1.5), Inches(4.8), Inches(3.5))
                    defn_frame = defn_box.text_frame
                    defn_frame.word_wrap = True
                    defn_paragraph = defn_frame.paragraphs[0]
                    defn_paragraph.text = definition
                    defn_paragraph.font.name = font_name
                    defn_paragraph.font.size = Pt(18)
                    defn_paragraph.font.color.rgb = theme_colors['text_color']
                    defn_paragraph.line_spacing = 1.5
                    defn_paragraph.space_before = Pt(8)
                    defn_paragraph.space_after = Pt(8)

                else:
                    # 添加内容框
                    content_box = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(8), Inches(3.8))
                    content_frame = content_box.text_frame
                    content_frame.word_wrap = True

                    # 添加内容
                    bullets = self.extract_bullets(para)

                    if bullets:
                        for j, bullet in enumerate(bullets[:5]):
                            if j > 0:
                                p = content_frame.add_paragraph()
                            else:
                                p = content_frame.paragraphs[0]
                            p.text = bullet
                            p.level = 0
                            p.font.name = font_name
                            p.font.size = Pt(16)
                            p.font.color.rgb = theme_colors['text_color']
                            p.space_before = Pt(12)
                            p.space_after = Pt(6)
                    else:
                        p = content_frame.paragraphs[0]
                        p.text = para[:500] if len(para) > 500 else para
                        p.font.name = font_name
                        p.font.size = Pt(18)
                        p.font.color.rgb = theme_colors['text_color']
                        p.line_spacing = 1.5
            else:
                # 添加内容框
                content_box = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(8), Inches(3.8))
                content_frame = content_box.text_frame
                content_frame.word_wrap = True

                p = content_frame.paragraphs[0]
                p.text = "根据输入的文本内容，AI已自动生成此幻灯片的演示内容。"
                p.font.name = font_name
                p.font.size = Pt(18)
                p.font.color.rgb = theme_colors['text_color']
                p.line_spacing = 1.5

                p2 = content_frame.add_paragraph()
                p2.text = "\n此处可以展示更多详细信息、数据分析或图表说明。"
                p2.font.name = font_name
                p2.font.size = Pt(16)
                p2.font.color.rgb = RGBColor(153, 153, 153)
                p2.line_spacing = 1.5

            # 添加装饰元素（小圆点）
            if i % 2 == 0:  # 每隔一页添加
                dot_shape = slide.shapes.add_shape(
                    MSO_SHAPE.OVAL,
                    Inches(9.2), Inches(5), Inches(0.3), Inches(0.3)
                )
                dot_shape.fill.solid()
                dot_shape.fill.fore_color.rgb = theme_colors['accent_color']
                dot_shape.line.fill.background()

            # 添加备注
            notes_slide = slide.notes_slide
            if notes_slide:
                note = notes_slide.notes_text_frame
                note.text = f"内容页{i+1}：详细展示{slide_title}的相关内容。"

        # ===================== 4. 创建专业术语表格页（版式1：标题+内容） =====================
        if include_charts and slide_count >= 5:
            content_layout = prs.slide_layouts[1]  # 标题+内容
            slide_table = prs.slides.add_slide(content_layout)

            # 设置背景色
            slide_table.background.fill.solid()
            slide_table.background.fill.fore_color.rgb = theme_colors['bg_color']

            # 设置标题
            title_table = slide_table.shapes.title
            title_table.text = "术语分类汇总"
            title_table.text_frame.paragraphs[0].font.name = font_name
            title_table.text_frame.paragraphs[0].font.size = Pt(28)
            title_table.text_frame.paragraphs[0].font.bold = True
            title_table.text_frame.paragraphs[0].font.color.rgb = theme_colors['primary_color']

            # 获取内容占位符
            placeholder = slide_table.placeholders[1]

            # 插入表格
            table_left = Inches(1)
            table_top = Inches(2)
            table_cols = 3
            table_rows = 5
            table_width = Inches(8)
            table_height = Inches(3.2)

            table = slide_table.shapes.add_table(
                rows=table_rows, cols=table_cols,
                left=table_left, top=table_top,
                width=table_width, height=table_height
            ).table

            # 定义表格数据 - 专业术语分类表
            table_data = [
                ["序号", "术语类别", "内容概览"],
                ["1", "基础术语", "核心概念与基本定义"],
                ["2", "技术参数", "规格数据与技术指标"],
                ["3", "操作规范", "使用方法与注意事项"],
                ["4", "维护保养", "日常维护与故障排除"]
            ]

            # 填充表格内容并自定义样式
            for row_idx in range(table_rows):
                for col_idx in range(table_cols):
                    cell = table.cell(row_idx, col_idx)
                    cell.text = table_data[row_idx][col_idx]
                    cell.text_frame.paragraphs[0].font.name = font_name
                    cell.text_frame.paragraphs[0].font.size = Pt(15)
                    cell.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
                    cell.text_frame.paragraphs[0].space_before = Pt(4)
                    cell.text_frame.paragraphs[0].space_after = Pt(4)

                    if row_idx == 0:
                        # 表头 - 主题色背景
                        cell.fill.solid()
                        cell.fill.fore_color.rgb = theme_colors['primary_color']
                        cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
                        cell.text_frame.paragraphs[0].font.bold = True
                        cell.text_frame.paragraphs[0].font.size = Pt(16)
                    elif row_idx % 2 == 1:
                        # 奇数行 - 浅色背景
                        cell.fill.solid()
                        cell.fill.fore_color.rgb = theme_colors['secondary_color']
                        cell.text_frame.paragraphs[0].font.color.rgb = theme_colors['text_color']
                    else:
                        # 偶数行 - 白色背景
                        cell.fill.solid()
                        cell.fill.fore_color.rgb = RGBColor(255, 255, 255)
                        cell.text_frame.paragraphs[0].font.color.rgb = theme_colors['text_color']

            # 添加备注
            notes_slide_table = slide_table.notes_slide
            if notes_slide_table:
                note = notes_slide_table.notes_text_frame
                note.text = "术语分类汇总页：展示主要术语类别及其内容概览，便于快速查阅。"

        # ===================== 5. 创建节标题页（版式2） =====================
        if slide_count >= 7:
            section_layout = prs.slide_layouts[2]  # 节标题
            slide_section = prs.slides.add_slide(section_layout)

            # 设置背景色
            slide_section.background.fill.solid()
            slide_section.background.fill.fore_color.rgb = theme_colors['primary_color']

            # 设置节标题
            title_section = slide_section.shapes.title
            title_section.text = "谢谢观看"
            title_section.text_frame.paragraphs[0].font.name = font_name
            title_section.text_frame.paragraphs[0].font.size = Pt(52)
            title_section.text_frame.paragraphs[0].font.bold = True
            title_section.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
            title_section.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

            # 添加副标题
            if len(slide_section.placeholders) > 1:
                subtitle_section = slide_section.placeholders[1]
                subtitle_section.text = f"AI智能生成演示文稿\n{theme_colors['name']}\n{datetime.now().strftime('%Y年%m月')}"
                subtitle_section.text_frame.paragraphs[0].font.name = font_name
                subtitle_section.text_frame.paragraphs[0].font.size = Pt(20)
                subtitle_section.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
                subtitle_section.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
                subtitle_section.text_frame.paragraphs[0].line_spacing = 1.8

            # 添加装饰形状（底部矩形）
            deco_section = slide_section.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(2), Inches(5.2), Inches(6), Inches(0.15)
            )
            deco_section.fill.solid()
            deco_section.fill.fore_color.rgb = RGBColor(255, 255, 255)
            deco_section.line.fill.background()

            # 添加备注
            notes_slide_section = slide_section.notes_slide
            if notes_slide_section:
                note = notes_slide_section.notes_text_frame
                note.text = "结束页：演示文稿结束，感谢您的观看与聆听。"

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