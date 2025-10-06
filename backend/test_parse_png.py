#!/usr/bin/env python3
"""
测试PNG文件解析
"""
import os
import sys
import asyncio

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.logics_parsing_service import LogicsParsingService

async def test_png_parsing():
    """测试PNG文件解析"""
    print("=== 测试PNG文件解析 ===")
    
    # 输入文件路径
    input_file = "../data/input-doc/英文论文.png"
    
    if not os.path.exists(input_file):
        print(f"错误: 文件不存在: {input_file}")
        return
    
    print(f"输入文件: {input_file}")
    
    try:
        # 初始化Logics-Parsing服务
        logics_service = LogicsParsingService()
        
        # 检查服务状态
        status = logics_service.check_requirements()
        print(f"服务状态: {status}")
        
        if not status['all_requirements_met']:
            print("错误: Logics-Parsing服务未就绪")
            return
        
        # 转换PNG文件
        print("\n开始转换PNG文件...")
        result = await logics_service.convert_to_html(
            input_path=input_file,
            output_path=None,  # 自动生成输出路径
            prompt="QwenVL HTML"
        )
        
        print("\n=== 转换结果 ===")
        if result['success']:
            print(f"✓ 转换成功")
            print(f"输入文件: {result['input_path']}")
            print(f"输出文件: {result['output_path']}")
            print(f"HTML内容长度: {len(result['html_content'])} 字符")
            
            print("\n📝 HTML内容预览:")
            preview = result['html_content'][:500]
            print(f"{preview}...")
            
            print(f"\n💾 文件已保存到: {result['output_path']}")
        else:
            print(f"✗ 转换失败: {result.get('error', '未知错误')}")
            
    except Exception as e:
        print(f"转换过程中出错: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_png_parsing())