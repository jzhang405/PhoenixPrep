"""
试题-答案匹配API端点
处理试题和答案文件的匹配，支持单个文件和分开文件
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, List
import uuid
import os
from ...services.question_answer_matcher import QuestionAnswerMatcher
from ...models.file_upload import FileUpload

router = APIRouter(prefix="/api/question-answer", tags=["试题-答案匹配"])

@router.post("/match")
async def match_questions_answers(
    question_file: Optional[UploadFile] = File(None),
    answer_file: Optional[UploadFile] = File(None),
    combined_file: Optional[UploadFile] = File(None),
    subject: str = Form(...),
    description: Optional[str] = Form(None)
):
    """
    匹配试题和答案
    
    支持两种模式：
    1. 分开文件：question_file + answer_file
    2. 单个文件：combined_file (包含试题和答案)
    """
    try:
        # 验证输入
        if combined_file and (question_file or answer_file):
            raise HTTPException(
                status_code=400,
                detail="不能同时提供combined_file和question_file/answer_file"
            )
        
        if not combined_file and not (question_file and answer_file):
            raise HTTPException(
                status_code=400,
                detail="必须提供combined_file或question_file+answer_file"
            )
        
        # 创建匹配器实例
        matcher = QuestionAnswerMatcher()
        
        # 处理文件
        if combined_file:
            # 单个文件模式
            combined_content = await combined_file.read()
            combined_filename = combined_file.filename
            
            result = matcher.match_questions_answers(
                combined_content=combined_content,
                combined_filename=combined_filename,
                subject=subject
            )
        else:
            # 分开文件模式
            question_content = await question_file.read()
            answer_content = await answer_file.read()
            
            result = matcher.match_questions_answers(
                question_content=question_content,
                answer_content=answer_content,
                question_filename=question_file.filename,
                answer_filename=answer_file.filename,
                subject=subject
            )
        
        return {
            "match_id": str(uuid.uuid4()),
            "status": "completed",
            "total_questions": result["total_questions"],
            "matched_count": result["matched_count"],
            "confidence_score": result["confidence_score"],
            "matching_methods": result["matching_methods"],
            "matched_pairs": result["matched_pairs"],
            "validation_report": result["validation_report"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"匹配失败: {str(e)}")

@router.get("/match/{match_id}")
async def get_match_result(match_id: str):
    """
    获取匹配结果
    """
    # 这里应该从数据库或缓存中获取结果
    # 目前返回示例数据
    return {
        "match_id": match_id,
        "status": "completed",
        "message": "匹配结果获取成功"
    }

@router.post("/validate-match")
async def validate_match_result(
    matched_pairs: List[dict],
    subject: str
):
    """
    验证匹配结果
    """
    try:
        matcher = QuestionAnswerMatcher()
        
        validation_result = matcher.validate_match_result(
            matched_pairs=matched_pairs,
            subject=subject
        )
        
        return validation_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"验证失败: {str(e)}")

@router.get("/matching-methods")
async def get_matching_methods():
    """
    获取支持的匹配方法
    """
    return {
        "methods": [
            {
                "name": "序号匹配",
                "description": "根据题目序号进行匹配",
                "confidence": "高"
            },
            {
                "name": "位置匹配", 
                "description": "根据题目在文档中的位置进行匹配",
                "confidence": "中"
            },
            {
                "name": "相似度匹配",
                "description": "根据题目内容相似度进行匹配",
                "confidence": "低"
            }
        ]
    }