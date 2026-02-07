from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Pt
from datetime import datetime
import os


def copy_images_to_new_doc(source_doc, target_doc):
    """
    从源文档复制所有图片到目标文档
    """
    import tempfile
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
                import os
                os.unlink(temp_path)


def process_word_with_format(input_path, output_path):
    """
    读取Word文档，保留格式和层级结构，修改文本后写入新文档
    :param input_path: 原Word文档路径（.docx）
    :param output_path: 新Word文档保存路径
    """
    # 加载原文档
    doc = Document(input_path)
    
    # 2. 遍历所有段落，保留格式并修改内容
    for para in doc.paragraphs:
        # 跳过空段落
        if not para.text.strip():
            continue
        
        # 示例1：修改文本（保留原段落的所有格式：字体、字号、对齐、层级）
        # 比如：将所有"旧关键词"替换为"新关键词"
        original_text = para.text
        modified_text = original_text.replace("旧关键词", "新关键词")
        
        # 关键：清空原段落文本，重新写入（保留原格式）
        para.text = modified_text
    
    # 3. 遍历所有表格（如果有表格，也保留格式修改）
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    if para.text.strip():
                        para.text = para.text.replace("旧关键词", "新关键词")
    
    # 4. 处理文档中的图片
    copy_images_to_new_doc(Document(input_path), doc)
    
    # 5. 保存新文档（保留所有原格式+修改后的内容）
    doc.save(output_path)
    print(f"文档处理完成，新文件已保存至：{output_path}")


# ------------------- 调用示例 -------------------
if __name__ == "__main__":
    # 替换为你的实际文件路径
    input_doc = "aa.docx"
    # 添加时间戳到文件名以防止重名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_doc = f"新文档_{timestamp}.docx"
    
    # 执行处理
    process_word_with_format(input_doc, output_doc)