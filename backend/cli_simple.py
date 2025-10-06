#!/usr/bin/env python3
"""
快速Logics-Parsing命令行工具
使用远程API，无需本地模型，速度快10-20倍
"""
import click
import asyncio
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.fast_logics_parsing import FastLogicsParsingService

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """快速Logics-Parsing命令行工具"""
    pass

@cli.command()
@click.argument('input_path')
@click.option('--output-path', help='输出HTML文件路径（可选）')
@click.option('--api-name', default='/pdf_parse', type=click.Choice(['/pdf_parse', '/to_pdf']), help='API端点选择')
def parse(input_path, output_path, api_name):
    """快速解析文档"""
    try:
        if not os.path.exists(input_path):
            click.echo(f"❌ 错误: 文件不存在: {input_path}")
            return
        
        click.echo(f"🚀 开始解析: {input_path}")
        
        # 初始化快速服务
        service = FastLogicsParsingService()
        
        # 检查服务状态
        status = service.check_service_status()
        if status['status'] != 'online':
            click.echo(f"❌ 服务不可用: {status}")
            return
        
        click.echo(f"✅ 服务状态: {status['status']}")
        
        # 使用asyncio运行异步方法
        async def parse_document():
            return await service.parse_document(
                input_path=input_path,
                output_path=output_path,
                api_name=api_name
            )
        
        result = asyncio.run(parse_document())
        
        if result['success']:
            click.echo("\n🎉 解析成功!")
            
            if api_name == '/pdf_parse':
                click.echo(f"📄 输入文件: {result['input_path']}")
                click.echo(f"📝 输出文件: {result['output_path']}")
                click.echo(f"📊 HTML长度: {len(result['html_content'])} 字符")
                
                click.echo("\n📋 内容预览:")
                preview = result['html_content'][:300]
                click.echo(f"{preview}...")
                
                click.echo(f"\n💾 已保存到: {result['output_path']}")
            else:
                click.echo(f"📄 输入文件: {result['input_path']}")
                click.echo(f"📄 输出PDF: {result['pdf_path']}")
                click.echo(f"💾 PDF已生成")
        else:
            click.echo(f"❌ 解析失败: {result.get('error', '未知错误')}")
            
    except Exception as e:
        click.echo(f"❌ 解析时出错: {str(e)}")

@cli.command()
def status():
    """检查服务状态"""
    try:
        service = FastLogicsParsingService()
        status = service.check_service_status()
        
        click.echo("🔍 服务状态检查:")
        click.echo(f"  📡 API地址: {status['api_url']}")
        click.echo(f"  🟢 状态: {status['status']}")
        click.echo(f"  ⏱️  响应: {status.get('response_time', '未知')}")
        click.echo(f"  📝 消息: {status['message']}")
        
        if status['status'] == 'online':
            click.echo("\n✅ 服务正常，可以开始解析!")
        else:
            click.echo(f"\n❌ 服务异常: {status.get('error', '未知错误')}")
            
    except Exception as e:
        click.echo(f"❌ 检查状态时出错: {str(e)}")


def main():
    """主函数"""
    cli()

if __name__ == "__main__":
    main()