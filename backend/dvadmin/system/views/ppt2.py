"""
使用 python-pptx 基于模板生成班会上发言的 PPT
包含5页幻灯片，使用 ppt.pptx 作为模板
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
import os
from datetime import datetime


def create_presentation():
    """创建班会上发言的PPT，基于模板"""

    # 检查模板文件是否存在
    template_file = "pptx.pptx"
    if os.path.exists(template_file):
        print(f"📄 使用模板文件: {template_file}")
        # 仅加载模板以参考其样式，不复制其幻灯片
        template_prs = Presentation(template_file)
        prs = Presentation()
        # 确保尺寸一致（16:9）
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(5.625)
    else:
        print(f"⚠️ 模板文件 {template_file} 不存在，使用默认模板")
        prs = Presentation()
        # 设置幻灯片大小为16:9
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(5.625)

    # ============ 第1页：标题页 ============
    slide_layout = prs.slide_layouts[6]  # 使用空白布局 for better customization
    slide1 = prs.slides.add_slide(slide_layout)

    # 添加背景图片 (使用文件夹下的 bg.png)
    bg_image_path = "bg.png"
    if os.path.exists(bg_image_path):
        slide1.shapes.add_picture(bg_image_path, Inches(0), Inches(0), 
                                 width=prs.slide_width, height=prs.slide_height)
        print("✅ 成功添加背景图片到第一页")
    else:
        print("⚠️ 未找到 bg.png 背景图片")

    # 添加标题
    title_box = slide1.shapes.add_textbox(Inches(1), Inches(1.4), Inches(8), Inches(1.2))
    title_frame = title_box.text_frame
    title_frame.text = "班会上发言"
    title_frame.paragraphs[0].font.size = Pt(36)
    title_frame.paragraphs[0].font.bold = True
    title_frame.paragraphs[0].font.name = 'SimHei'  # 黑体
    title_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)  # 白色字体
    title_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # 添加副标题
    subtitle_box = slide1.shapes.add_textbox(Inches(1), Inches(2.4), Inches(8), Inches(1))
    subtitle_frame = subtitle_box.text_frame
    subtitle_frame.text = "Python编程语言学习小组"
    subtitle_frame.paragraphs[0].font.size = Pt(22)
    subtitle_frame.paragraphs[0].font.name = 'SimHei'  # 黑体
    subtitle_frame.paragraphs[0].font.color.rgb = RGBColor(255,255, 255)  # 浅蓝色字体
    subtitle_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    subtitle_frame.word_wrap = True

    # ============ 第2页：学习成果展示 ============
    slide_layout = prs.slide_layouts[6]  # 使用空白布局
    slide2 = prs.slides.add_slide(slide_layout)

    # 添加背景图片 (使用文件夹下的 bg2.png)
    bg2_image_path = "bg2.png"
    if os.path.exists(bg2_image_path):
        slide2.shapes.add_picture(bg2_image_path, Inches(0), Inches(0), 
                                 width=prs.slide_width, height=prs.slide_height)
        print("✅ 成功添加背景图片到第二页")
    else:
        print("⚠️ 未找到 bg2.png 背景图片")

    # 添加标题框
    title_box = slide2.shapes.add_textbox(Inches(0.5), Inches(0.8), Inches(9), Inches(1))
    title_frame = title_box.text_frame
    title_frame.text = "📊 本学期学习成果"
    title_frame.paragraphs[0].font.size = Pt(32)
    title_frame.paragraphs[0].font.bold = True
    title_frame.paragraphs[0].font.color.rgb = RGBColor(0, 51, 102)
    title_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    # 添加内容列表
    content_box = slide2.shapes.add_textbox(Inches(1), Inches(1.5), Inches(8), Inches(3))
    text_frame = content_box.text_frame
    text_frame.word_wrap = True

    # 添加列表项
    points = [
        "✅ 完成了Python基础语法学习",
        "✅ 掌握了常用的数据结构（列表、字典、元组等）",
        "✅ 学习了面向对象编程的基本概念",
        "✅ 完成了5个实战项目",
        "✅ 参加了3次技术分享会"
    ]

    for i, point in enumerate(points):
        if i > 0:
            p = text_frame.add_paragraph()
        else:
            p = text_frame.paragraphs[0]

        p.text = point
        p.font.size = Pt(24)
        p.font.color.rgb = RGBColor(51, 51, 51)
        p.space_before = Pt(12)

    # ============ 第3页：项目展示（使用图表） ============
    slide_layout = prs.slide_layouts[6]
    slide3 = prs.slides.add_slide(slide_layout)

    # 添加背景图片 (使用文件夹下的 bg2.png)
    bg2_image_path = "bg2.png"
    if os.path.exists(bg2_image_path):
        slide3.shapes.add_picture(bg2_image_path, Inches(0), Inches(0), 
                                 width=prs.slide_width, height=prs.slide_height)
        print("✅ 成功添加背景图片到第三页")
    else:
        print("⚠️ 未找到 bg2.png 背景图片")

    # 标题
    title_box3 = slide3.shapes.add_textbox(Inches(0.5), Inches(0.8), Inches(9), Inches(1))
    title_frame3 = title_box3.text_frame
    title_frame3.text = "📈 项目完成情况统计"
    title_frame3.paragraphs[0].font.size = Pt(32)
    title_frame3.paragraphs[0].font.bold = True
    title_frame3.paragraphs[0].font.color.rgb = RGBColor(0, 51, 102)
    title_frame3.paragraphs[0].alignment = PP_ALIGN.CENTER

    # 创建图表数据
    chart_data = CategoryChartData()
    chart_data.categories = ['项目1', '项目2', '项目3', '项目4', '项目5']
    _ = chart_data.add_series('完成度', (95, 88, 92, 98, 85))

    # 添加柱状图
    x, y, cx, cy = Inches(1), Inches(1.5), Inches(8), Inches(3.5)
    chart = slide3.shapes.add_chart(
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
        series.format.fill.fore_color.rgb = RGBColor(0, 102, 204)

    # ============ 第4页：技术分享 ============
    slide_layout = prs.slide_layouts[6]
    slide4 = prs.slides.add_slide(slide_layout)

    # 添加背景图片 (使用文件夹下的 bg2.png)
    bg2_image_path = "bg2.png"
    if os.path.exists(bg2_image_path):
        slide4.shapes.add_picture(bg2_image_path, Inches(0), Inches(0), 
                                 width=prs.slide_width, height=prs.slide_height)
        print("✅ 成功添加背景图片到第四页")
    else:
        print("⚠️ 未找到 bg2.png 背景图片")

    # 标题
    title_box4 = slide4.shapes.add_textbox(Inches(0.5), Inches(0.8), Inches(9), Inches(1))
    title_frame4 = title_box4.text_frame
    title_frame4.text = "💡 技术分享与心得"
    title_frame4.paragraphs[0].font.size = Pt(32)
    title_frame4.paragraphs[0].font.bold = True
    title_frame4.paragraphs[0].font.color.rgb = RGBColor(0, 51, 102)
    title_frame4.paragraphs[0].alignment = PP_ALIGN.CENTER

    # 左侧内容框
    left_box = slide4.shapes.add_textbox(Inches(0.5), Inches(1.2), Inches(4.5), Inches(3.5))
    left_frame = left_box.text_frame
    left_frame.word_wrap = True

    p1 = left_frame.paragraphs[0]
    p1.text = "📚 学习心得"
    p1.font.size = Pt(22)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(0, 102, 204)

    xinde = [
        "坚持每天写代码练习",
        "遇到问题主动查阅文档",
        "多参与技术社区讨论",
        "代码质量比速度更重要"
    ]

    for xin in xinde:
        p = left_frame.add_paragraph()
        p.text = f"• {xin}"
        p.font.size = Pt(18)
        p.font.color.rgb = RGBColor(51, 51, 51)
        p.space_before = Pt(8)

    # 右侧内容框
    right_box = slide4.shapes.add_textbox(Inches(5), Inches(1.2), Inches(4.5), Inches(3.5))
    right_frame = right_box.text_frame
    right_frame.word_wrap = True

    p2 = right_frame.paragraphs[0]
    p2.text = "🎯 未来计划"
    p2.font.size = Pt(22)
    p2.font.bold = True
    p2.font.color.rgb = RGBColor(204, 0, 0)

    jihua = [
        "深入学习Web开发框架",
        "学习数据分析和可视化",
        "参与开源项目贡献",
        "准备Python认证考试"
    ]

    for plan in jihua:
        p = right_frame.add_paragraph()
        p.text = f"• {plan}"
        p.font.size = Pt(18)
        p.font.color.rgb = RGBColor(51, 51, 51)
        p.space_before = Pt(8)

    # ============ 第5页：谢谢 ============
    slide_layout = prs.slide_layouts[6]
    slide5 = prs.slides.add_slide(slide_layout)

    # 添加背景图片 (使用文件夹下的 bg.png)
    bg_image_path = "bg.png"
    if os.path.exists(bg_image_path):
        slide5.shapes.add_picture(bg_image_path, Inches(0), Inches(0), 
                                 width=prs.slide_width, height=prs.slide_height)
        print("✅ 成功添加背景图片到最后一页")
    else:
        print("⚠️ 未找到 bg.png 背景图片")

    # 添加"谢谢"文本
    thanks_box = slide5.shapes.add_textbox(Inches(3), Inches(1.5), Inches(4), Inches(1.5))
    thanks_frame = thanks_box.text_frame
    thanks_frame.text = "谢谢"
    thanks_frame.paragraphs[0].font.size = Pt(72)
    thanks_frame.paragraphs[0].font.bold = True
    thanks_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)  # 白色字体
    thanks_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    thanks_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

    # 保存PPT
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"最终版班会发言_{timestamp}.pptx"
    prs.save(output_file)
    print(f"✅ PPT生成成功！文件已保存为: {output_file}")
    print(f"📊 共生成 {len(prs.slides)} 页幻灯片")


if __name__ == "__main__":
    print("=" * 60)
    print("开始生成班会上发言的PPT...")
    print("=" * 60)

    create_presentation()

    print("=" * 60)
    print("完成！")
    print("=" * 60)
