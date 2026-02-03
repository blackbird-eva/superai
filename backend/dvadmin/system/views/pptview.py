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
        """
        使用python-pptx创建实际的PPT文件
        直接实现PPT生成逻辑，避免循环导入
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

        # ===================== 2. 创建内容页（简化版本，确保能生成） =====================
        content_count = max(1, slide_count - 2)  # 至少1页内容
        for i in range(min(content_count, len(paragraphs) - 1)):
            if i + 1 >= len(paragraphs):
                break
                
            blank_layout = prs.slide_layouts[6]  # 空白页
            slide = prs.slides.add_slide(blank_layout)

            # 设置背景色
            slide.background.fill.solid()
            slide.background.fill.fore_color.rgb = theme_colors['bg_color']

            # 添加标题
            title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.9))
            tf_title = title_box.text_frame
            para = paragraphs[i + 1]
            slide_title = para[:30] if len(para) > 30 else para
            tf_title.text = slide_title
            title_paragraph = tf_title.paragraphs[0]
            title_paragraph.font.name = font_name
            title_paragraph.font.size = Pt(28)
            title_paragraph.font.bold = True
            title_paragraph.font.color.rgb = theme_colors['primary_color']
            title_paragraph.alignment = PP_ALIGN.CENTER

            # 添加内容
            content_box = slide.shapes.add_textbox(Inches(0.7), Inches(1.5), Inches(8.6), Inches(3.5))
            content_frame = content_box.text_frame
            content_frame.word_wrap = True
            content_para = content_frame.paragraphs[0]
            content_text = para[30:300] if len(para) > 30 else "详细内容请参考原文。"
            content_para.text = content_text
            content_para.font.name = font_name
            content_para.font.size = Pt(16)
            content_para.font.color.rgb = theme_colors['text_color']
            content_para.line_spacing = 1.5

        # ===================== 3. 创建结束页 =====================
        section_layout = prs.slide_layouts[2]  # 节标题
        slide_end = prs.slides.add_slide(section_layout)
        slide_end.background.fill.solid()
        slide_end.background.fill.fore_color.rgb = theme_colors['primary_color']

        title_end = slide_end.shapes.title
        title_end.text = "谢谢观看"
        title_end.text_frame.paragraphs[0].font.name = font_name
        title_end.text_frame.paragraphs[0].font.size = Pt(52)
        title_end.text_frame.paragraphs[0].font.bold = True
        title_end.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
        title_end.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

        # ===================== 保存PPT文件 =====================
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
