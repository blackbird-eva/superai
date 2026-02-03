# -*- coding: utf-8 -*-
"""
文本翻译接口
Created on: 2026-02-03
"""
import requests
import json
import logging

from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from django.conf import settings

from dvadmin.system.models import Transdicts
from dvadmin.utils.json_response import SuccessResponse, ErrorResponse

logger = logging.getLogger(__name__)


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
        从翻译字典中查找翻译，如果找不到则使用大模型翻译
        """
        try:
            # 第一步：尝试从数据库中查找翻译
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

            # 第二步：数据库中未找到，使用大模型翻译
            logger.info(f"数据库未找到翻译，使用大模型翻译: {text[:50]}...")
            translated_text = self.translate_with_llm(text, source_lang, target_lang)

            # 第三步：可选：将翻译结果保存到数据库
            if translated_text and False :
                self._save_translation_to_db(text, translated_text, source_lang, target_lang)

            return translated_text

        except Exception as e:
            logger.error(f"翻译查询错误: {str(e)}")
            return None

    def translate_with_llm(self, text, source_lang, target_lang):
        """
        使用大模型进行翻译（参考 en.py 的实现）
        """
        # 从配置中读取大模型设置，提供默认值
        llm_base_url = getattr(settings, 'LLM_BASE_URL', 'http://localhost:1234/v1')
        llm_api_key = getattr(settings, 'LLM_API_KEY', 'not-needed')
        llm_model = getattr(settings, 'LLM_MODEL', 'hy-mt1.5-7b')
        llm_temperature = getattr(settings, 'LLM_TEMPERATURE', 0.8)
        llm_max_tokens = getattr(settings, 'LLM_MAX_TOKENS', 700)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {llm_api_key}"
        }

        # 获取术语词典
        cn_en_dicts = self._get_term_dict()
        print( "cn_en_dicts:", cn_en_dicts)
        # 构建术语词典说明
        dict_instruction = ""
        if cn_en_dicts:
            dict_instruction = "翻译时请优先使用以下术语词典中的翻译：\n"
            for cn, en in cn_en_dicts.items():
                dict_instruction += f"  - {cn} → {en}\n"
            dict_instruction += "\n"

        # 构建翻译提示词
        # 根据源语言和目标语言生成相应的翻译指令
        if source_lang == 'zh' and target_lang == 'en':
            translation_prompt = f"请将以下中文翻译成英文，只输出英文翻译结果，不要添加任何其他内容：\n\n{dict_instruction}原文：\n{text}"
        elif source_lang == 'en' and target_lang == 'zh':
            translation_prompt = f"请将以下英文翻译成中文，只输出中文翻译结果，不要添加任何其他内容：\n\n原文：\n{text}"
        else:
            # 默认使用中文到英文
            translation_prompt = f"请将以下文本翻译成英文，只输出英文翻译结果，不要添加任何其他内容：\n\n{dict_instruction}原文：\n{text}"

        url = f"{llm_base_url}/responses"
        payload = {
            "model": llm_model,
            "input": translation_prompt,
            "max_tokens": llm_max_tokens,
            "temperature": llm_temperature
        }

        try:
            logger.info(f"调用大模型翻译: {llm_base_url}/responses")
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            logger.debug(f"大模型返回结果: {json.dumps(result, ensure_ascii=False)[:500]}")

            # 尝试解析响应（参考 en.py 的逻辑）
            if "output" in result and len(result["output"]) > 0:
                output = result["output"][0]
                if "content" in output and len(output["content"]) > 0:
                    content = output["content"][0]
                    if "text" in content:
                        return content["text"].strip()
            elif "response" in result:
                return result["response"].strip()
            elif "choices" in result and len(result["choices"]) > 0:
                if "text" in result["choices"][0]:
                    return result["choices"][0]["text"].strip()
                elif "message" in result["choices"][0]:
                    return result["choices"][0]["message"]["content"].strip()
            else:
                logger.warning(f"无法解析大模型响应格式: {json.dumps(result, ensure_ascii=False)}")
                return None

        except requests.exceptions.Timeout:
            logger.error("大模型翻译请求超时")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"大模型翻译请求错误: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"大模型翻译发生错误: {str(e)}")
            return None

        return None

    def _get_term_dict(self):
        """
        从数据库中获取术语词典（用于大模型翻译时参考）
        """
        try:
            # 获取所有术语词典记录，按权重从大到小排列（权重高的优先使用）
            dicts = Transdicts.objects.all().order_by('-weight')[:100]  # 限制数量，避免过长
            cn_en_dict = {d.cn: d.en for d in dicts if d.cn and d.en}
            return cn_en_dict
        except Exception as e:
            logger.error(f"获取术语词典失败: {str(e)}")
            return {}

    def _save_translation_to_db(self, original_text, translated_text, source_lang, target_lang):
        """
        将翻译结果保存到数据库（可选功能）
        """
        try:
            # 检查是否已存在
            if source_lang == 'zh' and target_lang == 'en':
                if Transdicts.objects.filter(cn=original_text).exists():
                    return  # 已存在，不重复保存

                # 保存新记录
                Transdicts.objects.create(
                    cn=original_text,
                    en=translated_text,
                    pcate='其他'  # 默认类别
                )
                logger.info(f"翻译结果已保存到数据库: {original_text[:30]}... → {translated_text[:30]}...")

            elif source_lang == 'en' and target_lang == 'zh':
                if Transdicts.objects.filter(en=original_text).exists():
                    return  # 已存在，不重复保存

                # 保存新记录
                Transdicts.objects.create(
                    cn=translated_text,
                    en=original_text,
                    pcate='其他'  # 默认类别
                )
                logger.info(f"翻译结果已保存到数据库: {original_text[:30]}... → {translated_text[:30]}...")

        except Exception as e:
            logger.error(f"保存翻译结果到数据库失败: {str(e)}")
