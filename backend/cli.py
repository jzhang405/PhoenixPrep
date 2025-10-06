#!/usr/bin/env python3
"""
凤凰备考系统命令行接口
用于调试和测试后端功能
"""
import click
import asyncio
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fastapi import FastAPI
from fastapi.testclient import TestClient

# 导入服务模块
from src.services.document_parser import DocumentParserManager
from src.services.mistake_analysis import MistakeAnalysisService
from src.services.question_answer_matcher import QuestionAnswerMatcher

# 创建FastAPI应用实例
app = FastAPI()

@click.group()
@click.version_option(version="0.1.0")
def cli():
    """凤凰备考系统命令行工具"""
    pass

@cli.group()
def upload():
    """文件上传相关命令"""
    pass

@upload.command()
@click.argument('file_path')
@click.option('--file-type', type=click.Choice(['pdf', 'word', 'image']), help='文件类型')
async def process_file(file_path, file_type):
    """处理单个文件上传"""
    try:
        if not os.path.exists(file_path):
            click.echo(f"错误: 文件不存在: {file_path}")
            return
        
        # 自动检测文件类型
        if not file_type:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.pdf':
                file_type = 'pdf'
            elif ext in ['.doc', '.docx']:
                file_type = 'word'
            elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
                file_type = 'image'
            else:
                click.echo(f"错误: 不支持的文件类型: {ext}")
                return
        
        click.echo(f"处理文件: {file_path} (类型: {file_type})")
        
        # 初始化服务
        parser_manager = DocumentParserManager()
        
        # 模拟文件上传
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # 解析文档
        result = await parser_manager.parse_document(file_content, file_type)
        
        click.echo(f"解析结果:")
        click.echo(f"  文本内容长度: {len(result.get('content', ''))}")
        click.echo(f"  提取的问题数量: {len(result.get('questions', []))}")
        click.echo(f"  元数据: {result.get('metadata', {})}")
        
    except Exception as e:
        click.echo(f"处理文件时出错: {str(e)}")

@cli.group()
def questions():
    """题目管理相关命令"""
    pass

# @questions.command()
# @click.option('--subject', help='科目筛选')
# @click.option('--difficulty', type=click.Choice(['easy', 'medium', 'hard']), help='难度筛选')
# @click.option('--limit', default=10, help='返回数量限制')
# async def list(subject, difficulty, limit):
#     """列出题目"""
#     try:
#         question_service = QuestionService()
#         filters = {}
#         if subject:
#             filters['subject'] = subject
#         if difficulty:
#             filters['difficulty'] = difficulty
#         
#         questions = await question_service.get_questions(filters, limit)
#         
#         click.echo(f"找到 {len(questions)} 个题目:")
#         for i, q in enumerate(questions, 1):
#             click.echo(f"  {i}. ID: {q.get('id')}, 科目: {q.get('subject')}, 难度: {q.get('difficulty')}")
#             click.echo(f"     内容: {q.get('content', '')[:50]}...")
#             
#     except Exception as e:
#         click.echo(f"获取题目列表时出错: {str(e)}")

# @questions.command()
# @click.argument('question_id')
# async def get(question_id):
#     """获取单个题目详情"""
#     try:
#         question_service = QuestionService()
#         question = await question_service.get_question(question_id)
#         
#         if question:
#             click.echo(f"题目详情:")
#             click.echo(f"  ID: {question.get('id')}")
#             click.echo(f"  科目: {question.get('subject')}")
#             click.echo(f"  难度: {question.get('difficulty')}")
#             click.echo(f"  内容: {question.get('content')}")
#             click.echo(f"  答案: {question.get('answer')}")
#             click.echo(f"  解析: {question.get('explanation')}")
#         else:
#             click.echo(f"未找到题目: {question_id}")
#             
#     except Exception as e:
#         click.echo(f"获取题目详情时出错: {str(e)}")

@cli.group()
def analysis():
    """学习分析相关命令"""
    pass

# @analysis.command()
# @click.argument('student_id')
# async def performance(student_id):
#     """获取学生表现分析"""
#     try:
#         analysis_service = AnalysisService()
#         performance_data = await analysis_service.get_student_performance(student_id)
#         
#         click.echo(f"学生 {student_id} 表现分析:")
#         click.echo(f"  总体得分: {performance_data.get('overall_score', 0)}")
#         click.echo(f"  知识点掌握情况:")
#         
#         for knowledge_point in performance_data.get('knowledge_points', []):
#             click.echo(f"    - {knowledge_point.get('name')}: {knowledge_point.get('mastery_level')}%")
#             
#         click.echo(f"  薄弱环节: {', '.join(performance_data.get('weak_areas', []))}")
#         
#     except Exception as e:
#         click.echo(f"获取表现分析时出错: {str(e)}")

# @analysis.command()
# @click.argument('student_id')
# async def recommendations(student_id):
#     """获取学习建议"""
#     try:
#         analysis_service = AnalysisService()
#         recommendations = await analysis_service.get_recommendations(student_id)
#         
#         click.echo(f"学生 {student_id} 学习建议:")
#         for i, rec in enumerate(recommendations, 1):
#             click.echo(f"  {i}. {rec.get('type')}: {rec.get('content')}")
#             
#     except Exception as e:
#         click.echo(f"获取学习建议时出错: {str(e)}")

@cli.group()
def test():
    """测试相关命令"""
    pass

@test.command()
@click.option('--endpoint', default='/', help='测试端点')
def api(endpoint):
    """测试API端点"""
    try:
        with TestClient(app) as client:
            response = client.get(endpoint)
            click.echo(f"API测试结果:")
            click.echo(f"  状态码: {response.status_code}")
            click.echo(f"  响应: {response.json()}")
            
    except Exception as e:
        click.echo(f"API测试时出错: {str(e)}")

@test.command()
def services():
    """测试服务功能"""
    try:
        click.echo("测试服务功能...")
        
        # 测试文档解析服务
        parser_manager = DocumentParserManager()
        click.echo("✓ 文档解析服务初始化成功")
        
        # 测试错题分析服务
        mistake_service = MistakeAnalysisService()
        click.echo("✓ 错题分析服务初始化成功")
        
        # 测试试题-答案匹配服务
        matcher = QuestionAnswerMatcher()
        click.echo("✓ 试题-答案匹配服务初始化成功")
        
        click.echo("所有服务测试通过!")
        
    except Exception as e:
        click.echo(f"服务测试时出错: {str(e)}")

@cli.group()
def mistake():
    """错题分析相关命令"""
    pass

@mistake.command()
@click.argument('image_path')
@click.option('--student-id', required=True, help='学生ID')
@click.option('--subject', help='科目')
async def analyze(image_path, student_id, subject):
    """分析错题图片"""
    try:
        if not os.path.exists(image_path):
            click.echo(f"错误: 图片文件不存在: {image_path}")
            return
        
        click.echo(f"分析错题图片: {image_path}")
        click.echo(f"学生ID: {student_id}")
        if subject:
            click.echo(f"科目: {subject}")
        
        # 初始化错题分析服务
        mistake_service = MistakeAnalysisService()
        
        # 读取图片内容
        with open(image_path, 'rb') as f:
            image_content = f.read()
        
        # 分析错题
        result = await mistake_service.analyze_mistake_image(
            image_content=image_content,
            student_id=student_id,
            subject=subject
        )
        
        if result['success']:
            click.echo("\n=== 错题分析结果 ===")
            click.echo(f"识别置信度: {result.get('confidence_score', 0) * 100:.1f}%")
            
            click.echo("\n📝 题目内容:")
            click.echo(result.get('question_content', '未识别到题目内容'))
            
            click.echo("\n🎯 涉及知识点:")
            for kp in result.get('knowledge_points', []):
                click.echo(f"  - {kp}")
            
            click.echo("\n🔍 错题分析:")
            mistake_analysis = result.get('mistake_analysis', {})
            click.echo(f"  错误类型: {mistake_analysis.get('mistake_type', '未知')}")
            click.echo(f"  难度等级: {mistake_analysis.get('difficulty_level', '未知')}")
            click.echo(f"  原因分析: {mistake_analysis.get('reason', '未知')}")
            
            click.echo("\n📚 题目讲解:")
            click.echo(result.get('explanation', '暂无讲解'))
            
            click.echo("\n💡 推荐练习:")
            recommendations = result.get('recommendations', [])
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    click.echo(f"  {i}. {rec.get('title', '推荐题目')}")
                    click.echo(f"     知识点: {rec.get('knowledge_point', '未知')}")
                    click.echo(f"     难度: {rec.get('difficulty', '未知')}")
            else:
                click.echo("  暂无推荐练习")
                
        else:
            click.echo(f"分析失败: {result.get('error', '未知错误')}")
            
    except Exception as e:
        click.echo(f"分析错题时出错: {str(e)}")

@mistake.command()
@click.argument('student_id')
@click.option('--limit', default=10, help='显示数量限制')
async def history(student_id, limit):
    """查看错题历史"""
    try:
        mistake_service = MistakeAnalysisService()
        history = await mistake_service.get_mistake_history(student_id, limit)
        
        click.echo(f"学生 {student_id} 的错题历史:")
        if history:
            for i, item in enumerate(history, 1):
                click.echo(f"  {i}. 时间: {item.get('timestamp', '未知')}")
                click.echo(f"     题目: {item.get('question_content', '')[:50]}...")
                click.echo(f"     知识点: {', '.join(item.get('knowledge_points', []))}")
                click.echo()
        else:
            click.echo("  暂无错题记录")
            
    except Exception as e:
        click.echo(f"获取错题历史时出错: {str(e)}")

@mistake.command()
@click.argument('student_id')
async def statistics(student_id):
    """查看错题统计"""
    try:
        mistake_service = MistakeAnalysisService()
        stats = await mistake_service.get_mistake_statistics(student_id)
        
        click.echo(f"学生 {student_id} 的错题统计:")
        click.echo(f"  总错题数: {stats.get('total_mistakes', 0)}")
        
        click.echo("\n📊 按科目统计:")
        for subject, count in stats.get('by_subject', {}).items():
            click.echo(f"  - {subject}: {count} 题")
        
        click.echo("\n🎯 按知识点统计:")
        for kp, count in stats.get('by_knowledge_point', {}).items():
            click.echo(f"  - {kp}: {count} 题")
        
        click.echo("\n💡 改进建议:")
        for suggestion in stats.get('improvement_suggestions', []):
            click.echo(f"  - {suggestion}")
            
    except Exception as e:
        click.echo(f"获取错题统计时出错: {str(e)}")

@cli.command()
def health():
    """检查系统健康状态"""
    try:
        with TestClient(app) as client:
            response = client.get("/health")
            if response.status_code == 200:
                click.echo("✓ 系统健康状态: 正常")
            else:
                click.echo(f"✗ 系统健康状态: 异常 (状态码: {response.status_code})")
                
    except Exception as e:
        click.echo(f"✗ 系统健康检查失败: {str(e)}")

@cli.group()
def match():
    """试题-答案匹配相关命令"""
    pass

@cli.group()
def document():
    """文档解析相关命令"""
    pass

@document.command()
@click.argument('input_path')
@click.option('--output-path', help='输出HTML文件路径（可选，自动生成）')
@click.option('--api-name', default='/pdf_parse', type=click.Choice(['/pdf_parse', '/to_pdf']), help='API端点选择')
async def parse(input_path, output_path, api_name):
    """使用快速Logics-Parsing解析文档"""
    try:
        if not os.path.exists(input_path):
            click.echo(f"错误: 输入文件不存在: {input_path}")
            return
        
        click.echo(f"解析文档: {input_path}")
        
        # 初始化快速Logics-Parsing服务
        from src.services.fast_logics_parsing import FastLogicsParsingService
        fast_service = FastLogicsParsingService()
        
        # 检查服务状态
        status = fast_service.check_service_status()
        if status['status'] != 'online':
            click.echo(f"错误: Logics-Parsing服务不可用")
            click.echo(f"状态: {status}")
            return
        
        click.echo(f"✓ 服务状态: {status['status']}")
        
        # 解析文档
        result = await fast_service.parse_document(
            input_path=input_path,
            output_path=output_path,
            api_name=api_name
        )
        
        if result['success']:
            click.echo("\n=== 文档解析成功 ===")
            click.echo(f"输入文件: {result['input_path']}")
            click.echo(f"输出文件: {result.get('output_path', result.get('pdf_path', 'N/A'))}")
            
            if api_name == '/pdf_parse':
                click.echo(f"HTML内容长度: {len(result['html_content'])} 字符")
                
                click.echo("\n📝 解析内容预览:")
                preview = result['html_content'][:500]
                click.echo(f"{preview}...")
                
                click.echo(f"\n💾 HTML文件已保存到: {result['output_path']}")
            else:
                click.echo(f"💾 PDF文件已生成: {result['pdf_path']}")
        else:
            click.echo(f"解析失败: {result.get('error', '未知错误')}")
            
    except Exception as e:
        click.echo(f"文档解析时出错: {str(e)}")

@document.command()
async def status():
    """检查文档解析服务状态"""
    try:
        from src.services.fast_logics_parsing import FastLogicsParsingService
        from src.services.document_parser import DocumentParserManager
        
        click.echo("检查文档解析服务状态...")
        
        # 检查快速Logics-Parsing服务
        fast_service = FastLogicsParsingService()
        fast_status = fast_service.check_service_status()
        
        click.echo("\n=== 快速Logics-Parsing 服务状态 ===")
        click.echo(f"整体状态: {'✓ 在线' if fast_status['status'] == 'online' else '✗ 离线'}")
        click.echo(f"API地址: {fast_status['api_url']}")
        click.echo(f"响应时间: {fast_status.get('response_time', '未知')}")
        
        click.echo("\n支持的文件格式:")
        for fmt in fast_service.get_supported_formats():
            click.echo(f"  - {fmt}")
        
        # 检查文档解析管理器
        parser_manager = DocumentParserManager()
        parser_status = await parser_manager.check_service_status()
        
        click.echo("\n=== 文档解析管理器状态 ===")
        click.echo(f"整体状态: {parser_status['overall_status']}")
        
        click.echo("\n支持的文件格式:")
        for format_type, extensions in parser_status['supported_formats'].items():
            click.echo(f"  {format_type}: {', '.join(extensions)}")
        
        click.echo(f"\n💾 输出目录: {fast_service.output_dir}")
        
    except Exception as e:
        click.echo(f"检查服务状态时出错: {str(e)}")

@document.command()
def download_model():
    """下载Logics-Parsing模型"""
    try:
        click.echo("⚠️  注意: 快速服务使用远程API，无需下载本地模型")
        click.echo("✓ 快速服务已就绪，可以直接使用")
        click.echo("  如需使用本地模型，请参考: src/services/logics_parsing_service.py")
        
    except Exception as e:
        click.echo(f"操作时出错: {str(e)}")

@document.command()
@click.argument('input_files', nargs=-1)
@click.option('--output-dir', help='输出目录（可选）')
@click.option('--api-name', default='/pdf_parse', type=click.Choice(['/pdf_parse', '/to_pdf']), help='API端点选择')
async def batch_parse(input_files, output_dir, api_name):
    """批量解析文档"""
    try:
        if not input_files:
            click.echo("错误: 请提供至少一个输入文件")
            return
        
        click.echo(f"批量解析 {len(input_files)} 个文件...")
        
        # 初始化快速Logics-Parsing服务
        from src.services.fast_logics_parsing import FastLogicsParsingService
        fast_service = FastLogicsParsingService()
        
        # 批量解析
        result = await fast_service.batch_parse(
            input_files=list(input_files),
            output_dir=output_dir,
            api_name=api_name
        )
        
        click.echo("\n=== 批量解析结果 ===")
        click.echo(f"总文件数: {result['total_files']}")
        click.echo(f"成功: {result['successful']}")
        click.echo(f"失败: {result['failed']}")
        click.echo(f"输出目录: {result['output_dir']}")
        
        if result['successful'] > 0:
            click.echo("\n📝 成功解析的文件:")
            for res in result['results']:
                if res['success']:
                    output_file = res.get('output_path', res.get('pdf_path', 'N/A'))
                    click.echo(f"  ✓ {res['input_path']} → {output_file}")
        
        if result['failed'] > 0:
            click.echo("\n❌ 失败的文件:")
            for res in result['results']:
                if not res['success']:
                    click.echo(f"  ✗ {res['input_path']}: {res.get('error', '未知错误')}")
                    
    except Exception as e:
        click.echo(f"批量解析时出错: {str(e)}")

@match.command()
@click.argument('questions_file')
@click.option('--answers-file', help='答案文件路径（可选，如果不提供则从试题文件中提取答案）')
@click.option('--questions-type', default='pdf', help='试题文件类型')
@click.option('--answers-type', default='pdf', help='答案文件类型')
async def qa(questions_file, answers_file, questions_type, answers_type):
    """匹配试题和答案"""
    try:
        if not os.path.exists(questions_file):
            click.echo(f"错误: 试题文件不存在: {questions_file}")
            return
        
        click.echo(f"处理试题文件: {questions_file}")
        
        # 读取试题文件
        with open(questions_file, 'rb') as f:
            questions_content = f.read()
        
        # 读取答案文件（如果提供）
        answers_content = None
        if answers_file:
            if not os.path.exists(answers_file):
                click.echo(f"错误: 答案文件不存在: {answers_file}")
                return
            with open(answers_file, 'rb') as f:
                answers_content = f.read()
            click.echo(f"处理答案文件: {answers_file}")
        else:
            click.echo("从试题文件中提取答案...")
        
        # 初始化匹配服务
        matcher = QuestionAnswerMatcher()
        
        # 匹配试题和答案
        result = await matcher.match_questions_answers(
            questions_content=questions_content,
            answers_content=answers_content,
            questions_file_type=questions_type,
            answers_file_type=answers_type
        )
        
        if result['success']:
            click.echo("\n=== 试题-答案匹配结果 ===")
            click.echo(f"文件类型: {result.get('file_type', 'unknown')}")
            click.echo(f"试题数量: {result.get('total_questions', 0)}")
            click.echo(f"答案数量: {result.get('total_answers', 0)}")
            click.echo(f"匹配对数: {len(result.get('matched_pairs', []))}")
            
            # 显示匹配详情
            matched_pairs = result.get('matched_pairs', [])
            if matched_pairs:
                click.echo("\n📝 匹配详情 (基于题目标号):")
                for i, pair in enumerate(matched_pairs, 1):
                    question = pair['question']
                    answer = pair['answer']
                    
                    q_num = question.get('question_number', '无序号')
                    a_num = answer.get('answer_number', '无序号')
                    
                    click.echo(f"\n第 {i} 对 (题号 {q_num} → 答案 {a_num}):")
                    click.echo(f"  匹配方法: {pair.get('match_method', 'unknown')}")
                    click.echo(f"  置信度: {pair.get('confidence', 0):.2f}")
                    click.echo(f"  试题: {question['cleaned_text'][:80]}...")
                    click.echo(f"  答案: {answer['cleaned_text'][:50]}...")
            
            # 显示验证结果
            validation = result.get('validation', {})
            click.echo("\n🔍 验证结果:")
            click.echo(f"  匹配质量: {validation.get('match_quality', '未知')}")
            click.echo(f"  精确序号匹配: {validation.get('exact_number_matches', 0)}/{validation.get('total_pairs', 0)}")
            
            if validation.get('method_distribution'):
                click.echo("  匹配方法分布:")
                for method, count in validation['method_distribution'].items():
                    click.echo(f"    - {method}: {count}")
            
            if validation.get('issues'):
                click.echo("  问题:")
                for issue in validation['issues']:
                    click.echo(f"    - {issue}")
            
            if validation.get('suggestions'):
                click.echo("  建议:")
                for suggestion in validation['suggestions']:
                    click.echo(f"    - {suggestion}")
            
            # 生成匹配报告
            report = await matcher.get_matching_report(matched_pairs)
            click.echo(f"\n📊 匹配报告:\n{report}")
            
        else:
            click.echo(f"匹配失败: {result.get('error', '未知错误')}")
            
    except Exception as e:
        click.echo(f"试题-答案匹配时出错: {str(e)}")

@cli.command()
@click.option('--host', default='0.0.0.0', help='服务器主机')
@click.option('--port', default=8000, help='服务器端口')
@click.option('--reload', is_flag=True, help='启用热重载')
def serve(host, port, reload):
    """启动开发服务器"""
    import uvicorn
    click.echo(f"启动开发服务器: http://{host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=reload)

def main():
    """主函数"""
    cli()

if __name__ == "__main__":
    main()