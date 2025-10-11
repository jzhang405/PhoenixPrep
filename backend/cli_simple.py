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
from src.services.docx_parsing import DocxParsingService

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
        
        # 根据文件类型选择服务
        if input_path.lower().endswith(('.docx', '.doc')):
            # 使用Docx解析服务
            service = DocxParsingService()
            
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
                    output_path=output_path
                )
            
            result = asyncio.run(parse_document())
            
        else:
            # 使用快速Logics-Parsing服务
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
            if result.get('skipped'):
                click.echo(f"✅ {result['message']}")
                click.echo(f"📄 输入文件: {result['input_path']}")
                click.echo(f"📝 输出文件: {result['output_path']}")
            else:
                click.echo("\n🎉 解析成功!")
                
                if 'html_content' in result:
                    click.echo(f"📄 输入文件: {result['input_path']}")
                    click.echo(f"📝 输出文件: {result['output_path']}")
                    click.echo(f"📊 HTML长度: {len(result['html_content'])} 字符")
                    
                    click.echo("\n📋 内容预览:")
                    preview = result['html_content'][:300]
                    click.echo(f"{preview}...")
                    
                    click.echo(f"\n💾 已保存到: {result['output_path']}")
                elif 'pdf_path' in result:
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
        click.echo("🔍 服务状态检查:")
        
        # 检查快速Logics-Parsing服务
        fast_service = FastLogicsParsingService()
        fast_status = fast_service.check_service_status()
        
        click.echo(f"\n📡 快速Logics-Parsing服务:")
        click.echo(f"  🟢 状态: {fast_status['status']}")
        click.echo(f"  📡 API地址: {fast_status['api_url']}")
        click.echo(f"  ⏱️  响应: {fast_status.get('response_time', '未知')}")
        click.echo(f"  📝 消息: {fast_status['message']}")
        
        # 检查Docx解析服务
        docx_service = DocxParsingService()
        docx_status = docx_service.check_service_status()
        
        click.echo(f"\n📄 Docx解析服务:")
        click.echo(f"  🟢 状态: {docx_status['status']}")
        click.echo(f"  📝 消息: {docx_status['message']}")
        
        # 显示支持的文件格式
        click.echo(f"\n📁 支持的文件格式:")
        click.echo(f"  📄 Logics-Parsing: {', '.join(fast_service.get_supported_formats())}")
        click.echo(f"  📄 Docx解析: {', '.join(docx_service.get_supported_formats())}")
        
        if fast_status['status'] == 'online' and docx_status['status'] == 'online':
            click.echo("\n✅ 所有服务正常，可以开始解析!")
        else:
            click.echo(f"\n❌ 部分服务异常，请检查依赖")
            
    except Exception as e:
        click.echo(f"❌ 检查状态时出错: {str(e)}")

@cli.command()
@click.argument('question_path')
@click.argument('answer_path')
@click.option('--output-path', help='输出HTML文件路径（可选）')
def parse_qa(question_path, answer_path, output_path):
    """解析试题-答案对"""
    try:
        if not os.path.exists(question_path):
            click.echo(f"❌ 错误: 试题文件不存在: {question_path}")
            return
        if not os.path.exists(answer_path):
            click.echo(f"❌ 错误: 答案文件不存在: {answer_path}")
            return
        
        click.echo(f"🚀 开始解析试题-答案对:")
        click.echo(f"  试题: {question_path}")
        click.echo(f"  答案: {answer_path}")
        
        # 使用Docx解析服务
        service = DocxParsingService()
        
        # 检查服务状态
        status = service.check_service_status()
        if status['status'] != 'online':
            click.echo(f"❌ 服务不可用: {status}")
            return
        
        click.echo(f"✅ 服务状态: {status['status']}")
        
        # 使用asyncio运行异步方法
        async def parse_qa_pair():
            return await service.parse_question_answer_pair(
                question_path=question_path,
                answer_path=answer_path,
                output_path=output_path
            )
        
        result = asyncio.run(parse_qa_pair())
        
        if result['success']:
            click.echo("\n🎉 试题-答案对解析成功!")
            click.echo(f"📄 试题文件: {result['question_path']}")
            click.echo(f"📄 答案文件: {result['answer_path']}")
            click.echo(f"📝 输出文件: {result['output_path']}")
            click.echo(f"📊 HTML长度: {len(result['html_content'])} 字符")
            
            click.echo("\n📋 内容预览:")
            preview = result['html_content'][:300]
            click.echo(f"{preview}...")
            
            click.echo(f"\n💾 已保存到: {result['output_path']}")
        else:
            click.echo(f"❌ 解析失败: {result.get('error', '未知错误')}")
            
    except Exception as e:
        click.echo(f"❌ 解析时出错: {str(e)}")


def main():
    """主函数"""
    cli()

if __name__ == "__main__":
    main()