#!/usr/bin/env python3
"""
使用优化的CPU+FP16服务解析PNG文件
"""
import os
import sys
import asyncio

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.optimized_logics_parsing import OptimizedLogicsParsingService

async def test_png_parsing():
    """测试PNG文件解析"""
    print("=== 使用优化的CPU+FP16服务解析PNG文件 ===")
    
    # 输入文件路径
    input_file = "../data/input-doc/英文论文.png"
    
    if not os.path.exists(input_file):
        print(f"错误: 文件不存在: {input_file}")
        return
    
    print(f"输入文件: {input_file}")
    
    try:
        # 初始化优化的服务
        service = OptimizedLogicsParsingService()
        print("✓ 优化服务初始化成功")
        
        # 加载模型
        print("\n加载模型...")
        service.load_model()
        print("✓ 模型加载成功")
        
        # 使用优化服务解析图片
        print("\n开始解析PNG图片...")
        result = await service.parse_image(input_file, prompt="QwenVL HTML")
        
        print("\n=== 解析结果 ===")
        if result['success']:
            print(f"✓ 解析成功")
            print(f"输入: {result['input']}")
            print(f"输出: {result['output']}")
            print(f"设备: {result['device']}")
        else:
            print(f"✗ 解析失败: {result.get('error', '未知错误')}")
            
        # 清理内存
        service.unload_model()
        print("\n✓ 模型已卸载，内存已释放")
        
    except Exception as e:
        print(f"解析过程中出错: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_png_parsing())