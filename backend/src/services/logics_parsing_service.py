"""
Logics-Parsing 文档解析服务
集成 Alibaba Logics-Parsing 项目，将PDF/图片转换为HTML
使用优化的CPU + FP16配置
"""

import os
import subprocess
import tempfile
import asyncio
from typing import Dict, List, Optional
from pathlib import Path
import shutil
import click

# 导入优化的服务
from .optimized_logics_parsing import OptimizedLogicsParsingService

class LogicsParsingService:
    """Logics-Parsing 文档解析服务"""
    
    def __init__(self, logics_parsing_path: str = None):
        """
        初始化Logics-Parsing服务
        
        Args:
            logics_parsing_path: Logics-Parsing项目路径，如果为None则使用默认路径
        """
        if logics_parsing_path is None:
            # 使用默认路径
            self.logics_parsing_path = "/Users/zhangcz/ws/python/src/github.com/alibaba/Logics-Parsing"
        else:
            self.logics_parsing_path = logics_parsing_path
        
        # 使用本地缓存中的模型路径
        home_dir = os.path.expanduser("~")
        self.model_path = os.path.join(home_dir, ".cache/modelscope/hub/models/Alibaba-DT/Logics-Parsing")
        
        # 使用项目内的输出目录
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.output_dir = os.path.join(project_root, "data/parsed-html")
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 初始化优化的服务
        self.optimized_service = OptimizedLogicsParsingService(self.model_path)
        
        # 检查模型是否存在
        self.check_model_exists()
    
    def check_model_exists(self):
        """检查模型文件是否存在，如果不存在则下载"""
        # 检查主要模型文件是否存在
        required_files = [
            "model-00001-of-00004.safetensors",
            "model-00002-of-00004.safetensors", 
            "model-00003-of-00004.safetensors",
            "model-00004-of-00004.safetensors",
            "model.safetensors.index.json"
        ]
        
        missing_files = []
        for file in required_files:
            file_path = os.path.join(self.model_path, file)
            if not os.path.exists(file_path):
                missing_files.append(file)
        
        if missing_files:
            print(f"模型文件缺失: {missing_files}")
            print(f"开始下载模型到: {self.model_path}")
            self.download_model()
        else:
            print(f"模型文件完整: {self.model_path}")
    
    def download_model(self):
        """使用modelscope CLI下载Logics-Parsing模型"""
        try:
            # 确保模型目录存在
            os.makedirs(self.model_path, exist_ok=True)
            
            # 使用modelscope CLI命令下载
            cmd = [
                "modelscope", "download", 
                "--model", "Alibaba-DT/Logics-Parsing",
                "--local-dir", self.model_path
            ]
            
            print(f"执行命令: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if result.returncode == 0:
                print(f"模型下载成功到: {self.model_path}")
                print(result.stdout)
            else:
                print(f"模型下载失败: {result.stderr}")
                raise Exception(f"模型下载失败: {result.stderr}")
                
        except subprocess.CalledProcessError as e:
            print(f"下载模型时出错: {str(e)}")
            print(f"错误输出: {e.stderr}")
            raise
        except Exception as e:
            print(f"下载模型时出错: {str(e)}")
            raise
    
    async def convert_to_html(self, 
                            input_path: str, 
                            output_path: Optional[str] = None,
                            prompt: str = "QwenVL HTML") -> Dict:
        """
        将PDF/图片文件转换为HTML
        
        Args:
            input_path: 输入文件路径 (PDF或图片)
            output_path: 输出HTML文件路径，如果为None则自动生成
            prompt: 解析提示词
            
        Returns:
            解析结果字典
        """
        try:
            # 检查输入文件是否存在
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"输入文件不存在: {input_path}")
            
            # 如果是PDF文件，需要先转换为图片
            if input_path.lower().endswith('.pdf'):
                # 这里需要先实现PDF转图片的功能
                # 暂时先返回错误
                raise NotImplementedError("PDF文件转换功能待实现，请先转换为图片格式")
            
            # 生成输出路径
            if output_path is None:
                input_name = Path(input_path).stem
                output_path = os.path.join(
                    self.output_dir, 
                    f"{input_name}_parsed.html"
                )
            
            # 运行修改版的Logics-Parsing推理（支持macOS）
            inference_script = os.path.join(os.path.dirname(__file__), "..", "..", "inference_macos.py")
            
            # 使用绝对路径
            abs_input_path = os.path.abspath(input_path)
            abs_output_path = os.path.abspath(output_path)
            
            cmd = [
                "python", inference_script,
                "--model_path", self.model_path,
                "--image_path", abs_input_path,
                "--output_path", abs_output_path,
                "--prompt", prompt
            ]
            
            # 异步执行推理
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.logics_parsing_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # 读取生成的HTML内容
                with open(output_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # 清理HTML内容
                cleaned_html = self.clean_html_content(html_content)
                
                return {
                    'success': True,
                    'input_path': input_path,
                    'output_path': output_path,
                    'html_content': cleaned_html,
                    'original_html': html_content,
                    'message': '文档解析成功'
                }
            else:
                error_msg = stderr.decode('utf-8') if stderr else '未知错误'
                raise Exception(f"Logics-Parsing推理失败: {error_msg}")
                
        except Exception as e:
            return {
                'success': False,
                'input_path': input_path,
                'error': str(e),
                'message': '文档解析失败'
            }
    
    def clean_html_content(self, html_content: str) -> str:
        """
        清理HTML内容，提取结构化文本
        
        Args:
            html_content: 原始HTML内容
            
        Returns:
            清理后的结构化文本
        """
        import re
        
        # 移除图片标签
        html_content = re.sub(
            r'<img\b[^>]*\bdata-bbox\s*=\s*"?\d+,\d+,\d+,\d+"?[^>]*\/?>',
            '',
            html_content,
            flags=re.IGNORECASE
        )
        
        # 简化段落标签
        html_content = re.sub(
            r'<p\b[^>]*>(.*?)<\/p>',
            r'\1\n',
            html_content,
            flags=re.DOTALL | re.IGNORECASE
        )
        
        # 移除特定div标签
        def strip_div(class_name: str, txt: str) -> str:
            pattern = re.compile(
                rf'\s*<div\b[^>]*class="{class_name}"[^>]*>(.*?)<\/div>\s*',
                flags=re.DOTALL | re.IGNORECASE
            )
            return pattern.sub(r' \1 ', txt)
        
        for cls in ['image', 'chemistry', 'table', 'formula', 'image caption']:
            html_content = strip_div(cls, html_content)
        
        # 清理多余空格
        html_content = re.sub(r'\s+', ' ', html_content).strip()
        
        return html_content
    
    async def batch_convert(self, 
                          input_files: List[str], 
                          output_dir: Optional[str] = None) -> Dict:
        """
        批量转换文件
        
        Args:
            input_files: 输入文件路径列表
            output_dir: 输出目录，如果为None则使用项目输出目录
            
        Returns:
            批量转换结果
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
                
                result = await self.convert_to_html(input_file, output_file)
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
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的输入格式"""
        return ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.pdf']
    
    def check_requirements(self) -> Dict:
        """检查系统要求"""
        requirements = {
            'logics_parsing_path': os.path.exists(self.logics_parsing_path),
            'model_path': os.path.exists(self.model_path),
            'inference_script': os.path.exists(os.path.join(self.logics_parsing_path, "inference.py")),
            'download_script': os.path.exists(os.path.join(self.logics_parsing_path, "download_model.py"))
        }
        
        all_met = all(requirements.values())
        
        return {
            'all_requirements_met': all_met,
            'requirements': requirements,
            'model_path': self.model_path
        }
    
    async def parse_text_directly(self, text: str) -> Dict:
        """
        直接使用优化的服务解析文本
        
        Args:
            text: 输入文本
            
        Returns:
            解析结果
        """
        try:
            print("使用优化的CPU + FP16服务解析文本...")
            result = await self.optimized_service.parse_document(text)
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '文本解析失败'
            }