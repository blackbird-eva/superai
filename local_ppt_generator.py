#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
本地PPT生成器 - 替代Coze API的解决方案
直接从文本内容生成专业PPT，无需外部API
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
import uuid

# 检查依赖
required_packages = {
    'pptx': 'python-pptx',
    'jieba': 'jieba'  # 中文分词
}

missing_packages = []
for module, package in required_packages.items():
    try:
        __import__(module)
    except ImportError:
        missing_packages.append(package)

if missing_packages:
    print(f"⚠️  缺少依赖包: {', '.join(missing_packages)}")
    print(f"请运行: pip install {' '.join(missing_packages)}")

from pptx import Presentation
from pptx.util import Inches, Pt, Cm
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

try:
    import jieba
    import jieba.posseg as pseg
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False

class LocalPPTGenerator:
    """本地PPT生成器 - 智能从文本生成PPT"""
    
    def __init__(self, output_dir="generated_ppts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 主题配置
        self.themes = {
            'business': {
                'bg_colors': [RGBColor(245, 245, 245), RGBColor(255, 255, 255)],
                'title_color': RGBColor(0, 51, 102),
                'content_color': RGBColor(51, 51, 51),
                'accent_color': RGBColor(0, 102, 204)
            },
            'tech': {
                'bg_colors': [RGBColor(240, 245, 255), RGBColor(250, 250, 255)],
                'title_color': RGBColor(0, 82, 204),
                'content_color': RGBColor(64, 64, 64),
                'accent_color': RGBColor(0, 150, 255)
            },
            'education': {
                'bg_colors': [RGBColor(255, 253, 245), RGBColor(255, 255, 250)],
                'title_color': RGBColor(153, 102, 0),
                'content_color': RGBColor(77, 77, 77),
                'accent_color': RGBColor(255, 153, 0)
            },
            'creative': {
                'bg_colors': [RGBColor(253, 245, 255), RGBColor(255, 250, 250)],
                'title_color': RGBColor(153, 0, 153),
                'content_color': RGBColor(51, 51, 51),
                'accent_color': RGBColor(255, 51, 153)
            },
            'academic': {
                'bg_colors': [RGBColor(250, 250, 250), RGBColor(255, 255, 255)],
                'title_color': RGBColor(0, 0, 0),
                'content_color': RGBColor(51, 51, 51),
                'accent_color': RGBColor(102, 102, 102)
            }
        }
        
        print(f"🎨 本地PPT生成器初始化完成")
        print(f"📁 输出目录: {self.output_dir.absolute()}")
    
    def extract_keywords(self, text, top_n=10):
        """提取关键词（简化版，不使用jieba也可用）"""
        if JIEBA_AVAILABLE:
            # 使用jieba进行中文分词和关键词提取
            words = pseg.cut(text)
            # 过滤名词、动词，去除停用词
            keywords = []
            for word, flag in words:
                if len(word) > 1 and flag.startswith(('n', 'v', 'a')):
                    keywords.append(word)
            
            # 统计词频
            from collections import Counter
            word_freq = Counter(keywords)
            return [word for word, count in word_freq.most_common(top_n)]
        else:
            # 简单的关键词提取（按长度和频率）
            # 移除标点符号和数字
            cleaned_text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z]', ' ', text)
            words = cleaned_text.split()
            
            # 过滤短词和常见词
            stop_words = {'的', '是', '在', '有', '和', '与', '或', '及', '等', '这', '那', '一', '个'}
            keywords = [word for word in words if len(word) > 1 and word not in stop_words]
            
            # 统计频率
            from collections import Counter
            word_freq = Counter(keywords)
            return [word for word, count in word_freq.most_common(top_n)]
    
    def parse_content_structure(self, text):
        """解析文本结构，提取标题和内容"""
        slides_content = []
        
        # 按段落分割
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # 第一页作为标题页
        if paragraphs:
            title_match = re.match(r'^[#*]*(.+?)[#*]*$', paragraphs[0])
            title = title_match.group(1) if title_match else paragraphs[0][:50]
            subtitle = f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            slides_content.append({
                'type': 'title',
                'title': title,
                'subtitle': subtitle,
                'content': []
            })
        
        # 解析其他页面
        for para in paragraphs[1:]:
            # 检查是否是标题格式
            title_match = re.match(r'^[#*]+\s*(.+)$', para)
            if title_match:
                # 新页面的开始
                slide_title = title_match.group(1)
                slides_content.append({
                    'type': 'content',
                    'title': slide_title,
                    'subtitle': '',
                    'content': []
                })
            else:
                # 添加到当前页面内容
                if slides_content and slides_content[-1]['type'] == 'content':
                    # 解析要点列表
                    lines = para.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line.startswith(('-', '•', '1.', '2.', '3.', '4.', '5.')):
                            # 移除列表标记
                            clean_line = re.sub(r'^[-•\d+\.\s]+', '', line)
                            slides_content[-1]['content'].append(clean_line)
                        elif line:
                            slides_content[-1]['content'].append(line)
        
        # 如果没有解析出内容页面，创建默认页面
        if len(slides_content) <= 1:
            slides_content.append({
                'type': 'content',
                'title': '内容概览',
                'subtitle': '',
                'content': ['基于输入文本自动生成的内容要点', '智能提取的关键信息', '结构化展示的核心观点']
            })
        
        return slides_content
    
    def create_title_slide(self, prs, slide_data, theme='business'):
        """创建标题页"""
        slide_layout = prs.slide_layouts[0]  # 标题页布局
        slide = prs.slides.add_slide(slide_layout)
        
        # 设置背景
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = theme_config['bg_colors'][0]
        
        # 获取标题和副标题占位符
        title_placeholder = slide.shapes.title
        subtitle_placeholder = slide.placeholders[1]
        
        # 设置标题
        title_placeholder.text = slide_data['title']
        title_frame = title_placeholder.text_frame.paragraphs[0]
        title_frame.font.name = '微软雅黑'
        title_frame.font.size = Pt(32)
        title_frame.font.color.rgb = theme_config['title_color']
        title_frame.alignment = PP_ALIGN.CENTER
        
        # 设置副标题
        if slide_data['subtitle']:
            subtitle_placeholder.text = slide_data['subtitle']
            subtitle_frame = subtitle_placeholder.text_frame.paragraphs[0]
            subtitle_frame.font.name = '微软雅黑'
            subtitle_frame.font.size = Pt(16)
            subtitle_frame.font.color.rgb = theme_config['content_color']
            subtitle_frame.alignment = PP_ALIGN.CENTER
        
        return slide
    
    def create_content_slide(self, prs, slide_data, theme='business'):
        """创建内容页"""
        slide_layout = prs.slide_layouts[1]  # 标题和内容布局
        slide = prs.slides.add_slide(slide_layout)
        
        # 设置背景
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = theme_config['bg_colors'][1]
        
        # 设置标题
        title_placeholder = slide.shapes.title
        title_placeholder.text = slide_data['title']
        title_frame = title_placeholder.text_frame.paragraphs[0]
        title_frame.font.name = '微软雅黑'
        title_frame.font.size = Pt(24)
        title_frame.font.color.rgb = theme_config['title_color']
        
        # 设置内容
        if slide_data['content']:
            content_placeholder = slide.placeholders[1]
            tf = content_placeholder.text_frame
            tf.clear()
            
            for i, content_item in enumerate(slide_data['content'][:6]):  # 最多6个要点
                p = tf.add_paragraph()
                p.text = f"• {content_item}"
                p.font.name = '微软雅黑'
                p.font.size = Pt(16)
                p.font.color.rgb = theme_config['content_color']
                p.space_after = Pt(8)
        
        return slide
    
    def generate_from_text(self, text, title="智能生成PPT", theme='business', slide_count=8):
        """从文本生成PPT"""
        global theme_config
        theme_config = self.themes.get(theme, self.themes['business'])
        
        print(f"🚀 开始生成PPT...")
        print(f"📝 主题: {theme}")
        print(f"📊 目标页数: {slide_count}")
        
        # 提取关键词
        keywords = self.extract_keywords(text)
        print(f"🔍 提取关键词: {', '.join(keywords[:5])}")
        
        # 解析内容结构
        slides_content = self.parse_content_structure(text)
        
        # 限制幻灯片数量
        slides_content = slides_content[:slide_count+1]  # +1 因为第一页是标题页
        
        # 创建PPT
        prs = Presentation()
        
        # 生成幻灯片
        for i, slide_data in enumerate(slides_content):
            print(f"   📄 生成第{i+1}页: {slide_data['title'][:30]}...")
            
            if slide_data['type'] == 'title':
                self.create_title_slide(prs, slide_data, theme)
            else:
                self.create_content_slide(prs, slide_data, theme)
        
        # 保存文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{title}_{theme}_{timestamp}.pptx"
        filepath = self.output_dir / filename
        
        prs.save(filepath)
        file_size = filepath.stat().st_size
        
        print(f"✅ PPT生成完成!")
        print(f"📁 文件: {filename}")
        print(f"💾 大小: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        return {
            'success': True,
            'filepath': str(filepath),
            'filename': filename,
            'slide_count': len(slides_content),
            'file_size': file_size,
            'keywords': keywords,
            'theme': theme,
            'generation_time': datetime.now().isoformat()
        }
    
    def generate_from_template(self, template_type='business_report', title="报告PPT", theme='business'):
        """从模板生成PPT"""
        
        templates = {
            'business_report': {
                'title': title,
                'slides': [
                    {'type': 'title', 'title': title, 'subtitle': f'商业报告 - {datetime.now().strftime("%Y年%m月")}'},
                    {'type': 'content', 'title': '执行摘要', 'content': ['核心发现概述', '关键数据指标', '主要结论和建议']},
                    {'type': 'content', 'title': '市场分析', 'content': ['市场规模与增长', '竞争格局分析', '目标客户群体', '市场机会识别']},
                    {'type': 'content', 'title': '业务现状', 'content': ['当前业绩表现', '运营效率分析', '资源利用情况', '存在问题识别']},
                    {'type': 'content', 'title': '战略建议', 'content': ['短期行动计划', '中长期发展规划', '资源配置策略', '风险控制措施']},
                    {'type': 'content', 'title': '总结展望', 'content': ['核心要点回顾', '预期成果展望', '下一步行动安排']}
                ]
            },
            'tech_presentation': {
                'title': title,
                'slides': [
                    {'type': 'title', 'title': title, 'subtitle': f'技术方案演示 - {datetime.now().strftime("%Y年%m月")}'},
                    {'type': 'content', 'title': '项目背景', 'content': ['业务需求分析', '技术挑战识别', '解决方案概述']},
                    {'type': 'content', 'title': '架构设计', 'content': ['整体架构图', '核心组件说明', '技术栈选择理由']},
                    {'type': 'content', 'title': '关键特性', 'content': ['功能特性介绍', '性能指标', '安全考虑']},
                    {'type': 'content', 'title': '实施计划', 'content': ['开发里程碑', '测试策略', '部署方案']},
                    {'type': 'content', 'title': 'Q&A', 'content': ['常见问题解答', '技术支持联系方式']}
                ]
            },
            'education_training': {
                'title': title,
                'slides': [
                    {'type': 'title', 'title': title, 'subtitle': f'培训课件 - {datetime.now().strftime("%Y年%m月")}'},
                    {'type': 'content', 'title': '学习目标', 'content': ['知识目标', '技能目标', '态度目标']},
                    {'type': 'content', 'title': '核心概念', 'content': ['基本概念解释', '重要原理阐述', '相关理论介绍']},
                    {'type': 'content', 'title': '实践案例', 'content': ['案例分析', '经验分享', '最佳实践']},
                    {'type': 'content', 'title': '互动练习', 'content': ['练习题', '讨论话题', '实操任务']},
                    {'type': 'content', 'title': '总结回顾', 'content': ['重点内容回顾', '学习成果检验', '后续学习建议']}
                ]
            }
        }
        
        template = templates.get(template_type, templates['business_report'])
        template['title'] = title
        
        global theme_config
        theme_config = self.themes.get(theme, self.themes['business'])
        
        # 创建PPT
        prs = Presentation()
        
        for i, slide_data in enumerate(template['slides']):
            print(f"   📄 生成第{i+1}页: {slide_data['title']}")
            
            if slide_data['type'] == 'title':
                self.create_title_slide(prs, slide_data, theme)
            else:
                self.create_content_slide(prs, slide_data, theme)
        
        # 保存文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{template_type}_{theme}_{timestamp}.pptx"
        filepath = self.output_dir / filename
        
        prs.save(filepath)
        
        return {
            'success': True,
            'filepath': str(filepath),
            'filename': filename,
            'slide_count': len(template['slides']),
            'template_type': template_type,
            'theme': theme
        }

def main():
    """演示本地PPT生成器"""
    generator = LocalPPTGenerator()
    
    print("🎯 本地PPT生成器演示")
    print("=" * 50)
    
    # 示例1: 从文本生成
    sample_text = """
# 人工智能发展趋势分析

## 技术突破与应用前景

人工智能技术正在经历第三次发展浪潮，深度学习、自然语言处理、计算机视觉等领域取得重大突破。

- 大模型技术推动AI能力边界不断扩展
- 多模态AI实现文本、图像、语音的统一理解
- AI在医疗、教育、金融等行业应用日趋成熟

## 产业发展现状

全球AI产业规模持续快速增长，中国AI企业数量位居世界前列。

- 2023年全球AI市场规模达到5000亿美元
- 中国AI核心产业规模超过5000亿元人民币
- 涌现出一批具有国际竞争力的AI领军企业

## 面临的挑战与机遇

技术发展带来巨大机遇，同时也面临数据安全、伦理治理等挑战。

- 需要建立完善的AI治理体系
- 加强国际合作与标准制定
- 培养AI高端人才队伍
"""
    
    print("\n📝 示例1: 从文本生成PPT")
    result1 = generator.generate_from_text(
        text=sample_text,
        title="AI发展趋势分析",
        theme='tech',
        slide_count=6
    )
    
    # 示例2: 从模板生成
    print("\n📋 示例2: 从模板生成PPT")
    result2 = generator.generate_from_template(
        template_type='business_report',
        title='季度业务分析报告',
        theme='business'
    )
    
    print("\n🎉 演示完成!")
    print(f"生成的文件保存在: {generator.output_dir.absolute()}")

if __name__ == "__main__":
    main()
