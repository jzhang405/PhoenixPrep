"""
快速的Logics-Parsing服务
使用远程Gradio API避免本地加载15GB模型
"""

import os
import asyncio
from typing import Dict, Optional
from pathlib import Path
from gradio_client import Client, handle_file

class FastLogicsParsingService:
    """快速的Logics-Parsing服务"""
    
    def __init__(self):
        """初始化快速服务"""
        self.client = Client("https://alibaba-dt-logics-parsing.ms.show/")
        self.api_url = "https://alibaba-dt-logics-parsing.ms.show/"
        
        # 使用项目内的输出目录
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.output_dir = os.path.join(project_root, "data/parsed-html")
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        print("✓ 快速Logics-Parsing服务初始化成功")
        print(f"  API地址: {self.api_url}")
        print(f"  输出目录: {self.output_dir}")
    
    async def parse_document(self, 
                           input_path: str, 
                           output_path: Optional[str] = None,
                           api_name: str = "/pdf_parse") -> Dict:
        """
        解析文档
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径，如果为None则自动生成
            api_name: API端点名称，可选 "/pdf_parse" 或 "/to_pdf"
            
        Returns:
            解析结果字典
        """
        try:
            # 检查输入文件是否存在
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"输入文件不存在: {input_path}")
            
            # 生成输出路径
            if output_path is None:
                input_name = Path(input_path).stem
                output_path = os.path.join(
                    self.output_dir, 
                    f"{input_name}_parsed.html"
                )
            
            # 检查输出文件是否已存在且有效
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                print(f"✅ 跳过已存在文件: {input_path}")
                return {
                    'success': True,
                    'input_path': input_path,
                    'output_path': output_path,
                    'skipped': True,
                    'message': '文件已存在，跳过解析'
                }
            
            print(f"开始解析文档: {input_path}")
            print(f"使用API: {api_name}")
            
            # 使用异步执行避免阻塞
            def sync_parse():
                return self.client.predict(
                    file_path=handle_file(input_path),
                    api_name=api_name
                )
            
            # 在异步环境中运行同步调用
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, sync_parse)
            
            # 处理不同API的返回结果
            if api_name == "/pdf_parse":
                # /pdf_parse返回6个元素的元组
                html_content = self._extract_html_content(result)
                
                # 保存HTML内容
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                return {
                    'success': True,
                    'input_path': input_path,
                    'output_path': output_path,
                    'html_content': html_content,
                    'raw_result': result,
                    'api_name': api_name,
                    'message': '文档解析成功'
                }
                
            elif api_name == "/to_pdf":
                # /to_pdf返回PDF文件路径
                return {
                    'success': True,
                    'input_path': input_path,
                    'pdf_path': result,
                    'api_name': api_name,
                    'message': '文档转换成功'
                }
            else:
                raise ValueError(f"不支持的API名称: {api_name}")
                
        except Exception as e:
            return {
                'success': False,
                'input_path': input_path,
                'error': str(e),
                'api_name': api_name,
                'message': '文档解析失败'
            }
    
    def _extract_html_content(self, result) -> str:
        """
        从/pdf_parse结果中提取HTML内容
        
        Args:
            result: /pdf_parse API返回的6元素元组
            
        Returns:
            清理后的HTML内容
        """
        if not isinstance(result, (list, tuple)) or len(result) < 6:
            return str(result)
        
        # 通常第一个元素包含HTML内容
        html_content = result[0]
        
        # 清理HTML内容
        cleaned_html = self._clean_html_content(html_content)
        
        return cleaned_html
    
    def _clean_html_content(self, html_content: str) -> str:
        """
        清理HTML内容
        
        Args:
            html_content: 原始HTML内容
            
        Returns:
            清理后的HTML内容
        """
        import re
        
        # 简化HTML标签
        html_content = re.sub(r'<div\b[^>]*data-bbox="[^"]*"[^>]*>', '<div>', html_content)
        
        # 移除多余的空格和换行
        html_content = re.sub(r'\s+', ' ', html_content).strip()
        
        # 恢复合理的段落分隔
        html_content = html_content.replace('</div>', '</div>\n')
        html_content = html_content.replace('</table>', '</table>\n')
        html_content = html_content.replace('</tr>', '</tr>\n')
        
        return html_content
    
    async def batch_parse(self, 
                         input_files: list, 
                         output_dir: Optional[str] = None,
                         api_name: str = "/pdf_parse") -> Dict:
        """
        批量解析文档
        
        Args:
            input_files: 输入文件路径列表
            output_dir: 输出目录，如果为None则使用项目输出目录
            api_name: API端点名称
            
        Returns:
            批量解析结果
        """
        if output_dir is None:
            output_dir = self.output_dir
        
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        successful = 0
        failed = 0
        
        for input_file in input_files:
            try:
                output_file = os.path.join(
                    output_dir, 
                    f"{Path(input_file).stem}_parsed.html"
                )
                
                result = await self.parse_document(input_file, output_file, api_name)
                results.append(result)
                
                if result['success']:
                    successful += 1
                else:
                    failed += 1
                    
            except Exception as e:
                results.append({
                    'success': False,
                    'input_path': input_file,
                    'error': str(e)
                })
                failed += 1
        
        return {
            'total_files': len(input_files),
            'successful': successful,
            'failed': failed,
            'output_dir': output_dir,
            'results': results
        }
    
    def get_supported_formats(self) -> list:
        """获取支持的输入格式"""
        return ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.pdf']
    
    def check_service_status(self) -> Dict:
        """检查服务状态"""
        try:
            # 简单测试连接
            test_result = self.client.predict(
                file_path=handle_file('https://github.com/gradio-app/gradio/raw/main/test/test_files/sample_file.pdf'),
                api_name="/pdf_parse"
            )
            
            return {
                'status': 'online',
                'api_url': self.api_url,
                'response_time': '正常',
                'message': '服务运行正常'
            }
            
        except Exception as e:
            return {
                'status': 'offline',
                'api_url': self.api_url,
                'error': str(e),
                'message': '服务不可用'
            }

# 测试函数
async def test_fast_service():
    """测试快速服务"""
    service = FastLogicsParsingService()
    
    # 测试服务状态
    status = service.check_service_status()
    print(f"服务状态: {status}")
    
    # 测试本地PNG文件解析
    local_file = "../data/input-doc/英文论文.png"
    if os.path.exists(local_file):
        print(f"\n测试解析PNG文件: {local_file}")
        result = await service.parse_document(local_file)
        
        if result['success']:
            print("✓ 解析成功!")
            print(f"输出文件: {result['output_path']}")
            print(f"HTML内容长度: {len(result['html_content'])} 字符")
            print(f"内容预览: {result['html_content'][:200]}...")
        else:
            print(f"✗ 解析失败: {result.get('error')}")
    else:
        print(f"测试文件不存在: {local_file}")

if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_fast_service())