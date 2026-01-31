import hashlib
import os
import uuid
from time import time
from pathlib import PurePosixPath

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils import timezone
from application import dispatch
from dvadmin.utils.models import CoreModel, table_prefix, get_custom_app_models


# 文档翻译状态选项
DOCXFILE_STATUS = [
    ('uploaded', '已上传'),
    ('processing', '处理中'),
    ('completed', '翻译完成'),
    ('failed', '翻译失败'),
    ('cancelled', '已取消'),
]


def docxfile_upload_path(instance, filename):
    """
    文档文件上传路径生成函数
    """
    # 生成唯一文件名
    ext = filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    
    # 按日期组织目录结构
    from datetime import datetime
    date_path = datetime.now().strftime('%Y/%m/%d')
    
    return f'docx/{date_path}/{unique_filename}'


def calculate_file_md5(file_path):
    """
    计算文件MD5值
    """
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return None


class Docxfile(CoreModel):
    """
    DOCX文档翻译管理
    """
    # 基本文件信息
    original_name = models.CharField(max_length=255, verbose_name="原始文件名", help_text="原始文件名")
    file_path = models.FileField(upload_to=docxfile_upload_path, verbose_name="文件路径", help_text="存储的文件路径")
    file_size = models.IntegerField(default=0, verbose_name="文件大小", help_text="文件大小(字节)")
    
    # 文档类型和支持格式
    DOCUMENT_TYPES = [
        ('docx', 'Word文档 (.docx)'),
        ('ppt', 'PowerPoint (.ppt/.pptx)'),
        ('pdf', 'PDF文档 (.pdf)'),
        ('txt', '纯文本 (.txt)'),
        ('other', '其他格式')
    ]
    type = models.CharField(
        max_length=10, 
        choices=DOCUMENT_TYPES, 
        default='docx', 
        verbose_name="文档类型", 
        help_text="文档文件类型"
    )
    
    # 文档简介
    about_text = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="文档简介", 
        help_text="文档内容简要描述"
    )
    
    # 功能开关
    transtask = models.BooleanField(
        default=True, 
        verbose_name="需要翻译", 
        help_text="是否需要进行翻译任务"
    )
    graphtask = models.BooleanField(
        default=False, 
        verbose_name="知识图谱", 
        help_text="是否生成知识图谱"
    )
    share = models.BooleanField(
        default=False, 
        verbose_name="是否分享", 
        help_text="是否允许分享给其他用户"
    )
    userversion = models.BooleanField(
        default=True, 
        verbose_name="版本控制", 
        help_text="是否启用版本控制功能"
    )
    
    # 翻译相关字段
    status = models.CharField(
        max_length=20, 
        choices=DOCXFILE_STATUS, 
        default="uploaded", 
        verbose_name="翻译状态", 
        help_text="文档翻译处理状态"
    )
    paragraph_count = models.IntegerField(default=0, verbose_name="段落数量", help_text="文档段落总数")
    word_count = models.IntegerField(default=0, verbose_name="字数统计", help_text="文档总字数")
    page_count = models.IntegerField(default=0, verbose_name="页数统计", help_text="文档页数")
    
    # 语言设置
    source_language = models.CharField(max_length=10, default="auto", verbose_name="源语言", help_text="原文语言代码")
    target_language = models.CharField(max_length=10, default="zh", verbose_name="目标语言", help_text="目标翻译语言代码")
    
    # 处理信息
    processing_time = models.FloatField(default=0, verbose_name="处理时间", help_text="翻译处理耗时(秒)")
    error_message = models.TextField(blank=True, null=True, verbose_name="错误信息", help_text="处理过程中的错误信息")
    
    # 翻译结果
    translated_path = models.CharField(max_length=500, blank=True, null=True, verbose_name="翻译后文件路径", help_text="翻译后文档存储路径")
    translated_filename = models.CharField(max_length=255, blank=True, null=True, verbose_name="翻译后文件名", help_text="翻译后文件名")
    
    class Meta:
        db_table = table_prefix + "docxfile"
        verbose_name = "DOCX文档翻译"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["type"]),
            models.Index(fields=["transtask", "graphtask", "share"]),
            models.Index(fields=["source_language", "target_language"]),
            models.Index(fields=["create_datetime"]),
        ]


class Docxpages(CoreModel):
    """
    文档页面内容管理
    用于存储文档中每个页面的详细内容和翻译结果
    """
    # 关联文档
    docxfile = models.ForeignKey(
        Docxfile,
        on_delete=models.CASCADE,
        related_name='pages',
        verbose_name="所属文档",
        help_text="关联的文档文件"
    )
    
    # 页面基本信息
    page_number = models.IntegerField(
        verbose_name="页码",
        help_text="文档中的页码序号"
    )
    
    # 原始页面内容
    original_title = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="原始标题",
        help_text="页面标题或章节标题"
    )
    
    original_content = models.TextField(
        blank=True,
        null=True,
        verbose_name="原始内容",
        help_text="页面原始文本内容"
    )
    
    # 翻译后内容
    translated_title = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="翻译后标题",
        help_text="翻译后的页面标题"
    )
    
    translated_content = models.TextField(
        blank=True,
        null=True,
        verbose_name="翻译后内容",
        help_text="翻译后的页面内容"
    )
    
    # 内容统计
    char_count = models.IntegerField(
        default=0,
        verbose_name="字符数",
        help_text="原始内容字符数量"
    )
    
    translated_char_count = models.IntegerField(
        default=0,
        verbose_name="翻译后字符数",
        help_text="翻译后内容字符数量"
    )
    
    paragraph_count = models.IntegerField(
        default=0,
        verbose_name="段落数",
        help_text="页面内段落数量"
    )
    
    # 处理状态
    PAGE_STATUS = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '处理完成'),
        ('failed', '处理失败'),
        ('skipped', '跳过')
    ]
    
    status = models.CharField(
        max_length=20,
        choices=PAGE_STATUS,
        default='pending',
        verbose_name="处理状态",
        help_text="页面内容处理状态"
    )
    
    # 处理信息
    processing_order = models.IntegerField(
        default=0,
        verbose_name="处理顺序",
        help_text="页面处理的先后顺序"
    )
    
    processing_time = models.FloatField(
        default=0,
        verbose_name="处理时间",
        help_text="页面处理耗时(秒)"
    )
    
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name="错误信息",
        help_text="页面处理过程中的错误信息"
    )
    
    # 内容预览和索引
    preview_text = models.TextField(
        blank=True,
        null=True,
        verbose_name="预览文本",
        help_text="内容预览片段，用于快速浏览"
    )
    
    content_hash = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name="内容哈希",
        help_text="内容MD5哈希值，用于去重和完整性校验"
    )
    
    # 知识图谱相关数据
    entities = models.JSONField(
        blank=True,
        null=True,
        verbose_name="实体列表",
        help_text="页面中提取的实体信息(JSON格式)"
    )
    
    keywords = models.JSONField(
        blank=True,
        null=True,
        verbose_name="关键词",
        help_text="页面关键词列表(JSON格式)"
    )
    
    summary = models.TextField(
        blank=True,
        null=True,
        verbose_name="摘要",
        help_text="页面内容摘要"
    )
    
    # 版本控制
    version = models.IntegerField(
        default=1,
        verbose_name="版本号",
        help_text="内容版本号"
    )
    
    parent_page = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='versions',
        verbose_name="父版本",
        help_text="上一版本页面，用于版本追踪"
    )
    
    # 元数据
    page_metadata = models.JSONField(
        blank=True,
        null=True,
        verbose_name="页面元数据",
        help_text="页面相关的元数据信息(JSON格式)"
    )
    
    class Meta:
        db_table = table_prefix + "docxpages"
        verbose_name = "文档页面内容"
        verbose_name_plural = verbose_name
        ordering = ["docxfile", "page_number", "-create_datetime"]
        unique_together = [["docxfile", "page_number", "version"]]
        indexes = [
            models.Index(fields=["docxfile", "page_number"]),
            models.Index(fields=["docxfile", "status"]),
            models.Index(fields=["status", "processing_order"]),
            models.Index(fields=["content_hash"]),
            models.Index(fields=["create_datetime"]),
            models.Index(fields=["version"]),
        ]
    
    def __str__(self):
        return f"{self.docxfile.original_name} - 第{self.page_number}页"
    
    def save(self, *args, **kwargs):
        """
        重写save方法，自动计算字符数和生成哈希值
        """
        # 计算字符数
        if self.original_content:
            self.char_count = len(self.original_content)
        
        if self.translated_content:
            self.translated_char_count = len(self.translated_content)
        
        # 生成内容哈希
        if self.original_content and not self.content_hash:
            self.content_hash = hashlib.md5(self.original_content.encode('utf-8')).hexdigest()
        
        # 生成预览文本
        if self.original_content and not self.preview_text:
            # 取前200个字符作为预览
            preview = self.original_content[:200]
            if len(self.original_content) > 200:
                preview += "..."
            self.preview_text = preview
        
        super().save(*args, **kwargs)
    
    def get_content_preview(self, length=100):
        """
        获取内容预览
        """
        content = self.translated_content or self.original_content or ""
        if len(content) <= length:
            return content
        return content[:length] + "..."
    
    def is_translated(self):
        """
        检查页面是否已翻译
        """
        return bool(self.translated_content and self.status == 'completed')
    
    def get_processing_progress(self):
        """
        获取处理进度信息
        """
        return {
            'page_number': self.page_number,
            'status': self.status,
            'char_count': self.char_count,
            'translated_char_count': self.translated_char_count,
            'paragraph_count': self.paragraph_count,
            'processing_time': self.processing_time,
            'has_entities': bool(self.entities),
            'has_keywords': bool(self.keywords),
            'has_summary': bool(self.summary)
        }


class Transdicts(CoreModel):
    CATEGORY_CHOICES = (
        ('通用', '通用'),
        ('飞行', '飞行'),
        ('行业', '行业'),
        ('机械', '机械'),
        ('维保', '维保'),
        ('文档', '文档'),
        ('其他', '其他'),
    )
    pcate = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="类别", default='通用', null=False, blank=False, help_text="词条类别")
    cn = models.CharField(max_length=200, verbose_name="中文", help_text="词条中文")
    en = models.CharField(max_length=200, verbose_name="英文", help_text="词条英文")
    infos = models.CharField(max_length=200, verbose_name="信息", null=True, blank=True, help_text="额外信息")
    note = models.CharField(max_length=200, verbose_name="备注", null=True, blank=True, help_text="备注信息")
    ainote = models.CharField(max_length=200, verbose_name="AI备注", null=True, blank=True, help_text="备注信息")
    weight = models.FloatField(verbose_name="权重", default=3.0, help_text="权重")

    class Meta:
        db_table = table_prefix + "transdicts"
        verbose_name = "翻译字典"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)