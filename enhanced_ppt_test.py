#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
增强版PPT生成测试脚本
扩展原有功能，增加更多实用特性和健壮性
"""

import os
import sys
import platform
from datetime import datetime
from pathlib import Path
import tempfile

# 检查依赖
required_packages = {
    'pptx': 'python-pptx',
    'PIL': 'Pillow'  # 用于图片处理
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
    sys.exit(1)

from pptx import Presentation
from pptx.util import Inches, Pt, Cm
from pptx.dml.color import RGBColor, HSLColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR_TYPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.table import TableStylePresets

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class FontManager:
    """字体管理器 - 处理跨平台字体兼容性"""
    
    @staticmethod
    def get_safe_font(font_name):
        """获取安全的字体名称"""
        system = platform.system()
        
        font_mapping = {
            '微软雅黑': {
                'Windows': 'Microsoft YaHei',
                'Darwin': 'PingFang TC',  # macOS
                'Linux': 'Noto Sans CJK SC'
            },
            '宋体': {
                'Windows': 'SimSun',
                'Darwin': 'Songti SC',
                'Linux': 'Noto Serif CJK SC'
            }
        }
        
        if font_name in font_mapping:
            return font_mapping[font_name].get(system, font_mapping[font_name]['Windows'])
        
        return font_name

class PPTTestSuite:
    """PPT测试套件"""
    
    def __init__(self, output_dir="test_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.created_files = []
        self.test_results = []
        
        # 字体兼容性
        self.font_manager = FontManager()
        
        print(f"📁 输出目录: {self.output_dir.absolute()}")
        print(f"💻 操作系统: {platform.system()} {platform.release()}")
        print(f"🐍 Python版本: {sys.version.split()[0]}")
    
    def log_test(self, test_name, success, message=""):
        """记录测试结果"""
        status = "✅" if success else "❌"
        result = f"{status} {test_name}: {message}"
        print(result)
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'time': datetime.now().isoformat()
        })
    
    def create_title_slide(self, prs, title, subtitle=""):
        """创建标题页 - 通用方法"""
        slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(slide_layout)
        
        title_placeholder = slide.shapes.title
        subtitle_placeholder = slide.placeholders[1]
        
        title_placeholder.text = title
        if subtitle:
            subtitle_placeholder.text = subtitle
        
        # 样式化标题
        title_frame = title_placeholder.text_frame.paragraphs[0]
        title_frame.font.name = self.font_manager.get_safe_font("微软雅黑")
        title_frame.font.size = Pt(32)
        title_frame.font.color.rgb = RGBColor(0, 51, 102)
        title_frame.alignment = PP_ALIGN.CENTER
        
        return slide
    
    def create_content_slide(self, prs, title, content_list, layout_index=1):
        """创建内容页 - 通用方法"""
        slide_layout = prs.slide_layouts[layout_index]
        slide = prs.slides.add_slide(slide_layout)
        
        title_placeholder = slide.shapes.title
        content_placeholder = slide.placeholders[1]
        
        title_placeholder.text = title
        
        # 样式化标题
        title_frame = title_placeholder.text_frame.paragraphs[0]
        title_frame.font.name = self.font_manager.get_safe_font("微软雅黑")
        title_frame.font.size = Pt(24)
        title_frame.font.color.rgb = RGBColor(102, 0, 0)
        
        # 填充内容
        tf = content_placeholder.text_frame
        tf.clear()
        
        for i, content in enumerate(content_list):
            p = tf.add_paragraph()
            p.text = content
            p.font.name = self.font_manager.get_safe_font("微软雅黑")
            p.font.size = Pt(16)
            p.space_after = Pt(12)
            
            # 多级列表支持
            if isinstance(content, tuple):
                text, level = content
                p.text = text
                p.level = level
        
        return slide
    
    def test_basic_generation(self):
        """测试基础PPT生成"""
        print("\n" + "=" * 60)
        print("🧪 测试1: 基础PPT生成")
        print("=" * 60)
        
        try:
            prs = Presentation()
            
            # 标题页
            self.create_title_slide(
                prs, 
                "Python-PPTX 增强测试报告",
                f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n测试套件版本: 2.0"
            )
            
            # 内容页
            content = [
                "✓ 基础文本插入功能正常",
                "✓ 字体样式设置生效",
                "✓ 颜色配置正确应用",
                "✓ 版式切换无异常"
            ]
            self.create_content_slide(prs, "基础功能验证", content)
            
            # 保存文件
            filename = f"basic_generation_{int(datetime.now().timestamp())}.pptx"
            filepath = self.output_dir / filename
            prs.save(filepath)
            
            # 验证文件
            if self._validate_ppt_file(filepath):
                self.log_test("基础生成", True, f"文件已保存: {filename}")
                self.created_files.append(str(filepath))
                return True
            else:
                self.log_test("基础生成", False, "生成的文件无效")
                return False
                
        except Exception as e:
            self.log_test("基础生成", False, str(e))
            return False
    
    def test_advanced_styles(self):
        """测试高级样式功能"""
        print("\n" + "=" * 60)
        print("🎨 测试2: 高级样式功能")
        print("=" * 60)
        
        try:
            prs = Presentation()
            
            # 渐变背景测试
            slide1 = prs.slides.add_slide(prs.slide_layouts[6])
            self._create_gradient_background(slide1)
            
            title_box = slide1.shapes.add_textbox(Cm(2), Cm(2), Cm(20), Cm(3))
            tf = title_box.text_frame
            p = tf.paragraphs[0]
            p.text = "渐变背景效果演示"
            p.font.name = self.font_manager.get_safe_font("微软雅黑")
            p.font.size = Pt(28)
            p.font.color.rgb = RGBColor(255, 255, 255)
            p.alignment = PP_ALIGN.CENTER
            
            # 复杂形状测试
            slide2 = prs.slides.add_slide(prs.slide_layouts[6])
            self._create_complex_shapes(slide2)
            
            # 保存文件
            filename = f"advanced_styles_{int(datetime.now().timestamp())}.pptx"
            filepath = self.output_dir / filename
            prs.save(filepath)
            
            if self._validate_ppt_file(filepath):
                self.log_test("高级样式", True, f"渐变和形状测试完成")
                self.created_files.append(str(filepath))
                return True
            else:
                self.log_test("高级样式", False, "文件验证失败")
                return False
                
        except Exception as e:
            self.log_test("高级样式", False, str(e))
            return False
    
    def test_chart_insertion(self):
        """测试图表插入功能"""
        print("\n" + "=" * 60)
        print("📊 测试3: 图表插入功能")
        print("=" * 60)
        
        try:
            prs = Presentation()
            
            # 创建数据
            chart_data = CategoryChartData()
            chart_data.categories = ['Q1', 'Q2', 'Q3', 'Q4']
            chart_data.add_series('销售额', (4.3, 2.5, 3.5, 4.5))
            chart_data.add_series('利润', (1.2, 2.3, 1.8, 2.9))
            
            # 添加图表slide
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            
            # 添加标题
            title_box = slide.shapes.add_textbox(Cm(1), Cm(0.5), Cm(20), Cm(1))
            tf = title_box.text_frame
            p = tf.paragraphs[0]
            p.text = "销售数据图表分析"
            p.font.name = self.font_manager.get_safe_font("微软雅黑")
            p.font.size = Pt(20)
            
            # 插入图表
            x, y, cx, cy = Cm(1), Cm(2), Cm(20), Cm(12)
            chart = slide.shapes.add_chart(
                XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, chart_data
            ).chart
            
            # 设置图表样式
            chart.has_legend = True
            chart.legend.position = XL_LEGEND_POSITION.BOTTOM
            chart.legend.include_in_layout = False
            
            # 保存文件
            filename = f"chart_insertion_{int(datetime.now().timestamp())}.pptx"
            filepath = self.output_dir / filename
            prs.save(filepath)
            
            if self._validate_ppt_file(filepath):
                self.log_test("图表插入", True, "柱状图创建成功")
                self.created_files.append(str(filepath))
                return True
            else:
                self.log_test("图表插入", False, "文件验证失败")
                return False
                
        except Exception as e:
            self.log_test("图表插入", False, str(e))
            return False
    
    def test_image_handling(self):
        """测试图片处理功能"""
        print("\n" + "=" * 60)
        print("🖼️  测试4: 图片处理功能")
        print("=" * 60)
        
        if not PIL_AVAILABLE:
            self.log_test("图片处理", False, "PIL/Pillow未安装，跳过测试")
            return False
        
        try:
            # 创建测试图片
            test_image_path = self._create_test_image()
            
            prs = Presentation()
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            
            # 添加标题
            title_box = slide.shapes.add_textbox(Cm(1), Cm(0.5), Cm(20), Cm(1))
            tf = title_box.text_frame
            p = tf.paragraphs[0]
            p.text = "动态生成图片演示"
            p.font.name = self.font_manager.get_safe_font("微软雅黑")
            p.font.size = Pt(20)
            
            # 插入图片
            left, top, width, height = Cm(2), Cm(2), Cm(8), Cm(6)
            slide.shapes.add_picture(test_image_path, left, top, width, height)
            
            # 添加说明文字
            text_box = slide.shapes.add_textbox(Cm(11), Cm(2), Cm(8), Cm(6))
            tf = text_box.text_frame
            tf.text = "此图片由程序动态生成\n用于测试PPT图片插入功能\n支持PNG/JPG/BMP等格式"
            
            for paragraph in tf.paragraphs:
                paragraph.font.name = self.font_manager.get_safe_font("微软雅黑")
                paragraph.font.size = Pt(14)
            
            # 保存文件
            filename = f"image_handling_{int(datetime.now().timestamp())}.pptx"
            filepath = self.output_dir / filename
            prs.save(filepath)
            
            # 清理测试图片
            os.remove(test_image_path)
            
            if self._validate_ppt_file(filepath):
                self.log_test("图片处理", True, "动态图片插入成功")
                self.created_files.append(str(filepath))
                return True
            else:
                self.log_test("图片处理", False, "文件验证失败")
                return False
                
        except Exception as e:
            self.log_test("图片处理", False, str(e))
            return False
    
    def _create_gradient_background(self, slide):
        """创建渐变背景"""
        background = slide.background
        fill = background.fill
        fill.gradient()
        fill.gradient_angle = 45
        
        # 设置渐变色
        stops = fill.gradient_stops
        stops[0].color.rgb = RGBColor(0, 51, 102)    # 深蓝
        stops[1].color.rgb = RGBColor(51, 102, 153)   # 中蓝
        stops[2].color.rgb = RGBColor(102, 153, 204)  # 浅蓝
    
    def _create_complex_shapes(self, slide):
        """创建复杂形状组合"""
        # 主标题
        title_box = slide.shapes.add_textbox(Cm(1), Cm(0.5), Cm(20), Cm(1))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = "复杂形状设计演示"
        p.font.name = self.font_manager.get_safe_font("微软雅黑")
        p.font.size = Pt(20)
        
        # 创建各种形状
        shapes_config = [
            (MSO_SHAPE.ROUNDED_RECTANGLE, Cm(2), Cm(2), Cm(4), Cm(2), RGBColor(255, 0, 0)),
            (MSO_SHAPE.OVAL, Cm(7), Cm(2), Cm(4), Cm(2), RGBColor(0, 255, 0)),
            (MSO_SHAPE.DIAMOND, Cm(12), Cm(2), Cm(4), Cm(2), RGBColor(0, 0, 255)),
            (MSO_SHAPE.FLOWCHART_PROCESS, Cm(2), Cm(5), Cm(4), Cm(2), RGBColor(255, 255, 0)),
        ]
        
        for shape_type, left, top, width, height, color in shapes_config:
            shape = slide.shapes.add_shape(shape_type, left, top, width, height)
            shape.fill.solid()
            shape.fill.fore_color.rgb = color
            shape.line.fill.background()
            
            # 添加形状标签
            center_left = left + width/2 - Cm(1)
            center_top = top + height/2 - Cm(0.3)
            label_box = slide.shapes.add_textbox(center_left, center_top, Cm(2), Cm(0.6))
            label_tf = label_box.text_frame
            label_p = label_tf.paragraphs[0]
            label_p.text = shape_type.name.split('_')[-1].lower()
            label_p.font.size = Pt(8)
            label_p.alignment = PP_ALIGN.CENTER
    
    def _create_test_image(self):
        """创建测试图片"""
        img = Image.new('RGB', (400, 300), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # 绘制简单图形
        draw.rectangle([50, 50, 350, 250], outline='darkblue', width=3)
        draw.ellipse([100, 100, 300, 200], fill='orange', outline='red', width=2)
        
        # 添加文字
        try:
            # 尝试使用中文字体
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = None
        
        draw.text((120, 140), "测试图片", fill='white', font=font)
        
        # 保存临时文件
        temp_path = self.output_dir / f"test_image_{int(datetime.now().timestamp())}.png"
        img.save(temp_path)
        return str(temp_path)
    
    def _validate_ppt_file(self, filepath):
        """验证PPT文件完整性"""
        try:
            if not os.path.exists(filepath):
                return False
            
            file_size = os.path.getsize(filepath)
            if file_size < 1000:  # 文件太小，可能有问题
                return False
            
            # 验证ZIP结构
            import zipfile
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                required_files = ['[Content_Types].xml', 'ppt/presentation.xml']
                file_list = zip_ref.namelist()
                
                for req_file in required_files:
                    if req_file not in file_list:
                        return False
                
                return True
                
        except Exception:
            return False
    
    def generate_report(self):
        """生成测试报告"""
        report_path = self.output_dir / f"test_report_{int(datetime.now().timestamp())}.txt"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("PPT生成测试报告\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"操作系统: {platform.system()} {platform.release()}\n")
            f.write(f"Python版本: {sys.version.split()[0]}\n")
            f.write(f"输出目录: {self.output_dir.absolute()}\n\n")
            
            f.write("测试结果汇总:\n")
            f.write("-" * 30 + "\n")
            
            passed = sum(1 for r in self.test_results if r['success'])
            total = len(self.test_results)
            
            for result in self.test_results:
                status = "✅ 通过" if result['success'] else "❌ 失败"
                f.write(f"{status} | {result['test']}\n")
                if result['message']:
                    f.write(f"         {result['message']}\n")
            
            f.write(f"\n总计: {passed}/{total} 项测试通过\n")
            
            if self.created_files:
                f.write(f"\n生成的文件:\n")
                for file_path in self.created_files:
                    file_size = os.path.getsize(file_path)
                    f.write(f"  - {os.path.basename(file_path)} ({file_size} bytes)\n")
        
        print(f"\n📋 测试报告已生成: {report_path}")

def main():
    """主函数"""
    print("🚀 Python-PPTX 增强测试套件 v2.0")
    print("=" * 60)
    
    # 创建测试套件实例
    tester = PPTTestSuite()
    
    try:
        # 运行所有测试
        tests = [
            tester.test_basic_generation,
            tester.test_advanced_styles,
            tester.test_chart_insertion,
            tester.test_image_handling
        ]
        
        for test_func in tests:
            test_func()
        
        # 生成报告
        tester.generate_report()
        
        # 总结
        passed = sum(1 for r in tester.test_results if r['success'])
        total = len(tester.test_results)
        
        print("\n" + "=" * 60)
        print(f"🏁 测试完成: {passed}/{total} 项通过")
        
        if passed == total:
            print("🎉 所有测试通过! PPT生成功能正常")
        else:
            print(f"⚠️  {total-passed} 项测试失败，请检查日志")
        
        print(f"📁 输出文件位置: {tester.output_dir.absolute()}")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n⏹️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
