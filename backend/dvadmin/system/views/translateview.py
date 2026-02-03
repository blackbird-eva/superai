# -*- coding: utf-8 -*-
"""
文本翻译接口
Created on: 2026-02-03
"""
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer

from dvadmin.system.models import Transdicts
from dvadmin.utils.json_response import SuccessResponse, ErrorResponse


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
