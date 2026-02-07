# -*- coding: utf-8 -*-
"""
Word文档处理模块
提供wordwork函数用于处理上传的Word文档
"""
from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Pt, RGBColor
from datetime import datetime
import os
import uuid
import tempfile
import re


def copy_images_to_new_doc(source_doc, target_doc):
    """
    从源文档复制所有图片到目标文档
    """
    # 获取源文档中的所有关系
    for rel_id, relationship in source_doc.part.rels.items():
        if relationship.reltype == 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image':
            # 获取图片数据
            image_part = relationship.target_part
            image_data = image_part.blob
            
            # 创建临时文件来保存图片
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(image_data)
                temp_path = temp_file.name
            
            try:
                # 将图片添加到目标文档
                target_doc.add_paragraph()  # 添加空行以分隔
                target_doc.add_picture(temp_path)
            finally:
                # 清理临时文件
                os.unlink(temp_path)


def trans(text, source_lang='zh', target_lang='en'):
    """
    翻译文本，将文本按句子分割并逐句翻译
    :param text: 待翻译的文本
    :param source_lang: 源语言
    :param target_lang: 目标语言
    :return: 翻译后的文本
    """
    from .translateview import TranslateView
    import re
    
    # 默认情况下，如果未指定源语言和目标语言，则使用预设值
    # 此处假设已正确设置，无需再次检测
    
    # 按句子分割文本，保留标点符号
    # 匹配中文句号、英文句号、问号、感叹号等作为句子分隔符
    sentences = re.split(r'([。！？.!?])', text)
    
    # 重新组合句子（将标点符号与前面的句子合并）
    combined_sentences = []
    for i in range(0, len(sentences)-1, 2):
        sentence = sentences[i]
        punctuation = sentences[i+1] if i+1 < len(sentences) else ""
        if sentence.strip():  # 忽略空句子
            combined_sentences.append(sentence + punctuation)
    
    # 逐句翻译
    translated_sentences = []
    for sentence in combined_sentences:
        if sentence.strip():
            # 创建TranslateView实例来使用其翻译方法
            translator = TranslateView()
            try:
                # 直接调用翻译方法
                translated_sentence = translator.translate_from_db(sentence, source_lang, target_lang)
                if not translated_sentence:
                    translated_sentence = sentence  # 翻译失败则保持原句
            except Exception as e:
                print(f"翻译句子时出错: {sentence[:50]}..., 错误: {str(e)}")
                translated_sentence = sentence  # 出错则保持原句
        else:
            translated_sentence = sentence  # 空句子保持不变
        
        translated_sentences.append(translated_sentence)
    
    # 组合翻译后的句子
    return ''.join(translated_sentences)


 

def process_word_with_format(input_path, output_path, source_lang='zh', target_lang='en'):
    """
    读取Word文档，保留格式和层级结构，修改文本后写入新文档
    :param input_path: 原Word文档路径（.docx）
    :param output_path: 新Word文档保存路径
    :param source_lang: 源语言
    :param target_lang: 目标语言
    """
    # 加载原文档
    doc = Document(input_path)
    
    # 2. 遍历所有段落，保留格式并修改内容
    for para in doc.paragraphs:
        # 跳过空段落
        if not para.text.strip():
            continue
        
        # 使用翻译函数翻译段落文本
        original_text = para.text
        modified_text = trans(original_text, source_lang, target_lang)  # 调用上面定义的trans函数
        print(f"原文本: {original_text}")
        print(f"新文本: {modified_text}")
 

        # 关键：保留原有格式，逐个运行块替换文本
        # 清空段落但保留第一个运行块的格式
        if para.runs:
            # 保留第一个运行块的格式
            first_run = para.runs[0]
            original_format = {
                'bold': first_run.bold,
                'italic': first_run.italic,
                'underline': first_run.underline,
                'font_name': first_run.font.name if first_run.font.name else None,
                'font_size': first_run.font.size,
                'color': first_run.font.color.rgb if first_run.font.color and first_run.font.color.rgb else None
            }
            
            # 清空段落内容
            para.clear()
            
            # 添加新文本，应用原始格式
            new_run = para.add_run(modified_text)
            new_run.bold = original_format['bold']
            new_run.italic = original_format['italic']
            new_run.underline = original_format['underline']
            if original_format['font_name']:
                new_run.font.name = original_format['font_name']
            if original_format['font_size']:
                new_run.font.size = original_format['font_size']
            if original_format['color']:
                new_run.font.color.rgb = original_format['color']
        else:
            # 如果没有运行块，直接设置文本
            para.text = modified_text
        
    # 3. 遍历所有表格（如果有表格，也保留格式修改）
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    if para.text.strip():
                        # 翻译表格中的文本
                        original_text = para.text
                        print(f"表格原文本: {original_text}")
                        modified_text = trans(original_text, source_lang, target_lang)
                        if modified_text == "" or not modified_text:
                            modified_text = original_text
                        print(f"表格新文本: {modified_text}")
                        
                        # 保留原有格式
                        if para.runs:
                            # 保留第一个运行块的格式
                            first_run = para.runs[0]
                            original_format = {
                                'bold': first_run.bold,
                                'italic': first_run.italic,
                                'underline': first_run.underline,
                                'font_name': first_run.font.name if first_run.font.name else None,
                                'font_size': first_run.font.size,
                                'color': first_run.font.color.rgb if first_run.font.color and first_run.font.color.rgb else None
                            }
                            
                            # 清空段落内容
                            para.clear()
                            
                            # 添加新文本，应用原始格式
                            new_run = para.add_run(modified_text)
                            new_run.bold = original_format['bold']
                            new_run.italic = original_format['italic']
                            new_run.underline = original_format['underline']
                            if original_format['font_name']:
                                new_run.font.name = original_format['font_name']
                            if original_format['font_size']:
                                new_run.font.size = original_format['font_size']
                            if original_format['color']:
                                new_run.font.color.rgb = original_format['color']
                        else:
                            # 如果没有运行块，直接设置文本
                            para.text = modified_text
    
    # 4. 处理文档中的图片
    copy_images_to_new_doc(Document(input_path), doc)
    
    # 5. 保存新文档（保留所有原格式+修改后的内容）
    doc.save(output_path)


def wordwork(input_path, source_lang='zh', target_lang='en'):
    """
    处理Word文件的主函数
    :param input_path: 服务器上保存的原始文件路径
    :param source_lang: 源语言
    :param target_lang: 目标语言
    :return: 处理后的新文件路径
    """
    # 生成新文件名（使用时间戳+UUID防止重名）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]  # 取UUID的前8位
    
    # 获取原始文件的目录和名称
    dir_path = os.path.dirname(input_path)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    extension = os.path.splitext(input_path)[1]
    
    # 生成新文件名
    new_filename = f"{base_name}_processed_{timestamp}_{unique_id}{extension}"
    output_path = os.path.join(dir_path, new_filename)
    
    # 处理文档
    process_word_with_format(input_path, output_path, source_lang, target_lang)
    
    return output_path