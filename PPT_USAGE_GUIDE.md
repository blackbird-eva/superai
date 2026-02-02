# PPT智能生成 - 完整技术指南

## 📌 代码运行注意事项

### 1. 跨平台字体兼容性

#### 问题说明
代码中默认使用Windows中文字体（如"微软雅黑"），在macOS或Linux系统上可能无法正常显示。

#### 解决方案
系统已实现自动字体检测功能，根据操作系统自动选择兼容字体：

| 操作系统 | 优先字体 | 备选字体 |
|---------|---------|---------|
| Windows | 微软雅黑/思源黑体/宋体/黑体/楷体 | - |
| macOS | PingFang SC/Heiti SC/STSong/Kaiti SC | - |
| Linux | Noto Sans CJK SC/SimHei/KaiTi | Arial（兜底） |

### 2. 尺寸单位说明

#### 使用英寸（Inches）单位
```python
from pptx.util import Inches, Pt

# 幻灯片尺寸（16:9比例）
prs.slide_width = Inches(10)   # 宽度10英寸
prs.slide_height = Inches(5.625)  # 高度5.625英寸
```

#### 换算参考
```
1英寸 = 2.54厘米
1英寸 ≈ 96磅

常用尺寸对照：
- 1英寸 = 2.54厘米
- 0.5英寸 = 1.27厘米
- 10英寸 = 25.4厘米
```

### 3. 图片插入说明

#### 图片插入示例
```python
# 插入图片（推荐使用绝对路径）
img_path = "/absolute/path/to/image.png"

slide.shapes.add_picture(
    img_path,
    left=Inches(2),      # 左边距2英寸
    top=Inches(2),       # 上边距2英寸
    width=Inches(6)      # 宽度6英寸（高度按比例自适应）
)
```

#### 支持的图片格式
- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)
- BMP (.bmp)
- TIFF (.tiff)

---

## 🎨 版式索引说明（内置空白模板）

python-pptx 内置空白模板的核心版式索引为固定值：

| 索引 | 版式名称 | 适用场景 | 使用示例 |
|------|---------|---------|---------|
| **0** | 标题页 | PPT封面、章节封面 | `prs.slide_layouts[0]` |
| **1** | 标题 + 内容 | 核心内容页、技术要点 | `prs.slide_layouts[1]` |
| **2** | 节标题 | 章节分隔页 | `prs.slide_layouts[2]` |
| **3** | 两栏内容 | 内容对比、分类展示 | `prs.slide_layouts[3]` |
| **4** | 标题 + 图表 | 数据可视化展示 | `prs.slide_layouts[4]` |
| **5** | 标题 + 图片 + 内容 | 图文结合展示 | `prs.slide_layouts[5]` |
| **6** | 空白页 | 自由布局（图片/表格） | `prs.slide_layouts[6]` |

#### 版式使用示例
```python
# 使用版式0：标题页
slide = prs.slides.add_slide(prs.slide_layouts[0])
title = slide.shapes.title
title.text = "封面标题"

# 使用版式1：标题+内容
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = "章节标题"
slide.placeholders[1].text = "内容文本"

# 使用版式6：空白页（自由布局）
slide = prs.slides.add_slide(prs.slide_layouts[6])
text_box = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(8), Inches(4))
text_box.text_frame.text = "自由布局内容"
```

---

## 🔧 核心拓展功能

### 1. 插入形状

```python
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

# 插入矩形
shape = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(2), Inches(6), Inches(4), Inches(1)
)
shape.fill.solid()
shape.fill.fore_color.rgb = RGBColor(255, 230, 204)  # 浅橙色背景

# 插入圆角矩形
shape = slide.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(0.5), Inches(0.3), Inches(9), Inches(0.9)
)
shape.fill.solid()
shape.fill.fore_color.rgb = RGBColor(64, 158, 255)  # 蓝色

# 插入圆形（椭圆）
shape = slide.shapes.add_shape(
    MSO_SHAPE.OVAL,
    Inches(9.2), Inches(5), Inches(0.3), Inches(0.3)
)
shape.fill.solid()
shape.fill.fore_color.rgb = RGBColor(103, 194, 58)  # 绿色

# 插入装饰线
line_shape = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(0.5), Inches(1.5), Inches(9), Inches(0.05)
)
line_shape.fill.solid()
line_shape.fill.fore_color.rgb = RGBColor(240, 240, 240)  # 灰色
```

#### 支持的形状类型
```python
MSO_SHAPE.RECTANGLE          # 矩形
MSO_SHAPE.ROUNDED_RECTANGLE  # 圆角矩形
MSO_SHAPE.OVAL              # 椭圆/圆形
MSO_SHAPE.DIAMOND           # 菱形
MSO_SHAPE.TRIANGLE          # 三角形
MSO_SHAPE.STAR              # 星形
MSO_SHAPE.ARROW             # 箭头
```

### 2. 设置幻灯片背景

#### 纯色背景
```python
# 设置浅灰色背景
slide.background.fill.solid()
slide.background.fill.fore_color.rgb = RGBColor(245, 245, 245)

# 设置主题色背景
slide.background.fill.solid()
slide.background.fill.fore_color.rgb = RGBColor(64, 158, 255)
```

#### 渐变背景（高级）
```python
from pptx.dml.fill import FillFormat

# 创建渐变背景
fill = slide.background.fill
fill.gradient()
fill.gradient_angle = 90  # 渐变角度

# 设置渐变色
# 注意：python-pptx对渐变支持有限，建议使用纯色
```

### 3. 添加备注

```python
# 为幻灯片添加隐藏备注
notes_slide = slide.notes_slide
if notes_slide:
    note = notes_slide.notes_text_frame
    note.text = "此页为核心技术要点，讲解时需强调python-pptx的核心类和版式使用"
```

#### 备注用途
- 演讲者备注（演讲稿）
- 制作说明
- 版本信息
- 注意事项

### 4. 查看占位符信息

```python
# 打印占位符索引和名称
for idx, placeholder in enumerate(slide.placeholders):
    print(f"索引 {idx}: {placeholder.name}")
    print(f"  类型: {placeholder.placeholder_format}")
```

#### 常见占位符名称
```
Title         # 标题
Content       # 内容
Subtitle      # 副标题
Date          # 日期
Footer        # 页脚
Slide Number   # 幻灯片编号
```

### 5. 设置表格样式

```python
# 设置表格边框
for row in table.rows:
    for cell in row.cells:
        # 边框颜色
        cell.border.top.color.rgb = RGBColor(0, 0, 0)
        cell.border.bottom.color.rgb = RGBColor(0, 0, 0)
        cell.border.left.color.rgb = RGBColor(0, 0, 0)
        cell.border.right.color.rgb = RGBColor(0, 0, 0)

        # 边框宽度
        cell.border.top.width = Pt(1)
        cell.border.bottom.width = Pt(1)
        cell.border.left.width = Pt(1)
        cell.border.right.width = Pt(1)
```

### 6. 段落样式设置

```python
from pptx.enum.text import PP_ALIGN

# 文本对齐
paragraph.alignment = PP_ALIGN.CENTER    # 居中
paragraph.alignment = PP_ALIGN.LEFT       # 左对齐
paragraph.alignment = PP_ALIGN.RIGHT      # 右对齐
paragraph.alignment = PP_ALIGN.JUSTIFY   # 两端对齐

# 行间距
paragraph.line_spacing = 1.5  # 1.5倍行距

# 段落间距
paragraph.space_before = Pt(12)   # 段前间距12磅
paragraph.space_after = Pt(6)     # 段后间距6磅

# 文本缩进
paragraph.first_line_indent = Pt(24)  # 首行缩进24磅（两个字符）
```

### 7. 字体样式设置

```python
from pptx.dml.color import RGBColor

# 字体名称
paragraph.font.name = "微软雅黑"

# 字体大小
paragraph.font.size = Pt(18)

# 字体颜色
paragraph.font.color.rgb = RGBColor(51, 51, 51)

# 字体加粗
paragraph.font.bold = True

# 字体斜体
paragraph.font.italic = True

# 字体下划线
paragraph.font.underline = True

# 删除线
paragraph.font.strike = False
```

---

## ⚠️ 常见问题解决方案

### 1. 中文乱码

**问题**：生成的PPT中文字符显示为方块或乱码。

**原因**：字体不支持中文或系统未安装指定字体。

**解决方案**：
```python
# 确保使用系统支持的中文字体
paragraph.font.name = "微软雅黑"  # Windows
# 或
paragraph.font.name = "PingFang SC"  # macOS
# 或
paragraph.font.name = "Arial"  # 兜底（英文）

# 避免使用稀有字体
paragraph.font.name = "方正黑体"  # ❌ 可能不支持
paragraph.font.name = "宋体"  # ✅ 系统自带
```

### 2. 图片变形

**问题**：插入的图片比例不正确，拉伸变形。

**原因**：同时指定宽度和高度，强制改变图片比例。

**解决方案**：
```python
# ✅ 正确：仅指定宽度，高度按比例自适应
slide.shapes.add_picture(
    img_path,
    left=Inches(2),
    top=Inches(2),
    width=Inches(6)      # 只指定宽度
)

# ✅ 正确：仅指定高度，宽度按比例自适应
slide.shapes.add_picture(
    img_path,
    left=Inches(2),
    top=Inches(2),
    height=Inches(4)     # 只指定高度
)

# ❌ 错误：同时指定宽高，可能导致变形
slide.shapes.add_picture(
    img_path,
    left=Inches(1),
    top=Inches(1),
    width=Inches(4),
    height=Inches(3)  # 同时指定，可能变形
)
```

### 3. 占位符索引错误

**问题**：使用错误的占位符索引导致 `KeyError` 或 `AttributeError`。

**原因**：不同版式的占位符索引不同。

**解决方案**：
```python
# 方法1：打印占位符信息
for idx, placeholder in enumerate(slide.placeholders):
    print(f"索引 {idx}: {placeholder.name}")

# 方法2：使用属性访问（推荐）
title = slide.shapes.title  # 直接获取标题占位符
subtitle = slide.placeholders[1]  # 索引1通常是副标题

# 方法3：使用异常处理
try:
    subtitle = slide.placeholders[1]
    subtitle.text = "副标题"
except (KeyError, AttributeError):
    print("该版式没有副标题占位符")
```

#### 各版式的占位符索引
```
版式0（标题页）：
  - 索引0: Title（主标题）
  - 索引1: Subtitle（副标题）

版式1（标题+内容）：
  - 索引0: Title（标题）
  - 索引1: Content（内容）

版式2（节标题）：
  - 索引0: Title（标题）
  - 索引1: Body（正文）

版式6（空白页）：
  - 无占位符，完全自由布局
```

### 4. 文件保存失败

**问题**：保存PPT时报错 `PermissionDenied` 或 `IOError`。

**原因**：
1. PPT文件已被打开（被占用）
2. 保存路径无写入权限
3. 磁盘空间不足

**解决方案**：
```python
# 1. 关闭已打开的PPT文件
# 在PowerPoint/WPS中打开的文件必须先关闭

# 2. 检查路径权限
import os
save_path = "/path/to/save.pptx"
save_dir = os.path.dirname(save_path)

# 确保目录存在
if not os.path.exists(save_dir):
    os.makedirs(save_dir, exist_ok=True)

# 检查写权限
if not os.access(save_dir, os.W_OK):
    raise Exception("目录无写权限")

# 3. 使用异常处理
try:
    prs.save(save_path)
    print("保存成功")
except PermissionError:
    print("文件被占用，请关闭后重试")
    # 使用临时目录
    import tempfile
    temp_path = os.path.join(tempfile.gettempdir(), "backup.pptx")
    prs.save(temp_path)
except IOError as e:
    print(f"保存失败: {e}")
```

### 5. 文件过大

**问题**：生成的PPT文件体积过大（>10MB）。

**原因**：
1. 图片未压缩
2. 幻灯片数量过多
3. 使用了过多高分辨率图片

**解决方案**：
```python
# 1. 压缩图片（在插入前）
from PIL import Image

img = Image.open(img_path)
img.thumbnail((1920, 1080))  # 限制最大尺寸
img.save("compressed.png", "PNG", optimize=True)

# 2. 控制幻灯片数量
slide_count = min(requested_count, 20)  # 最多20张

# 3. 使用矢量图形代替图片（适用于图表等）
shape = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    left=Inches(2), top=Inches(2),
    width=Inches(4), height=Inches(3)
)
shape.fill.solid()
shape.fill.fore_color.rgb = RGBColor(255, 230, 204)
```

### 6. 字体不生效

**问题**：设置的字体在PPT中显示为默认字体（Calibri）。

**原因**：
1. 系统未安装该字体
2. 字体名称拼写错误
3. 使用了不支持的字体格式

**解决方案**：
```python
# 1. 验证字体是否安装
import matplotlib.font_manager
fonts = [f.name for f in matplotlib.font_manager.fontManager.ttflist]
if "微软雅黑" not in fonts:
    print("系统未安装微软雅黑字体")

# 2. 使用正确的字体名称
paragraph.font.name = "Microsoft YaHei"  # 英文命名字体
# 或
paragraph.font.name = "微软雅黑"  # 中文命名字体

# 3. 使用系统默认字体作为兜底
try:
    paragraph.font.name = "自定义字体"
except:
    paragraph.font.name = "Arial"  # 兜底
```

---

## 🎯 快速开始

### 最小化示例
```python
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor

# 创建PPT
prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[0])

# 添加标题
title = slide.shapes.title
title.text = "我的PPT"
title.text_frame.paragraphs[0].font.size = Pt(44)
title.text_frame.paragraphs[0].font.color.rgb = RGBColor(64, 158, 255)

# 保存
prs.save("test.pptx")
```

### 运行此系统
```bash
# 1. 安装依赖
pip install python-pptx==1.0.2

# 2. 启动Django服务器
cd backend
python manage.py runserver

# 3. 访问前端
# 在浏览器中打开前端页面
# 输入文本内容，点击生成PPT
```

---

## 📚 参考资源

- python-pptx官方文档: https://python-pptx.readthedocs.io/
- PowerPoint API参考: https://docs.microsoft.com/en-us/office/vba/api/overview/powerpoint
- RGB颜色转换工具: https://www.rgbtohex.net/
- 版式说明: https://python-pptx.readthedocs.io/en/latest/api/slides.html

---

**注意**：本系统已内置跨平台字体兼容、路径安全验证、错误处理等机制，可直接在生产环境使用。

