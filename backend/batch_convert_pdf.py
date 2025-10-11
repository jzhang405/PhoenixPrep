#!/usr/bin/env python3
"""
批量PDF转换脚本
实现增量超时策略和文件存在检查
"""

import os
import asyncio
import subprocess
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# 配置参数
PDF_DIR = "/Users/zhangcz/Downloads/naijing/真题库/北京123模考"
OUTPUT_DIR = "../data/parsed-html"
CLI_SCRIPT = "cli_simple.py"

# 超时策略 (秒)
TIMEOUT_STRATEGY = [
    300,   # 5分钟
    600,   # 10分钟  
    900,   # 15分钟
]

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

def convert_pdf_with_timeout(pdf_path, timeout_seconds):
    """使用指定超时时间转换单个PDF文件"""
    output_path = get_output_filename(pdf_path)
    
    # 检查是否已存在有效输出
    if file_exists_and_valid(output_path):
        print(f"✅ 跳过已存在文件: {Path(pdf_path).name}")
        return {"success": True, "skipped": True, "file": pdf_path}
    
    print(f"🚀 开始转换: {Path(pdf_path).name} (超时: {timeout_seconds//60}分钟)")
    
    try:
        # 添加随机等待时间 (1-3分钟)
        wait_time = 60 + (time.time() % 120)  # 60-180秒
        print(f"⏰ 等待 {wait_time//60} 分钟...")
        time.sleep(wait_time)
        
        # 运行转换命令
        start_time = time.time()
        result = subprocess.run(
            ["python", CLI_SCRIPT, "parse", pdf_path],
            timeout=timeout_seconds,
            capture_output=True,
            text=True
        )
        
        elapsed_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ 转换成功: {Path(pdf_path).name} (耗时: {elapsed_time:.1f}秒)")
            return {"success": True, "file": pdf_path, "time": elapsed_time}
        else:
            print(f"❌ 转换失败: {Path(pdf_path).name}")
            print(f"   错误: {result.stderr[:200]}")
            return {"success": False, "file": pdf_path, "error": result.stderr}
            
    except subprocess.TimeoutExpired:
        print(f"⏰ 超时: {Path(pdf_path).name} (超时时间: {timeout_seconds//60}分钟)")
        return {"success": False, "file": pdf_path, "error": "timeout"}
    except Exception as e:
        print(f"❌ 异常: {Path(pdf_path).name} - {str(e)}")
        return {"success": False, "file": pdf_path, "error": str(e)}

def find_pdf_files():
    """查找所有PDF文件"""
    pdf_files = []
    for root, dirs, files in os.walk(PDF_DIR):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return sorted(pdf_files)

async def batch_convert_with_retry(batch_size=10):
    """批量转换PDF文件，使用增量超时策略"""
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
    
    # 统计结果
    results = {
        "total": len(pdf_files),
        "successful": 0,
        "failed": 0,
        "skipped": len(skipped_files),
        "details": []
    }
    
    # 失败的文件列表，用于重试
    failed_files = []
    
    # 分批处理 (只处理前20个文件作为测试)
    test_files = files_to_process[:20]
    batches = [test_files[i:i + batch_size] for i in range(0, len(test_files), batch_size)]
    
    for batch_num, batch in enumerate(batches, 1):
        print(f"\n📦 处理批次 {batch_num}/{len(batches)} (共{len(batch)}个文件)")
        
        # 第一轮转换
        print(f"🎯 第一轮转换 (超时: {TIMEOUT_STRATEGY[0]//60}分钟)")
        for pdf_file in batch:
            result = convert_pdf_with_timeout(pdf_file, TIMEOUT_STRATEGY[0])
            results["details"].append(result)
            
            if result.get("skipped"):
                results["skipped"] += 1
            elif result["success"]:
                results["successful"] += 1
            else:
                results["failed"] += 1
                failed_files.append(pdf_file)
    
    # 第二轮重试 (增加超时时间)
    if failed_files:
        print(f"\n🔄 第二轮重试 (超时: {TIMEOUT_STRATEGY[1]//60}分钟)")
        for pdf_file in failed_files:
            result = convert_pdf_with_timeout(pdf_file, TIMEOUT_STRATEGY[1])
            results["details"].append(result)
            
            if result["success"]:
                results["successful"] += 1
                results["failed"] -= 1
            # 如果仍然失败，保留在failed_files中用于下一轮
    
    # 第三轮重试 (最大超时时间)
    if failed_files:
        print(f"\n🔄 第三轮重试 (超时: {TIMEOUT_STRATEGY[2]//60}分钟)")
        for pdf_file in failed_files:
            result = convert_pdf_with_timeout(pdf_file, TIMEOUT_STRATEGY[2])
            results["details"].append(result)
            
            if result["success"]:
                results["successful"] += 1
                results["failed"] -= 1
    
    # 打印最终结果
    print(f"\n📊 转换结果:")
    print(f"   总计: {results['total']}")
    print(f"   成功: {results['successful']}")
    print(f"   失败: {results['failed']}")
    print(f"   跳过: {results['skipped']}")
    
    return results

if __name__ == "__main__":
    print("🚀 开始批量PDF转换")
    print(f"输入目录: {PDF_DIR}")
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"超时策略: {[t//60 for t in TIMEOUT_STRATEGY]} 分钟")
    print("-" * 50)
    
    asyncio.run(batch_convert_with_retry())