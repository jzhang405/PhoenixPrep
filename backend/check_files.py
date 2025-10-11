#!/usr/bin/env python3
"""
检查PDF文件状态
"""

import os
from pathlib import Path

PDF_DIR = "/Users/zhangcz/Downloads/naijing/真题库/北京123模考"
OUTPUT_DIR = "../data/parsed-html"

def get_output_filename(pdf_path):
    """根据PDF文件路径生成输出文件名"""
    pdf_name = Path(pdf_path).stem
    return os.path.join(OUTPUT_DIR, f"{pdf_name}_parsed.html")

def file_exists_and_valid(output_path):
    """检查输出文件是否存在且有效"""
    if not os.path.exists(output_path):
        return False
    
    # 检查文件大小，太小的文件可能是失败的
    file_size = os.path.getsize(output_path)
    return file_size > 1000  # 至少1KB才认为是有效的

def find_pdf_files():
    """查找所有PDF文件"""
    pdf_files = []
    for root, dirs, files in os.walk(PDF_DIR):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return sorted(pdf_files)

def main():
    pdf_files = find_pdf_files()
    print(f"📁 找到 {len(pdf_files)} 个PDF文件")
    
    # 检查文件状态
    files_to_process = []
    skipped_files = []
    
    for pdf_file in pdf_files:
        output_path = get_output_filename(pdf_file)
        if file_exists_and_valid(output_path):
            skipped_files.append(pdf_file)
        else:
            files_to_process.append(pdf_file)
    
    print(f"\n📊 文件状态:")
    print(f"   跳过已存在: {len(skipped_files)}")
    print(f"   需要处理: {len(files_to_process)}")
    
    # 显示需要处理的文件
    if files_to_process:
        print(f"\n📝 需要处理的文件:")
        for i, file in enumerate(files_to_process[:20], 1):
            print(f"   {i:2d}. {Path(file).name}")
        if len(files_to_process) > 20:
            print(f"   ... 还有 {len(files_to_process) - 20} 个文件")
    
    # 显示已跳过的文件
    if skipped_files:
        print(f"\n✅ 已跳过的文件:")
        for i, file in enumerate(skipped_files[:10], 1):
            print(f"   {i:2d}. {Path(file).name}")
        if len(skipped_files) > 10:
            print(f"   ... 还有 {len(skipped_files) - 10} 个文件")

if __name__ == "__main__":
    main()