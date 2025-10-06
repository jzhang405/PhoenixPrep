#!/usr/bin/env python3
"""
凤凰备考系统命令行接口 - 简化版
仅包含当前可用的功能
"""
import click
import asyncio
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.document_parser import DocumentParserManager
from src.services.logics_parsing_service import LogicsParsingService

@click.group()
@click.version_option(version="0.1.0")
def cli():
    """凤凰备考系统命令行工具 - 简化版"""
    pass

@cli.group()
def document():
    """文档解析相关命令"""
    pass

@document.command()
@click.argument('input_path')
@click.option('--output-path', help='输出HTML文件路径（可选，自动生成）')
@click.option('--prompt', default='QwenVL HTML', help='解析提示词')
def parse(input_path, output_path, prompt):
    """使用Logics-Parsing解析文档为HTML"""
    try:
        if not os.path.exists(input_path):
            click.echo(f"错误: 输入文件不存在: {input_path}")
            return
        
        click.echo(f"解析文档: {input_path}")
        
        # 初始化Logics-Parsing服务
        logics_service = LogicsParsingService()
        
        # 检查服务状态
        status = logics_service.check_requirements()
        if not status['all_requirements_met']:
            click.echo("错误: Logics-Parsing服务未就绪")
            click.echo(f"状态: {status}")
            return
        
        # 使用asyncio运行异步方法
        async def convert_document():
            return await logics_service.convert_to_html(
                input_path=input_path,
                output_path=output_path,
                prompt=prompt
            )
        
        result = asyncio.run(convert_document())
        
        if result['success']:
            click.echo("\n=== 文档解析成功 ===")
            click.echo(f"输入文件: {result['input_path']}")
            click.echo(f"输出文件: {result['output_path']}")
            click.echo(f"HTML内容长度: {len(result['html_content'])} 字符")
            
            click.echo("\n📝 解析内容预览:")
            preview = result['html_content'][:500]
            click.echo(f"{preview}...")
            
            click.echo(f"\n💾 文件已保存到: {result['output_path']}")
        else:
            click.echo(f"解析失败: {result.get('error', '未知错误')}")
            
    except Exception as e:
        click.echo(f"文档解析时出错: {str(e)}")

@document.command()
def status():
    """检查文档解析服务状态"""
    try:
        click.echo("检查文档解析服务状态...")
        
        # 检查Logics-Parsing服务
        logics_service = LogicsParsingService()
        logics_status = logics_service.check_requirements()
        
        click.echo("\n=== Logics-Parsing 服务状态 ===")
        click.echo(f"整体状态: {'✓ 就绪' if logics_status['all_requirements_met'] else '✗ 未就绪'}")
        click.echo(f"模型路径: {logics_status['model_path']}")
        
        click.echo("\n要求检查:")
        for req_name, req_status in logics_status['requirements'].items():
            status_icon = "✓" if req_status else "✗"
            click.echo(f"  {status_icon} {req_name}: {'满足' if req_status else '不满足'}")
        
        # 检查文档解析管理器
        parser_manager = DocumentParserManager()
        
        # 使用asyncio运行异步方法
        async def get_parser_status():
            return await parser_manager.check_service_status()
        
        parser_status = asyncio.run(get_parser_status())
        
        click.echo("\n=== 文档解析管理器状态 ===")
        click.echo(f"整体状态: {parser_status['overall_status']}")
        
        click.echo("\n支持的文件格式:")
        for format_type, extensions in parser_status['supported_formats'].items():
            click.echo(f"  {format_type}: {', '.join(extensions)}")
        
        click.echo(f"\n💾 模型文件存储: {logics_service.model_path}")
        click.echo(f"📁 解析结果存储: {logics_service.output_dir}")
        
    except Exception as e:
        click.echo(f"检查服务状态时出错: {str(e)}")

@document.command()
def download_model():
    """下载Logics-Parsing模型"""
    try:
        click.echo("开始下载Logics-Parsing模型...")
        
        # 初始化服务，会自动下载模型
        logics_service = LogicsParsingService()
        
        click.echo("✓ 模型下载完成")
        click.echo(f"模型存储位置: {logics_service.model_path}")
        
    except Exception as e:
        click.echo(f"下载模型时出错: {str(e)}")

@document.command()
@click.argument('input_files', nargs=-1)
@click.option('--output-dir', help='输出目录（可选）')
def batch_parse(input_files, output_dir):
    """批量解析文档"""
    try:
        if not input_files:
            click.echo("错误: 请提供至少一个输入文件")
            return
        
        click.echo(f"批量解析 {len(input_files)} 个文件...")
        
        # 初始化Logics-Parsing服务
        logics_service = LogicsParsingService()
        
        # 使用asyncio运行异步方法
        async def batch_convert_documents():
            return await logics_service.batch_convert(
                input_files=list(input_files),
                output_dir=output_dir
            )
        
        result = asyncio.run(batch_convert_documents())
        
        click.echo("\n=== 批量解析结果 ===")
        click.echo(f"总文件数: {result['total_files']}")
        click.echo(f"成功: {result['successful']}")
        click.echo(f"失败: {result['failed']}")
        click.echo(f"输出目录: {result['output_dir']}")
        
        if result['successful'] > 0:
            click.echo("\n📝 成功解析的文件:")
            for res in result['results']:
                if res['success']:
                    click.echo(f"  ✓ {res['input_path']} → {res['output_path']}")
        
        if result['failed'] > 0:
            click.echo("\n❌ 失败的文件:")
            for res in result['results']:
                if not res['success']:
                    click.echo(f"  ✗ {res['input_path']}: {res.get('error', '未知错误')}")
                    
    except Exception as e:
        click.echo(f"批量解析时出错: {str(e)}")

def main():
    """主函数"""
    cli()

if __name__ == "__main__":
    main()