"""
错题分析服务
处理学生上传的错题图片，提供题目讲解和推荐练习
"""
from typing import Dict, List, Optional
import asyncio
from ..agents.document_analyzer import DocumentAnalyzerAgent
from ..agents.knowledge_analyzer import KnowledgeAnalyzerAgent
from ..agents.question_generator import QuestionGeneratorAgent

class MistakeAnalysisService:
    """错题分析服务"""
    
    def __init__(self):
        self.document_analyzer = DocumentAnalyzerAgent()
        self.knowledge_analyzer = KnowledgeAnalyzerAgent()
        self.question_generator = QuestionGeneratorAgent()
    
    async def analyze_mistake_image(self, image_content: bytes, student_id: str, subject: str = None) -> Dict:
        """
        分析错题图片
        
        Args:
            image_content: 图片内容字节
            student_id: 学生ID
            subject: 科目（可选）
            
        Returns:
            分析结果字典
        """
        try:
            # 1. 使用文档解析器分析图片内容
            analysis_result = await self.document_analyzer.analyze_image(image_content)
            
            # 2. 提取题目内容和知识点
            question_content = analysis_result.get('content', '')
            extracted_knowledge_points = analysis_result.get('knowledge_points', [])
            
            # 3. 使用知识分析器分析错题原因
            mistake_analysis = await self.knowledge_analyzer.analyze_mistake(
                question_content=question_content,
                knowledge_points=extracted_knowledge_points,
                student_id=student_id,
                subject=subject
            )
            
            # 4. 生成题目讲解
            explanation = await self._generate_explanation(
                question_content=question_content,
                mistake_analysis=mistake_analysis
            )
            
            # 5. 推荐相关练习
            recommendations = await self._generate_recommendations(
                student_id=student_id,
                knowledge_points=extracted_knowledge_points,
                mistake_type=mistake_analysis.get('mistake_type')
            )
            
            return {
                'success': True,
                'question_content': question_content,
                'knowledge_points': extracted_knowledge_points,
                'mistake_analysis': mistake_analysis,
                'explanation': explanation,
                'recommendations': recommendations,
                'confidence_score': analysis_result.get('confidence_score', 0.0)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'question_content': '',
                'knowledge_points': [],
                'mistake_analysis': {},
                'explanation': '',
                'recommendations': []
            }
    
    async def _generate_explanation(self, question_content: str, mistake_analysis: Dict) -> str:
        """生成题目讲解"""
        try:
            # 使用知识分析器生成详细讲解
            explanation = await self.knowledge_analyzer.generate_explanation(
                question_content=question_content,
                mistake_type=mistake_analysis.get('mistake_type'),
                difficulty_level=mistake_analysis.get('difficulty_level')
            )
            return explanation
        except Exception:
            return "暂时无法生成题目讲解，请稍后再试。"
    
    async def _generate_recommendations(self, student_id: str, knowledge_points: List[str], mistake_type: str) -> List[Dict]:
        """生成推荐练习"""
        try:
            # 使用题目生成器推荐相关练习
            recommendations = await self.question_generator.generate_recommendations(
                student_id=student_id,
                knowledge_points=knowledge_points,
                mistake_type=mistake_type,
                count=5  # 推荐5道相关题目
            )
            return recommendations
        except Exception:
            return []
    
    async def get_mistake_history(self, student_id: str, limit: int = 10) -> List[Dict]:
        """获取学生错题历史"""
        try:
            # 从数据库获取错题历史
            # 这里需要实现数据库查询逻辑
            return []
        except Exception as e:
            return []
    
    async def get_mistake_statistics(self, student_id: str) -> Dict:
        """获取错题统计"""
        try:
            # 统计学生的错题情况
            # 这里需要实现统计逻辑
            return {
                'total_mistakes': 0,
                'by_subject': {},
                'by_knowledge_point': {},
                'improvement_suggestions': []
            }
        except Exception as e:
            return {
                'total_mistakes': 0,
                'by_subject': {},
                'by_knowledge_point': {},
                'improvement_suggestions': []
            }