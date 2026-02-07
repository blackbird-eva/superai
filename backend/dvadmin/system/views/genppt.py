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
        import logging
        logger = logging.getLogger(__name__)
        
        from pptx import Presentation
        from pptx.util import Pt, Inches
        from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
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

        # ===================== 1. 调用大模型生成智能内容 =====================
        # 使用大模型分析文本内容，生成结构化的PPT内容（包括标题和副标题）
        ai_generated_content = self.generate_content_with_ai(text_content, theme, slide_count, paragraphs)
        
        print(ai_generated_content)
        # 从AI生成的内容中提取标题和副标题
        # 兼容两种字段名：subtitle 和 subtilt（拼写错误）
        ppt_title = ai_generated_content.get('title') or (paragraphs[0] if paragraphs else "演示文稿")
        ppt_subtitle = ai_generated_content.get('subtitle') or ai_generated_content.get('subtilt', '')
        
        logger.info(f"AI生成的标题: {ppt_title}")
        logger.info(f"AI生成的副标题: {ppt_subtitle}")

        # ===================== 2. 创建封面页（版式0：标题页） =====================
        title_slide_layout = prs.slide_layouts[0]  # 标题页
        slide1 = prs.slides.add_slide(title_slide_layout)

        # 设置背景图片
        bg_img_path = "d:/ai/bg.png"
        if os.path.exists(bg_img_path):
            # 添加背景图片，确保在文本下方
            # 先创建一个透明或白色的背景确保文本可见
            slide1.background.fill.solid()
            slide1.background.fill.fore_color.rgb = RGBColor(255, 255, 255)  # 白色背景确保文本可见
            
            # 添加背景图片，然后将所有文本框置于图片上方
            pic = slide1.shapes.add_picture(bg_img_path, 0, 0, prs.slide_width, prs.slide_height)
            
            # 将图片移到底层（在PowerPoint中，形状的顺序决定了层级）
            # 获取图片元素并将其移动到最前面，然后将其发送到后面
            slide1.shapes._spTree.remove(pic._element)
            slide1.shapes._spTree.insert(2, pic._element)  # 插入到较低层级
        else:
            # 如果背景图片不存在，设置纯色背景
            slide1.background.fill.solid()
            slide1.background.fill.fore_color.rgb = theme_colors['bg_color']

        # 设置主标题（使用AI生成的标题）
        # 删除原来的标题占位符，创建新的文本框以精确控制位置
        title_placeholder = slide1.shapes.title
        title_placeholder.text = ""
        
        # 创建新的文本框，向上移动约100px（~1.4英寸），并设为白色
        title_left = Inches(0.5)
        title_top = Inches(1.0)  # 原来默认位置约为2.0英寸，现在改为1.0英寸，向上移动约1英寸(约72px)
        title_width = Inches(9)   # 保持宽度
        title_height = Inches(1.2)  # 高度调整以适应内容
        
        title_box = slide1.shapes.add_textbox(title_left, title_top, title_width, title_height)
        title_frame = title_box.text_frame
        title_frame.text = ppt_title
        title_frame.paragraphs[0].font.name = font_name
        title_frame.paragraphs[0].font.size = Pt(46)
        title_frame.paragraphs[0].font.bold = True
        title_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)  # 白色文字
        title_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        title_frame.word_wrap = True

        # 设置副标题（使用AI生成的副标题，如果没有则使用默认格式）
        # 创建新的副标题文本框，向上移动并与主标题协调
        subtitle_left = Inches(0.5)
        subtitle_top = Inches(2.3)  # 在主标题下方
        subtitle_width = Inches(9)
        subtitle_height = Inches(0.8)
        
        subtitle_box = slide1.shapes.add_textbox(subtitle_left, subtitle_top, subtitle_width, subtitle_height)
        subtitle_frame = subtitle_box.text_frame
        if ppt_subtitle:
            # 使用AI生成的副标题
            subtitle_frame.text = ppt_subtitle
        else:
            # 使用默认格式
            subtitle_frame.text = f"专业术语详解1 | {theme_colors['name']}\n{datetime.now().strftime('%Y年%m月')}"
        
        subtitle_frame.paragraphs[0].font.name = font_name
        subtitle_frame.paragraphs[0].font.size = Pt(18)
        subtitle_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)  # 白色文字
        subtitle_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        subtitle_frame.paragraphs[0].line_spacing = 1.6
        subtitle_frame.word_wrap = True

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

        # ===================== 3. 根据AI生成的内容创建幻灯片 =====================
        
        # ===================== 3. 根据AI生成的内容创建幻灯片 =====================
        for slide_idx, slide_data in enumerate(ai_generated_content['slides']):
            if slide_idx >= slide_count - 2:  # 预留封面和结束页
                break
                
            blank_layout = prs.slide_layouts[6]  # 空白页
            slide = prs.slides.add_slide(blank_layout)

            # 设置背景图片
            bg_img_path = "d:/ai/bg2.png"
            if os.path.exists(bg_img_path):
                slide.shapes.add_picture(bg_img_path, 0, 0, prs.slide_width, prs.slide_height)
            else:
                # 如果背景图片不存在，设置纯色背景
                slide.background.fill.solid()
                slide.background.fill.fore_color.rgb = theme_colors['bg_color']

            # 设置幻灯片标题（无背景框，只有黑色文字）
            slide_title = slide_data.get('title', f'内容 {slide_idx + 1}')
            
            # 创建文本框而不是带背景的形状
            title_left = Inches(0.5)
            title_top = Inches(0.8)
            title_width = Inches(9)
            title_height = Inches(0.9)
            
            title_box = slide.shapes.add_textbox(title_left, title_top, title_width, title_height)
            title_frame = title_box.text_frame
            title_frame.text = slide_title
            title_frame.paragraphs[0].font.name = font_name
            title_frame.paragraphs[0].font.size = Pt(28)
            title_frame.paragraphs[0].font.bold = True
            title_frame.paragraphs[0].font.color.rgb = RGBColor(0, 0, 0)  # 黑色文字
            title_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
            title_frame.word_wrap = True

            # 根据内容类型选择布局
            content_type = slide_data.get('type', 'text')
            
            if content_type == 'bullet_points':
                # 要点列表布局（参考pptdemo.py第76-100行）
                content_box = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(8), Inches(3.8))
                content_frame = content_box.text_frame
                content_frame.word_wrap = True

                bullets = slide_data.get('content', [])
                for j, bullet in enumerate(bullets[:6]):  # 最多6个要点
                    if j > 0:
                        p = content_frame.add_paragraph()
                    else:
                        p = content_frame.paragraphs[0]
                    p.text = f"• {bullet}"
                    p.level = 0
                    p.font.name = font_name
                    p.font.size = Pt(18)
                    p.font.color.rgb = theme_colors['text_color']
                    p.space_before = Pt(12)
                    p.space_after = Pt(6)
                    
            elif content_type == 'two_column':
                # 双栏布局（参考pptdemo.py第149-197行）
                # 左栏
                left_box = slide.shapes.add_shape(
                    MSO_SHAPE.ROUNDED_RECTANGLE,
                    Inches(0.7), Inches(1.5), Inches(4), Inches(3.5)
                )
                left_box.fill.solid()
                left_box.fill.fore_color.rgb = theme_colors['secondary_color']
                left_box.line.fill.background()

                left_title = slide_data.get('left_title', '要点')
                left_content = slide_data.get('left_content', [])
                
                left_frame = left_box.text_frame
                left_frame.text = left_title
                left_para = left_frame.paragraphs[0]
                left_para.font.name = font_name
                left_para.font.size = Pt(20)
                left_para.font.bold = True
                left_para.font.color.rgb = theme_colors['primary_color']
                left_para.alignment = PP_ALIGN.CENTER
                
                for item in left_content[:4]:
                    p = left_frame.add_paragraph()
                    p.text = f"• {item}"
                    p.font.name = font_name
                    p.font.size = Pt(16)
                    p.font.color.rgb = theme_colors['text_color']
                    p.space_before = Pt(8)

                # 右栏
                right_box = slide.shapes.add_shape(
                    MSO_SHAPE.ROUNDED_RECTANGLE,
                    Inches(5.3), Inches(1.5), Inches(4), Inches(3.5)
                )
                right_box.fill.solid()
                right_box.fill.fore_color.rgb = theme_colors['secondary_color']
                right_box.line.fill.background()

                right_title = slide_data.get('right_title', '详情')
                right_content = slide_data.get('right_content', [])
                
                right_frame = right_box.text_frame
                right_frame.text = right_title
                right_para = right_frame.paragraphs[0]
                right_para.font.name = font_name
                right_para.font.size = Pt(20)
                right_para.font.bold = True
                right_para.font.color.rgb = theme_colors['accent_color']
                right_para.alignment = PP_ALIGN.CENTER
                
                for item in right_content[:4]:
                    p = right_frame.add_paragraph()
                    p.text = f"• {item}"
                    p.font.name = font_name
                    p.font.size = Pt(16)
                    p.font.color.rgb = theme_colors['text_color']
                    p.space_before = Pt(8)
                    
            elif content_type == 'chart' and include_charts:
                # 图表页（参考pptdemo.py第101-135行）
                try:
                    from pptx.chart.data import CategoryChartData
                    from pptx.enum.chart import XL_CHART_TYPE
                    
                    # 获取图表数据
                    chart_info = slide_data.get('chart_data', {})
                    categories = chart_info.get('categories', [])
                    values = chart_info.get('values', [])
                    
                    if categories and values:
                        chart_data = CategoryChartData()
                        chart_data.categories = categories
                        chart_data.add_series('数据', values)

                        # 添加柱状图
                        x, y, cx, cy = Inches(1), Inches(1.8), Inches(8), Inches(3)
                        chart = slide.shapes.add_chart(
                            XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, chart_data
                        ).chart

                        # 设置图表样式
                        chart.has_legend = False
                        chart.category_axis.has_major_gridlines = False
                        chart.value_axis.has_major_gridlines = True

                        # 设置柱状图颜色
                        plot = chart.plots[0]
                        for series in plot.series:
                            series.format.fill.solid()
                            series.format.fill.fore_color.rgb = theme_colors['primary_color']
                except Exception as chart_error:
                    # 如果图表创建失败，降级为文本内容
                    self._add_text_content(slide, slide_data, theme_colors, font_name)
                    
            elif content_type == 'summary':
                # 总结页（参考pptdemo.py第199-238行）
                summary_box = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(8), Inches(2.8))
                summary_frame = summary_box.text_frame
                summary_frame.word_wrap = True
                
                summary_text = slide_data.get('content', '内容总结')
                summary_frame.text = summary_text
                summary_para = summary_frame.paragraphs[0]
                summary_para.font.name = font_name
                summary_para.font.size = Pt(18)
                summary_para.font.color.rgb = theme_colors['text_color']
                summary_para.alignment = PP_ALIGN.JUSTIFY
                
                # 添加强调框
                highlight_box = slide.shapes.add_shape(
                    MSO_SHAPE.ROUNDED_RECTANGLE,
                    Inches(2), Inches(4.2), Inches(6), Inches(1)
                )
                highlight_box.fill.solid()
                highlight_box.fill.fore_color.rgb = theme_colors['accent_color']
                highlight_box.line.color.rgb = RGBColor(255, 255, 255)
                highlight_box.line.width = Pt(1.5)

                highlight_frame = highlight_box.text_frame
                highlight_text = slide_data.get('highlight', '关键要点')
                highlight_frame.text = highlight_text
                highlight_para = highlight_frame.paragraphs[0]
                highlight_para.font.name = font_name
                highlight_para.font.size = Pt(20)
                highlight_para.font.bold = True
                highlight_para.font.color.rgb = RGBColor(255, 255, 255)
                highlight_para.alignment = PP_ALIGN.CENTER
                highlight_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
                
            else:
                # 默认文本内容
                self._add_text_content(slide, slide_data, theme_colors, font_name)
                
            # 添加备注
            note_text = slide_data.get('note', f'内容页{slide_idx + 1}')
            if hasattr(slide, 'notes_slide'):
                notes_slide = slide.notes_slide
                if notes_slide:
                    note = notes_slide.notes_text_frame
                    note.text = note_text

        # ===================== 4. 创建结束页（使用空白版式避免占位符） =====================
        blank_layout = prs.slide_layouts[6]  # 使用空白版式
        slide_end = prs.slides.add_slide(blank_layout)
        
        # 设置背景图片
        bg_img_path = "d:/ai/bg.png"
        if os.path.exists(bg_img_path):
            # 添加背景图片，确保在文本下方
            # 先创建一个透明或白色的背景确保文本可见
            slide_end.background.fill.solid()
            slide_end.background.fill.fore_color.rgb = RGBColor(255, 255, 255)  # 白色背景确保文本可见
            
            # 添加背景图片，然后将所有文本框置于图片上方
            pic = slide_end.shapes.add_picture(bg_img_path, 0, 0, prs.slide_width, prs.slide_height)
            
            # 将图片移到底层（在PowerPoint中，形状的顺序决定了层级）
            # 获取图片元素并将其移动到最前面，然后将其发送到后面
            slide_end.shapes._spTree.remove(pic._element)
            slide_end.shapes._spTree.insert(2, pic._element)  # 插入到较低层级
        else:
            # 如果背景图片不存在，设置纯色背景
            slide_end.background.fill.solid()
            slide_end.background.fill.fore_color.rgb = theme_colors['primary_color']

        # 创建标题文本框，使用白色文字（不使用任何占位符）
        end_title_left = Inches(0.5)
        end_title_top = Inches(2.0)
        end_title_width = Inches(9)
        end_title_height = Inches(1.5)
        
        end_title_box = slide_end.shapes.add_textbox(end_title_left, end_title_top, end_title_width, end_title_height)
        end_title_frame = end_title_box.text_frame
        end_title_frame.text = "谢谢观看"
        end_title_frame.paragraphs[0].font.name = font_name
        end_title_frame.paragraphs[0].font.size = Pt(52)
        end_title_frame.paragraphs[0].font.bold = True
        end_title_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)  # 白色文字
        end_title_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        end_title_frame.word_wrap = True

        # ===================== 5. 保存PPT文件 =====================
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

    def generate_content_with_ai(self, text_content, theme, slide_count, paragraphs):
        """
        调用大模型生成智能PPT内容
        
        参数:
            text_content: 原始文本内容
            theme: 主题类型
            slide_count: 幻灯片数量
            paragraphs: 解析后的段落列表
            
        返回:
            包含生成内容的字典
        """
        import json
        import logging
        logger = logging.getLogger(__name__)
        
        # 检查是否配置了大模型服务
        use_llm = getattr(settings, 'USE_LLM_FOR_PPT', True )
        
        if not use_llm:
            logger.info("未启用大模型服务，使用规则生成内容")
            return self._generate_content_by_rules(text_content, theme, slide_count, paragraphs)
        
        try:
            # 尝试导入大模型库（这里使用示例，实际根据你的大模型实现调整）
            # 假设你有一个LLM服务调用方法
            from dvadmin.utils.llm_service import call_llm
            
            # 构建提示词
            prompt = f"""
请分析以下文本内容，为PPT生成{slide_count}页幻灯片的结构化内容。

主题风格：{theme}
语言：中文

原始文本内容：
{text_content[:3000]}

请按照以下JSON格式返回内容：
{{
    "title":"幻灯片总标题",
    "subtilt":"幻灯片副标题",

    "slides": [
        {{
            "type": "bullet_points",
            "title": "幻灯片标题",
            "content": ["要点1", "要点2", "要点3"],
            "note": "备注信息"
        }},
        {{
            "type": "two_column",
            "title": "双栏标题",
            "left_title": "左栏标题",
            "left_content": ["左栏要点1", "左栏要点2"],
            "right_title": "右栏标题",
            "right_content": ["右栏要点1", "右栏要点2"],
            "note": "备注信息"
        }},
        {{
            "type": "chart",
            "title": "图表标题",
            "chart_data": {{
                "categories": ["类别1", "类别2", "类别3"],
                "values": [100, 200, 150]
            }},
            "note": "备注信息"
        }},
        {{
            "type": "summary",
            "title": "总结标题",
            "content": "总结文本内容...",
            "highlight": "关键要点",
            "note": "备注信息"
        }}
    ]
}}

注意：
1. 幻灯片类型包括：bullet_points（要点列表）、two_column（双栏）、chart（图表）、summary（总结）
2. 确保内容简洁、专业
3. 每个要点不超过50个字
4. 图表页只在include_charts为True时使用
5. 返回纯JSON格式，不要有其他说明文字
"""

            # 调用大模型
            logger.info(f"开始调用大模型生成PPT内容，主题：{theme}，页数：{slide_count}")
            logger.info(f"调用大模型生成PPT内容，提示词：{prompt}")
            llm_response = call_llm(prompt)
            
            # 解析返回的JSON
            try:
                ai_content = json.loads(llm_response)
                logger.info(f"大模型成功生成内容，共{len(ai_content.get('slides', []))}页")
                return ai_content
            except json.JSONDecodeError as e:
                logger.error(f"大模型返回的JSON解析失败: {e}")
                # 降级到规则生成
                return self._generate_content_by_rules(text_content, theme, slide_count, paragraphs)
                
        except ImportError:
            logger.warning("未找到大模型服务，使用规则生成内容")
            return self._generate_content_by_rules(text_content, theme, slide_count, paragraphs)
        except Exception as e:
            logger.error(f"调用大模型失败: {e}")
            # 降级到规则生成
            return self._generate_content_by_rules(text_content, theme, slide_count, paragraphs)

    def _generate_content_by_rules(self, text_content, theme, slide_count, paragraphs):
        """
        基于规则生成PPT内容（降级方案）
        """
        import re
        from collections import Counter
        
        slides = []
        
        # 使用第一个段落作为标题
        main_title = paragraphs[0] if paragraphs else "演示文稿"
        
        # 统计段落内容，提取关键词
        all_text = ' '.join(paragraphs)
        words = re.findall(r'[\w\u4e00-\u9fff]+', all_text)
        common_words = Counter(words).most_common(20)
        
        # 根据页数生成不同类型的幻灯片
        slide_types = ['bullet_points', 'two_column', 'summary', 'bullet_points', 'chart']
        
        for i in range(min(slide_count - 2, len(paragraphs) - 1)):
            if i + 1 >= len(paragraphs):
                break
                
            slide_type = slide_types[i % len(slide_types)]
            para = paragraphs[i + 1]
            
            if slide_type == 'bullet_points':
                # 从段落中提取要点
                sentences = re.split(r'[。！？；\n]', para)
                bullets = [s.strip() for s in sentences if len(s.strip()) > 5][:6]
                
                slides.append({
                    'type': 'bullet_points',
                    'title': para[:30] + ('...' if len(para) > 30 else ''),
                    'content': bullets,
                    'note': f'内容页{i + 1}：{bullets[0] if bullets else ""}'
                })
                
            elif slide_type == 'two_column':
                # 双栏布局
                sentences = re.split(r'[。！？；\n]', para)
                left_content = [s.strip() for s in sentences[:3] if len(s.strip()) > 5]
                right_content = [s.strip() for s in sentences[3:6] if len(s.strip()) > 5]
                
                slides.append({
                    'type': 'two_column',
                    'title': '内容概览',
                    'left_title': '主要观点',
                    'left_content': left_content,
                    'right_title': '详细说明',
                    'right_content': right_content,
                    'note': f'内容页{i + 1}：双栏布局展示'
                })
                
            elif slide_type == 'summary':
                # 总结页
                summary_text = para[:200] + ('...' if len(para) > 200 else '')
                
                slides.append({
                    'type': 'summary',
                    'title': '要点总结',
                    'content': summary_text,
                    'highlight': common_words[i][0] if i < len(common_words) else '核心要点',
                    'note': f'内容页{i + 1}：总结回顾'
                })
                
            elif slide_type == 'chart':
                # 图表页（模拟数据）
                slides.append({
                    'type': 'chart',
                    'title': '数据分析',
                    'chart_data': {
                        'categories': ['类别1', '类别2', '类别3', '类别4', '类别5'],
                        'values': [30, 45, 25, 60, 40]
                    },
                    'note': f'内容页{i + 1}：数据图表展示'
                })

        return {'slides': slides}

    def _add_text_content(self, slide, slide_data, theme_colors, font_name):
        """
        添加默认的文本内容（降级方案）
        """
        from pptx.util import Inches, Pt
        from pptx.enum.text import PP_ALIGN
        from pptx.dml.color import RGBColor
        
        content_box = slide.shapes.add_textbox(Inches(0.7), Inches(1.5), Inches(8.6), Inches(3.5))
        content_frame = content_box.text_frame
        content_frame.word_wrap = True
        
        content_text = slide_data.get('content', '内容详情')
        content_para = content_frame.paragraphs[0]
        content_para.text = content_text[:500] + ('...' if len(content_text) > 500 else '')
        content_para.font.name = font_name
        content_para.font.size = Pt(16)
        content_para.font.color.rgb = theme_colors['text_color']
        content_para.line_spacing = 1.5