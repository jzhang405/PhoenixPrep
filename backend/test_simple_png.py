#!/usr/bin/env python3
"""
简单的PNG文件解析测试
使用现有的inference_macos.py脚本
"""
import os
import subprocess
import time

def test_png_parsing():
    """测试PNG文件解析"""
    print("=== 使用inference_macos.py解析PNG文件 ===")
    
    # 输入文件路径
    input_file = "../data/input-doc/英文论文.png"
    output_file = "test_output.html"
    model_path = os.path.expanduser("~/.cache/modelscope/hub/models/Alibaba-DT/Logics-Parsing")
    
    if not os.path.exists(input_file):
        print(f"错误: 文件不存在: {input_file}")
        return
    
    print(f"输入文件: {input_file}")
    print(f"输出文件: {output_file}")
    print(f"模型路径: {model_path}")
    
    try:
        # 使用inference_macos.py脚本
        cmd = [
            "python", "inference_macos.py",
            "--model_path", model_path,
            "--image_path", input_file,
            "--output_path", output_file,
            "--prompt", "QwenVL HTML"
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        print("开始解析PNG图片...")
        
        # 运行命令
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5分钟超时
        end_time = time.time()
        
        print(f"执行时间: {end_time - start_time:.2f}秒")
        
        if result.returncode == 0:
            print("✓ 解析成功")
            
            # 读取输出文件
            if os.path.exists(output_file):
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"\n=== 解析结果 ===")
                print(f"输出长度: {len(content)} 字符")
                print(f"前500字符预览:")
                print(content[:500] + "..." if len(content) > 500 else content)
                
                # 保存完整结果
                with open("full_output.html", 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"完整结果已保存到: full_output.html")
            else:
                print("✗ 输出文件未生成")
                
        else:
            print(f"✗ 解析失败，返回码: {result.returncode}")
            print(f"错误输出: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("✗ 解析超时（5分钟）")
    except Exception as e:
        print(f"解析过程中出错: {str(e)}")

if __name__ == "__main__":
    test_png_parsing()