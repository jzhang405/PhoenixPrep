"""
文档解析管理器
统一管理各种文档解析方法，包括Logics-Parsing、PDF解析、Word解析等
"""

import os
import asyncio
from typing import Dict, List, Optional
from pathlib import Path
import tempfile

from .logics_parsing_service import LogicsParsingService

class DocumentParserManager:
    """文档解析管理器"""
    
    def __init__(self, logics_parsing_path: str = None):
        """
        初始化文档解析管理器
        
        Args:
            logics_parsing_path: Logics-Parsing项目路径
        """
        self.logics_parsing_service = LogicsParsingService(logics_parsing_path)
        
    async def parse_document(self, 
                           content: bytes, 
                           file_type: str,
                           filename: Optional[str] = None) -> Dict:
        """
        解析文档内容
        
        Args:
            content: 文档内容字节
            file_type: 文件类型 ('pdf', 'word', 'image', 'html')
            filename: 文件名（可选）
            
        Returns:
            解析结果字典
        """
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(
                suffix=f".{file_type}", 
                delete=False,
                prefix="doc_parser_"
            ) as temp_file:
                temp_file.write(content)
                temp_path = temp_file.name
            
            # 根据文件类型选择解析方法
            if file_type.lower() in ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif']:
                # 图片文件使用Logics-Parsing
                result = await self.logics_parsing_service.convert_to_html(temp_path)
                
            elif file_type.lower() == 'pdf':
                # PDF文件 - 需要先转换为图片再使用Logics-Parsing
                # 这里可以添加PDF转图片的逻辑
                result = await self._parse_pdf_file(temp_path)
                
            elif file_type.lower() in ['doc', 'docx']:
                # Word文档
                result = await self._parse_word_file(temp_path)
                
            elif file_type.lower() == 'html':
                # HTML文件直接返回
                with open(temp_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                result = {
                    'success': True,
                    'content': html_content,
                    'file_type': 'html',
                    'message': 'HTML文件解析成功'
                }
                
            else:
                raise ValueError(f"不支持的文件类型: {file_type}")
            
            # 清理临时文件
            try:
                os.unlink(temp_path)
            except:
                pass
            
            # 添加文件名信息
            if filename:
                result['filename'] = filename
            
            return result
            
        except Exception as e:
            # 确保临时文件被清理
            try:
                if 'temp_path' in locals():
                    os.unlink(temp_path)
            except:
                pass
            
            return {
                'success': False,
                'error': str(e),
                'file_type': file_type,
                'filename': filename,
                'message': f'文档解析失败: {str(e)}'
            }
    
    async def _parse_pdf_file(self, pdf_path: str) -> Dict:
        """
        解析PDF文件
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            解析结果
        """
        # 这里可以实现PDF转图片的逻辑
        # 暂时返回错误，提示需要先转换为图片
        return {
            'success': False,
            'error': 'PDF文件需要先转换为图片格式才能使用Logics-Parsing解析',
            'suggestion': '请使用图片格式的文档或等待PDF直接解析功能的实现'
        }
    
    async def _parse_word_file(self, word_path: str) -> Dict:
        """
        解析Word文档
        
        Args:
            word_path: Word文件路径
            
        Returns:
            解析结果
        """
        # 这里可以实现Word文档解析逻辑
        # 暂时返回错误
        return {
            'success': False,
            'error': 'Word文档解析功能待实现',
            'suggestion': '请将Word文档转换为PDF或图片格式'
        }
    
    async def batch_parse_documents(self, 
                                  file_list: List[Dict]) -> Dict:
        """
        批量解析文档
        
        Args:
            file_list: 文件列表，每个元素包含 'content', 'file_type', 'filename'
            
        Returns:
            批量解析结果
        """
        results = []
        successful = 0
        failed = 0
        
        for file_info in file_list:
            try:
                result = await self.parse_document(
                    content=file_info['content'],
                    file_type=file_info['file_type'],
                    filename=file_info.get('filename')
                )
                results.append(result)
                
                if result['success']:
                    successful += 1
                else:
                    failed += 1
                    
            except Exception as e:
                results.append({
                    'success': False,
                    'error': str(e),
                    'filename': file_info.get('filename'),
                    'file_type': file_info['file_type']
                })
                failed += 1
        
        return {
            'total_files': len(file_list),
            'successful': successful,
            'failed': failed,
            'results': results
        }
    
    def get_supported_file_types(self) -> Dict:
        """获取支持的文件类型"""
        return {
            'images': ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif'],
            'documents': ['pdf', 'doc', 'docx'],
            'web': ['html', 'htm']
        }
    
    async def check_service_status(self) -> Dict:
        """检查服务状态"""
        logics_status = self.logics_parsing_service.check_requirements()
        
        return {
            'logics_parsing': logics_status,
            'overall_status': 'ready' if logics_status['all_requirements_met'] else 'not_ready',
            'supported_formats': self.get_supported_file_types()
        }
    
    async def extract_text_from_html(self, html_content: str) -> Dict:
        """
        从HTML内容中提取纯文本
        
        Args:
            html_content: HTML内容
            
        Returns:
            文本提取结果
        """
        try:
            import re
            from html import unescape
            
            # 移除HTML标签
            text = re.sub(r'<[^>]+>', ' ', html_content)
            
            # 解码HTML实体
            text = unescape(text)
            
            # 清理多余空格
            text = re.sub(r'\s+', ' ', text).strip()
            
            return {
                'success': True,
                'text_content': text,
                'character_count': len(text),
                'word_count': len(text.split())
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def analyze_document_structure(self, html_content: str) -> Dict:
        """
        分析文档结构
        
        Args:
            html_content: HTML内容
            
        Returns:
            结构分析结果
        """
        try:
            import re
            
            # 提取标题
            titles = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', html_content, re.IGNORECASE)
            
            # 提取段落
            paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html_content, re.IGNORECASE)
            
            # 提取表格
            tables = re.findall(r'<table[^>]*>(.*?)</table>', html_content, re.DOTALL | re.IGNORECASE)
            
            # 提取图片
            images = re.findall(r'<img[^>]*>', html_content, re.IGNORECASE)
            
            return {
                'success': True,
                'structure': {
                    'titles': [t.strip() for t in titles if t.strip()],
                    'paragraphs': [p.strip() for p in paragraphs if p.strip()],
                    'tables_count': len(tables),
                    'images_count': len(images)
                },
                'summary': {
                    'total_titles': len(titles),
                    'total_paragraphs': len(paragraphs),
                    'has_tables': len(tables) > 0,
                    'has_images': len(images) > 0
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }