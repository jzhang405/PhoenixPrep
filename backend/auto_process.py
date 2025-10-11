#!/usr/bin/env python3
"""
自动PDF处理脚本
逐步加大等待时间处理剩余文件
"""

import os
import subprocess
import time
from pathlib import Path

PDF_DIR = "/Users/zhangcz/Downloads/naijing/真题库/北京123模考"
OUTPUT_DIR = "../data/parsed-html"
CLI_SCRIPT = "cli_simple.py"

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

def convert_pdf_with_retry(pdf_path, max_retries=3):
    """转换单个PDF文件，带重试机制"""
    output_path = get_output_filename(pdf_path)
    
    # 检查是否已存在有效输出
    if file_exists_and_valid(output_path):
        print(f"✅ 跳过已存在文件: {Path(pdf_path).name}")
        return {"success": True, "skipped": True, "file": pdf_path}
    
    for attempt in range(max_retries):
        # 逐步增加等待时间：1分钟、2分钟、3分钟
        wait_time = (attempt + 1) * 60
        print(f"⏰ 第{attempt+1}次尝试，等待 {wait_time//60} 分钟...")
        time.sleep(wait_time)
        
        print(f"🚀 开始转换: {Path(pdf_path).name} (第{attempt+1}次尝试)")
        
        try:
            # 运行转换命令
            start_time = time.time()
            result = subprocess.run(
                ["python", CLI_SCRIPT, "parse", pdf_path],
                timeout=300,  # 5分钟超时
                capture_output=True,
                text=True
            )
            
            elapsed_time = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ 转换成功: {Path(pdf_path).name} (耗时: {elapsed_time:.1f}秒)")
                return {"success": True, "file": pdf_path, "time": elapsed_time, "attempt": attempt+1}
            else:
                print(f"❌ 转换失败: {Path(pdf_path).name} (第{attempt+1}次)")
                print(f"   错误: {result.stderr[:200]}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ 超时: {Path(pdf_path).name} (第{attempt+1}次)")
        except Exception as e:
            print(f"❌ 异常: {Path(pdf_path).name} - {str(e)}")
    
    return {"success": False, "file": pdf_path, "error": "所有尝试都失败了"}

def main():
    pdf_files = find_pdf_files()
    print(f"📁 找到 {len(pdf_files)} 个PDF文件")
    
    # 先检查哪些文件需要处理
    files_to_process = []
    skipped_files = []
    
    for pdf_file in pdf_files:
        output_path = get_output_filename(pdf_file)
        if file_exists_and_valid(output_path):
            skipped_files.append(pdf_file)
        else:
            files_to_process.append(pdf_file)
    
    print(f"📊 文件状态:")
    print(f"   跳过已存在: {len(skipped_files)}")
    print(f"   需要处理: {len(files_to_process)}")
    
    if not files_to_process:
        print("🎉 所有文件都已处理完成!")
        return
    
    # 只处理前5个文件
    files_to_process = files_to_process[:5]
    
    # 统计结果
    results = {
        "total": len(files_to_process),
        "successful": 0,
        "failed": 0,
        "skipped": len(skipped_files),
        "details": []
    }
    
    print(f"\n🎯 开始自动处理前 {len(files_to_process)} 个文件...")
    print("=" * 50)
    
    for i, pdf_file in enumerate(files_to_process, 1):
        print(f"\n📦 处理文件 {i}/{len(files_to_process)}")
        print(f"📄 文件名: {Path(pdf_file).name}")
        
        result = convert_pdf_with_retry(pdf_file)
        results["details"].append(result)
        
        if result.get("skipped"):
            results["skipped"] += 1
        elif result["success"]:
            results["successful"] += 1
        else:
            results["failed"] += 1
        
        # 处理完一个文件后等待一段时间
        if i < len(files_to_process):
            wait_between = 30  # 30秒
            print(f"⏰ 等待 {wait_between} 秒后处理下一个文件...")
            time.sleep(wait_between)
    
    # 打印最终结果
    print(f"\n" + "=" * 50)
    print(f"📊 自动处理完成:")
    print(f"   总计处理: {results['total']}")
    print(f"   成功: {results['successful']}")
    print(f"   失败: {results['failed']}")
    print(f"   跳过: {results['skipped']}")
    
    if results['failed'] > 0:
        print(f"\n❌ 失败的文件:")
        for result in results['details']:
            if not result.get('success') and not result.get('skipped'):
                print(f"   - {Path(result['file']).name}")

if __name__ == "__main__":
    main()