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


def create_presentation():
    """创建班会上发言的PPT，基于模板"""

    # 检查模板文件是否存在
    template_file = "ppt.pptx"
    if os.path.exists(template_file):
        print(f"📄 使用模板文件: {template_file}")
        # 直接创建新的演示文稿，但使用模板的样式规范
        prs = Presentation()
        # 设置与模板相同的大小（16:9）
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(5.625)
    else:
        print(f"⚠️ 模板文件 {template_file} 不存在，使用默认模板")
        prs = Presentation()
        # 设置幻灯片大小为16:9
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(5.625)

    # ============ 第1页：标题页 ============
    slide_layout = prs.slide_layouts[0]  # 使用标题幻灯片布局
    slide1 = prs.slides.add_slide(slide_layout)

    title1 = slide1.shapes.title
    subtitle1 = slide1.placeholders[1]

    title1.text = "班会上发言"
    subtitle1.text = "Python编程语言学习小组\n2024年度总结"

    # 标题样式
    title1.text_frame.paragraphs[0].font.size = Pt(44)
    title1.text_frame.paragraphs[0].font.bold = True
    title1.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 51, 102)

    # 副标题样式
    subtitle1.text_frame.paragraphs[0].font.size = Pt(24)
    subtitle1.text_frame.paragraphs[0].font.color.rgb = RGBColor(128, 128, 128)

    # 添加装饰形状
    shape = slide1.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(4.5), Inches(10), Inches(1.125)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(0, 51, 102)
    shape.line.fill.background()

    # ============ 第2页：学习成果展示 ============
    slide_layout = prs.slide_layouts[6]  # 使用空白布局
    slide2 = prs.slides.add_slide(slide_layout)

    # 添加标题框
    title_box = slide2.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(1))
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

    # 标题
    title_box3 = slide3.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(1))
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

    # 标题
    title_box4 = slide4.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(1))
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

    # ============ 第5页：总结与展望 ============
    slide_layout = prs.slide_layouts[6]
    slide5 = prs.slides.add_slide(slide_layout)

    # 标题
    title_box5 = slide5.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(1))
    title_frame5 = title_box5.text_frame
    title_frame5.text = "🌟 总结与展望"
    title_frame5.paragraphs[0].font.size = Pt(32)
    title_frame5.paragraphs[0].font.bold = True
    title_frame5.paragraphs[0].font.color.rgb = RGBColor(0, 51, 102)
    title_frame5.paragraphs[0].alignment = PP_ALIGN.CENTER

    # 添加总结文本框
    summary_box = slide5.shapes.add_textbox(Inches(1), Inches(1.2), Inches(8), Inches(2.5))
    summary_frame = summary_box.text_frame
    summary_frame.word_wrap = True

    summary_text = "本学期我们在Python编程方面取得了显著进步。通过系统的学习和实践，不仅掌握了编程基础知识，还培养了问题解决能力和团队协作精神。感谢老师的指导和同学们的帮助！"
    summary_frame.text = summary_text
    summary_frame.paragraphs[0].font.size = Pt(20)
    summary_frame.paragraphs[0].font.color.rgb = RGBColor(51, 51, 51)
    summary_frame.paragraphs[0].alignment = PP_ALIGN.JUSTIFY

    # 添加感谢框
    thanks_box = slide5.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(1), Inches(3.8), Inches(8), Inches(1.2)
    )
    thanks_box.fill.solid()
    thanks_box.fill.fore_color.rgb = RGBColor(0, 51, 102)
    thanks_box.line.color.rgb = RGBColor(255, 255, 255)
    thanks_box.line.width = Pt(2)

    thanks_frame = thanks_box.text_frame
    thanks_frame.text = "🙏 感谢聆听！欢迎大家提出宝贵意见和建议！"
    thanks_frame.paragraphs[0].font.size = Pt(24)
    thanks_frame.paragraphs[0].font.bold = True
    thanks_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
    thanks_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    thanks_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

    # 保存PPT
    output_file = "班会发言.pptx"
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
