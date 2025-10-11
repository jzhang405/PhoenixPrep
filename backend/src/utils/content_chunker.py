"""
内容分块工具
用于处理超过API token限制的大文档
"""

import re
from typing import List, Dict
from pathlib import Path

class ContentChunker:
    """内容分块工具类"""
    
    def __init__(self, max_tokens: int = 120000, overlap_tokens: int = 1000):
        """
        初始化分块器
        
        Args:
            max_tokens: 每个块的最大token数
            overlap_tokens: 块之间的重叠token数
        """
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
    
    def estimate_tokens(self, text: str) -> int:
        """
        估计文本的token数量（简单估算）
        
        Args:
            text: 输入文本
            
        Returns:
            估计的token数量
        """
        # 简单估算：英文约4字符=1token，中文约2字符=1token
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_chars = len(text) - chinese_chars
        
        # 估算token数
        tokens = (english_chars // 4) + (chinese_chars // 2)
        return max(tokens, 1)
    
    def split_by_sentences(self, text: str) -> List[str]:
        """
        按句子分割文本
        
        Args:
            text: 输入文本
            
        Returns:
            句子列表
        """
        # 简单的句子分割
        sentences = re.split(r'[。！？.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def split_by_paragraphs(self, text: str) -> List[str]:
        """
        按段落分割文本
        
        Args:
            text: 输入文本
            
        Returns:
            段落列表
        """
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def chunk_content(self, content: str, chunk_strategy: str = "paragraph") -> List[Dict]:
        """
        将内容分块
        
        Args:
            content: 输入内容
            chunk_strategy: 分块策略 ("paragraph", "sentence", "fixed")
            
        Returns:
            分块结果列表
        """
        if self.estimate_tokens(content) <= self.max_tokens:
            return [{
                'content': content,
                'start_index': 0,
                'end_index': len(content),
                'estimated_tokens': self.estimate_tokens(content)
            }]
        
        chunks = []
        
        if chunk_strategy == "paragraph":
            segments = self.split_by_paragraphs(content)
        elif chunk_strategy == "sentence":
            segments = self.split_by_sentences(content)
        else:
            # 固定长度分块
            segments = self._split_fixed_length(content)
        
        current_chunk = ""
        current_tokens = 0
        start_index = 0
        
        for segment in segments:
            segment_tokens = self.estimate_tokens(segment)
            
            if current_tokens + segment_tokens > self.max_tokens:
                # 当前块已满，保存并开始新块
                if current_chunk:
                    chunks.append({
                        'content': current_chunk,
                        'start_index': start_index,
                        'end_index': start_index + len(current_chunk),
                        'estimated_tokens': current_tokens
                    })
                
                # 开始新块，包含重叠内容
                if chunks and self.overlap_tokens > 0:
                    # 从上一个块的末尾获取重叠内容
                    prev_chunk = chunks[-1]['content']
                    overlap_text = self._get_overlap_text(prev_chunk, self.overlap_tokens)
                    current_chunk = overlap_text + "\n\n" + segment
                    start_index = chunks[-1]['end_index'] - len(overlap_text)
                else:
                    current_chunk = segment
                    start_index = content.find(segment)
                
                current_tokens = self.estimate_tokens(current_chunk)
            else:
                # 添加到当前块
                if current_chunk:
                    current_chunk += "\n\n" + segment
                else:
                    current_chunk = segment
                    start_index = content.find(segment)
                current_tokens += segment_tokens
        
        # 添加最后一个块
        if current_chunk:
            chunks.append({
                'content': current_chunk,
                'start_index': start_index,
                'end_index': start_index + len(current_chunk),
                'estimated_tokens': current_tokens
            })
        
        return chunks
    
    def _split_fixed_length(self, text: str) -> List[str]:
        """固定长度分割"""
        # 按字符数分割，大约对应token数
        chunk_size = self.max_tokens * 3  # 粗略估算
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    def _get_overlap_text(self, text: str, overlap_tokens: int) -> str:
        """获取重叠文本"""
        words = text.split()
        overlap_words = max(int(overlap_tokens * 1.5), 50)  # 估算单词数
        
        if len(words) <= overlap_words:
            return text
        
        return ' '.join(words[-overlap_words:])
    
    def merge_chunk_results(self, chunk_results: List[Dict]) -> str:
        """
        合并分块处理结果
        
        Args:
            chunk_results: 分块处理结果列表
            
        Returns:
            合并后的完整结果
        """
        # 按原始位置排序
        sorted_results = sorted(chunk_results, key=lambda x: x.get('original_start', 0))
        
        # 合并内容，处理重叠
        merged_content = ""
        last_end = 0
        
        for result in sorted_results:
            content = result.get('processed_content', '')
            start = result.get('original_start', 0)
            end = result.get('original_end', len(content))
            
            if start > last_end:
                # 有间隙，添加原始内容
                gap_content = result.get('original_content', '')[last_end:start]
                merged_content += gap_content
            
            # 添加处理后的内容
            merged_content += content
            last_end = end
        
        return merged_content


def chunk_html_content(html_content: str, max_tokens: int = 120000) -> List[Dict]:
    """
    专门处理HTML内容的分块
    
    Args:
        html_content: HTML内容
        max_tokens: 最大token数
        
    Returns:
        分块结果
    """
    chunker = ContentChunker(max_tokens=max_tokens)
    
    # 先提取文本内容
    import re
    
    # 移除HTML标签获取纯文本
    clean_text = re.sub(r'<[^>]+>', ' ', html_content)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    # 分块处理
    chunks = chunker.chunk_content(clean_text, chunk_strategy="paragraph")
    
    # 为每个块添加HTML上下文
    for chunk in chunks:
        start = chunk['start_index']
        end = chunk['end_index']
        
        # 在原始HTML中找到对应的位置
        html_start = max(0, html_content.find(clean_text[start:start+100]))
        html_end = min(len(html_content), html_content.find(clean_text[end-100:end]) + 100)
        
        chunk['html_context'] = html_content[html_start:html_end]
    
    return chunks


def should_chunk_content(content: str, max_tokens: int = 120000) -> bool:
    """
    判断内容是否需要分块
    
    Args:
        content: 内容
        max_tokens: 最大token数
        
    Returns:
        是否需要分块
    """
    chunker = ContentChunker()
    estimated_tokens = chunker.estimate_tokens(content)
    return estimated_tokens > max_tokens