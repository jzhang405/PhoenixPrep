"""
试题-答案匹配服务
处理试题和答案分开的文件，将它们一一对应
"""
from typing import Dict, List, Tuple, Optional
import asyncio
import re
from difflib import SequenceMatcher

from ..services.document_parser import DocumentParserManager

# 临时占位符
class DocumentAnalyzerAgent:
    async def analyze_image(self, image_content):
        return {'content': '临时内容', 'knowledge_points': [], 'confidence_score': 0.0}

class QuestionAnswerMatcher:
    """试题-答案匹配服务"""
    
    def __init__(self):
        self.document_parser = DocumentParserManager()
        self.document_analyzer = DocumentAnalyzerAgent()
    
    async def match_questions_answers(
        self, 
        questions_content: bytes, 
        answers_content: bytes = None,
        questions_file_type: str = 'pdf',
        answers_file_type: str = 'pdf'
    ) -> Dict:
        """
        匹配试题和答案
        
        Args:
            questions_content: 试题文件内容
            answers_content: 答案文件内容
            questions_file_type: 试题文件类型
            answers_file_type: 答案文件类型
            
        Returns:
            匹配结果字典
        """
        try:
            # 1. 解析试题文件
            questions_result = await self.document_parser.parse_document(
                questions_content, questions_file_type
            )
            
            # 2. 判断是单个文件还是分开文件
            if answers_content is None:
                # 单个文件：从试题文件中提取答案
                questions, answers = self._extract_from_single_file(questions_result)
                file_type = 'single'
            else:
                # 分开文件：分别解析试题和答案
                answers_result = await self.document_parser.parse_document(
                    answers_content, answers_file_type
                )
                questions = self._extract_questions(questions_result)
                answers = self._extract_answers(answers_result)
                file_type = 'separate'
            
            # 3. 匹配试题和答案
            matched_pairs = await self._match_questions_with_answers(questions, answers)
            
            # 4. 验证匹配结果
            validation_result = self._validate_matches(matched_pairs)
            
            return {
                'success': True,
                'file_type': file_type,
                'total_questions': len(questions),
                'total_answers': len(answers),
                'matched_pairs': matched_pairs,
                'validation': validation_result,
                'questions_metadata': questions_result.get('metadata', {}),
                'answers_metadata': answers_result.get('metadata', {}) if answers_content else {}
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'total_questions': 0,
                'total_answers': 0,
                'matched_pairs': [],
                'validation': {}
            }
    
    def _extract_questions(self, questions_result: Dict) -> List[Dict]:
        """从试题解析结果中提取试题列表"""
        questions = []
        content = questions_result.get('content', '')
        
        # 使用正则表达式提取试题
        # 支持多种序号格式："1.", "2)", "一、", "二、", "(1)", "(2)" 等
        question_patterns = [
            r'(\d+[\.、\)]\s*[^\d]+?(?=\d+[\.、\)]|$))',  # 数字序号
            r'([一二三四五六七八九十]+[\.、]\s*[^一二三四五六七八九十]+?(?=[一二三四五六七八九十]+[\.、]|$))',  # 中文序号
            r'(\(\d+\)\s*[^\(]+?(?=\(\d+\)|$))',  # 括号数字序号
        ]
        
        for pattern in question_patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                question_text = match.group(1).strip()
                if len(question_text) > 10:  # 过滤掉太短的文本
                    questions.append({
                        'original_text': question_text,
                        'cleaned_text': self._clean_question_text(question_text),
                        'position': match.start(),
                        'question_number': self._extract_question_number(question_text)
                    })
        
        # 如果没有匹配到，尝试按行分割
        if not questions:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if len(line.strip()) > 10:
                    questions.append({
                        'original_text': line.strip(),
                        'cleaned_text': self._clean_question_text(line.strip()),
                        'position': i,
                        'question_number': i + 1
                    })
        
        return questions
    
    def _extract_answers(self, answers_result: Dict) -> List[Dict]:
        """从答案解析结果中提取答案列表"""
        answers = []
        content = answers_result.get('content', '')
        
        # 使用正则表达式提取答案
        # 假设答案以数字开头，如 "1.", "2.", "一、", "二、" 等
        answer_patterns = [
            r'(\d+[\.、]\s*[^\d]+?(?=\d+[\.、]|$))',  # 数字序号
            r'([一二三四五六七八九十]+[\.、]\s*[^一二三四五六七八九十]+?(?=[一二三四五六七八九十]+[\.、]|$))',  # 中文序号
            r'(答案\s*[：:]\s*[^\n]+)',  # 答案：格式
        ]
        
        for pattern in answer_patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                answer_text = match.group(1).strip()
                if len(answer_text) > 3:  # 答案可能较短
                    answers.append({
                        'original_text': answer_text,
                        'cleaned_text': self._clean_answer_text(answer_text),
                        'position': match.start(),
                        'answer_number': self._extract_answer_number(answer_text)
                    })
        
        # 如果没有匹配到，尝试按行分割
        if not answers:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if len(line.strip()) > 3:
                    answers.append({
                        'original_text': line.strip(),
                        'cleaned_text': self._clean_answer_text(line.strip()),
                        'position': i,
                        'answer_number': i + 1
                    })
        
        return answers
    
    def _extract_from_single_file(self, document_result: Dict) -> Tuple[List[Dict], List[Dict]]:
        """从单个文件中提取试题和答案"""
        content = document_result.get('content', '')
        
        # 尝试识别文件结构
        # 常见的结构：试题部分 + 答案部分
        
        # 方法1: 查找答案部分的分隔符
        answer_markers = [
            '答案', '参考答案', '标准答案', '解答', '解析', 
            'Answers', 'Answer Key', 'Solutions'
        ]
        
        questions_content = content
        answers_content = ''
        
        for marker in answer_markers:
            if marker in content:
                # 找到答案部分开始位置
                answer_start = content.find(marker)
                if answer_start != -1:
                    questions_content = content[:answer_start]
                    answers_content = content[answer_start:]
                    break
        
        # 提取试题
        questions = self._extract_questions({'content': questions_content})
        
        # 从答案部分提取答案
        if answers_content:
            answers = self._extract_answers({'content': answers_content})
        else:
            # 如果没有明显的答案部分，尝试从整个内容中提取
            answers = self._extract_answers({'content': content})
        
        return questions, answers
    
    def _clean_question_text(self, text: str) -> str:
        """清理试题文本"""
        # 移除序号
        text = re.sub(r'^\d+[\.、]\s*', '', text)
        text = re.sub(r'^[一二三四五六七八九十]+[\.、]\s*', '', text)
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _clean_answer_text(self, text: str) -> str:
        """清理答案文本"""
        # 移除"答案："等前缀
        text = re.sub(r'^答案\s*[：:]\s*', '', text)
        # 移除序号
        text = re.sub(r'^\d+[\.、]\s*', '', text)
        text = re.sub(r'^[一二三四五六七八九十]+[\.、]\s*', '', text)
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _extract_question_number(self, text: str) -> Optional[int]:
        """提取试题序号 - 支持多种格式"""
        # 匹配数字序号格式："1.", "2)", "(1)", "(2)"
        patterns = [
            r'^(\d+)[\.、]',  # 1. 或 1、
            r'^(\d+)\)',     # 1)
            r'^\((\d+)\)',  # (1)
        ]
        
        for pattern in patterns:
            match = re.match(pattern, text)
            if match:
                return int(match.group(1))
        
        # 匹配中文序号
        chinese_numbers = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, 
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
            '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20
        }
        
        # 匹配中文序号格式："一、", "二、"
        match = re.match(r'^([一二三四五六七八九十]+)[\.、]', text)
        if match:
            return chinese_numbers.get(match.group(1))
        
        return None
    
    def _extract_answer_number(self, text: str) -> Optional[int]:
        """提取答案序号"""
        return self._extract_question_number(text)
    
    async def _match_questions_with_answers(
        self, 
        questions: List[Dict], 
        answers: List[Dict]
    ) -> List[Dict]:
        """匹配试题和答案 - 主要基于题目标号对应"""
        matched_pairs = []
        
        # 方法1: 精确序号匹配 - 主要方法
        for question in questions:
            q_num = question.get('question_number')
            if q_num:
                # 查找相同序号的答案
                matching_answers = [
                    answer for answer in answers 
                    if answer.get('answer_number') == q_num
                ]
                
                if matching_answers:
                    # 如果有多个相同序号的答案，选择第一个
                    matched_answer = matching_answers[0]
                    matched_pairs.append({
                        'question': question,
                        'answer': matched_answer,
                        'match_method': 'exact_number',
                        'confidence': 1.0
                    })
                    # 从答案列表中移除已匹配的答案
                    answers.remove(matched_answer)
        
        # 方法2: 相对位置匹配 - 当序号不匹配时使用
        if len(matched_pairs) < min(len(questions), len(answers)):
            # 找出未匹配的试题和答案
            unmatched_questions = [
                q for q in questions 
                if not any(pair['question'] == q for pair in matched_pairs)
            ]
            unmatched_answers = [
                a for a in answers 
                if not any(pair['answer'] == a for pair in matched_pairs)
            ]
            
            # 按相对位置匹配
            for i in range(min(len(unmatched_questions), len(unmatched_answers))):
                matched_pairs.append({
                    'question': unmatched_questions[i],
                    'answer': unmatched_answers[i],
                    'match_method': 'relative_position',
                    'confidence': 0.7
                })
        
        # 方法3: 智能序号匹配 - 处理序号不连续的情况
        if len(matched_pairs) < min(len(questions), len(answers)):
            unmatched_questions = [
                q for q in questions 
                if not any(pair['question'] == q for pair in matched_pairs)
            ]
            unmatched_answers = [
                a for a in answers 
                if not any(pair['answer'] == a for pair in matched_pairs)
            ]
            
            # 尝试基于序号偏移进行匹配
            if unmatched_questions and unmatched_answers:
                # 计算可能的序号偏移
                q_nums = [q.get('question_number') for q in unmatched_questions if q.get('question_number')]
                a_nums = [a.get('answer_number') for a in unmatched_answers if a.get('answer_number')]
                
                if q_nums and a_nums:
                    # 找到最小的序号差
                    min_q = min(q_nums)
                    min_a = min(a_nums)
                    offset = min_a - min_q
                    
                    # 应用偏移进行匹配
                    for question in unmatched_questions:
                        q_num = question.get('question_number')
                        if q_num:
                            expected_a_num = q_num + offset
                            matching_answers = [
                                a for a in unmatched_answers 
                                if a.get('answer_number') == expected_a_num
                            ]
                            
                            if matching_answers:
                                matched_pairs.append({
                                    'question': question,
                                    'answer': matching_answers[0],
                                    'match_method': 'offset_number',
                                    'confidence': 0.9
                                })
                                unmatched_answers.remove(matching_answers[0])
        
        return matched_pairs
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _validate_matches(self, matched_pairs: List[Dict]) -> Dict:
        """验证匹配结果 - 重点关注序号匹配质量"""
        total_pairs = len(matched_pairs)
        if total_pairs == 0:
            return {
                'is_valid': False,
                'issues': ['没有匹配到任何试题-答案对'],
                'suggestions': ['请检查文件格式和内容']
            }
        
        issues = []
        suggestions = []
        
        # 分析匹配方法分布
        method_counts = {}
        for pair in matched_pairs:
            method = pair.get('match_method', 'unknown')
            method_counts[method] = method_counts.get(method, 0) + 1
        
        # 检查匹配置信度
        low_confidence_pairs = [
            pair for pair in matched_pairs 
            if pair.get('confidence', 0) < 0.7
        ]
        
        if low_confidence_pairs:
            issues.append(f'有 {len(low_confidence_pairs)} 对匹配置信度较低')
            suggestions.append('建议手动验证这些匹配结果')
        
        # 检查序号匹配比例
        exact_number_matches = method_counts.get('exact_number', 0)
        if exact_number_matches < total_pairs * 0.8:
            issues.append(f'精确序号匹配比例较低 ({exact_number_matches}/{total_pairs})')
            suggestions.append('请检查试题和答案的序号格式是否一致')
        
        # 检查序号连续性
        question_numbers = []
        for pair in matched_pairs:
            question = pair['question']
            if question.get('question_number'):
                question_numbers.append(question['question_number'])
        
        if question_numbers:
            question_numbers.sort()
            # 检查序号是否连续
            expected_sequence = list(range(min(question_numbers), max(question_numbers) + 1))
            missing_numbers = set(expected_sequence) - set(question_numbers)
            if missing_numbers:
                issues.append(f'试题序号不连续，缺失序号: {sorted(missing_numbers)}')
                suggestions.append('请检查是否有遗漏的试题')
        
        # 提供匹配质量报告
        match_quality = '高' if exact_number_matches >= total_pairs * 0.9 else '中' if exact_number_matches >= total_pairs * 0.7 else '低'
        
        return {
            'is_valid': len(issues) == 0,
            'total_pairs': total_pairs,
            'match_quality': match_quality,
            'exact_number_matches': exact_number_matches,
            'method_distribution': method_counts,
            'issues': issues,
            'suggestions': suggestions
        }
    
    async def get_matching_report(self, matched_pairs: List[Dict]) -> str:
        """生成匹配报告 - 重点关注序号匹配质量"""
        if not matched_pairs:
            return "没有匹配到试题-答案对"
        
        # 分析匹配方法分布
        method_counts = {}
        for pair in matched_pairs:
            method = pair.get('match_method', 'unknown')
            method_counts[method] = method_counts.get(method, 0) + 1
        
        # 计算序号匹配比例
        exact_number_matches = method_counts.get('exact_number', 0)
        match_quality = '高' if exact_number_matches >= len(matched_pairs) * 0.9 else '中' if exact_number_matches >= len(matched_pairs) * 0.7 else '低'
        
        report = f"试题-答案匹配报告\n"
        report += "=" * 50 + "\n"
        report += f"总匹配对数: {len(matched_pairs)}\n"
        report += f"匹配质量: {match_quality}\n"
        report += f"精确序号匹配: {exact_number_matches}/{len(matched_pairs)} ({exact_number_matches/len(matched_pairs)*100:.1f}%)\n"
        
        report += "\n匹配方法分布:\n"
        for method, count in method_counts.items():
            percentage = count / len(matched_pairs) * 100
            report += f"  {method}: {count} ({percentage:.1f}%)\n"
        
        report += "\n详细匹配结果:\n"
        report += "-" * 30 + "\n"
        
        for i, pair in enumerate(matched_pairs, 1):
            question = pair['question']
            answer = pair['answer']
            
            q_num = question.get('question_number', '无序号')
            a_num = answer.get('answer_number', '无序号')
            
            report += f"第 {i} 对 (题号 {q_num} → 答案 {a_num}):\n"
            report += f"  匹配方法: {pair.get('match_method', 'unknown')}\n"
            report += f"  置信度: {pair.get('confidence', 0):.2f}\n"
            report += f"  试题: {question['cleaned_text'][:50]}...\n"
            report += f"  答案: {answer['cleaned_text'][:30]}...\n\n"
        
        return report