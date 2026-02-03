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


