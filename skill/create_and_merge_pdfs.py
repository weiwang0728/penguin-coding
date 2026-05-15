#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建两个PDF文件并合并它们
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER
import fitz  # PyMuPDF

# 尝试注册中文字体（如果系统中有支持中文的字体）
def setup_chinese_font():
    try:
        # 尝试使用常见的中文字体
        font_paths = [
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
            '/System/Library/Fonts/PingFang.ttc',  # macOS
            'C:/Windows/Fonts/simhei.ttf',  # Windows
        ]
        
        for font_path in font_paths:
            try:
                pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                return True
            except:
                continue
    except:
        pass
    return False

def create_pdf1():
    """创建第一个PDF文件"""
    doc = SimpleDocTemplate("pdf1.pdf", pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # 设置标题样式
    title_style = styles['Title']
    title_style.alignment = TA_CENTER
    
    # 尝试使用中文字体
    if setup_chinese_font():
        title_style.fontName = 'ChineseFont'
        normal_style = styles['Normal']
        normal_style.fontName = 'ChineseFont'
    
    # 添加内容
    story.append(Paragraph("第一个PDF文档", title_style))
    story.append(Spacer(1, 0.2 * inch))
    
    content_lines = [
        "欢迎使用PDF处理技能！",
        "",
        "这是第一个PDF文件的内容。",
        "",
        "主要特点：",
        "• 使用ReportLab库创建",
        "• 支持中文内容",
        "• 格式化的文本",
        "",
        "接下来我们将创建第二个PDF文件，",
        "然后将它们合并在一起。",
        "",
        "PDF（Portable Document Format）是一种",
        "跨平台的文件格式，能够在各种设备上",
        "保持一致的显示效果。"
    ]
    
    for line in content_lines:
        story.append(Paragraph(line, styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))
    
    doc.build(story)
    print("✓ 已创建 pdf1.pdf")

def create_pdf2():
    """创建第二个PDF文件"""
    doc = SimpleDocTemplate("pdf2.pdf", pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # 设置标题样式
    title_style = styles['Title']
    title_style.alignment = TA_CENTER
    
    # 尝试使用中文字体
    if setup_chinese_font():
        title_style.fontName = 'ChineseFont'
        normal_style = styles['Normal']
        normal_style.fontName = 'ChineseFont'
    
    # 添加内容
    story.append(Paragraph("第二个PDF文档", title_style))
    story.append(Spacer(1, 0.2 * inch))
    
    content_lines = [
        "这是第二个PDF文件！",
        "",
        "PDF合并技术允许我们将多个",
        "PDF文件组合成一个文档。",
        "",
        "合并PDF的应用场景：",
        "• 组装多页报告",
        "• 合并章节文档",
        "• 创建完整的手册",
        "",
        "我们使用PyMuPDF（fitz）库",
        "来执行PDF合并操作。",
        "",
        "PyMuPDF是一个高性能的Python库，",
        "提供PDF文档的读取、创建、",
        "编辑和合并功能。",
        "",
        "This document also supports English text.",
        "",
        "感谢您的使用！"
    ]
    
    for line in content_lines:
        story.append(Paragraph(line, styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))
    
    doc.build(story)
    print("✓ 已创建 pdf2.pdf")

def merge_pdfs():
    """合并两个PDF文件"""
    result = fitz.open()
    
    # 打开并插入第一个PDF
    doc1 = fitz.open("pdf1.pdf")
    result.insert_pdf(doc1)
    doc1.close()
    
    # 打开并插入第二个PDF
    doc2 = fitz.open("pdf2.pdf")
    result.insert_pdf(doc2)
    doc2.close()
    
    # 保存合并后的PDF
    result.save("merged.pdf")
    result.close()
    
    print("✓ 已合并为 merged.pdf")
    
    # 显示合并结果信息
    merged = fitz.open("merged.pdf")
    print(f"  合并后的PDF包含 {len(merged)} 页")
    merged.close()

def main():
    print("=" * 50)
    print("PDF创建和合并示例")
    print("=" * 50)
    print()
    
    print("步骤 1: 创建第一个PDF...")
    create_pdf1()
    print()
    
    print("步骤 2: 创建第二个PDF...")
    create_pdf2()
    print()
    
    print("步骤 3: 合并PDF文件...")
    merge_pdfs()
    print()
    
    print("=" * 50)
    print("完成！生成了三个文件：")
    print("  - pdf1.pdf (第一个PDF)")
    print("  - pdf2.pdf (第二个PDF)")
    print("  - merged.pdf (合并后的PDF)")
    print("=" * 50)

if __name__ == "__main__":
    main()
