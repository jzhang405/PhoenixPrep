"""
错题分析API端点
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import asyncio

from ...services.mistake_analysis import MistakeAnalysisService

router = APIRouter()
mistake_service = MistakeAnalysisService()

@router.post("/mistake/analyze")
async def analyze_mistake(
    image: UploadFile = File(..., description="错题图片"),
    student_id: str = Form(..., description="学生ID"),
    subject: Optional[str] = Form(None, description="科目")
):
    """
    分析错题图片
    
    - **image**: 错题图片文件 (支持jpg, png, jpeg格式)
    - **student_id**: 学生ID
    - **subject**: 科目 (可选)
    """
    try:
        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
        if image.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {image.content_type}，请上传jpg或png格式的图片"
            )
        
        # 读取图片内容
        image_content = await image.read()
        
        # 分析错题
        result = await mistake_service.analyze_mistake_image(
            image_content=image_content,
            student_id=student_id,
            subject=subject
        )
        
        if result['success']:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": {
                        "question_content": result.get('question_content', ''),
                        "knowledge_points": result.get('knowledge_points', []),
                        "mistake_analysis": result.get('mistake_analysis', {}),
                        "explanation": result.get('explanation', ''),
                        "recommendations": result.get('recommendations', []),
                        "confidence_score": result.get('confidence_score', 0.0)
                    }
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"错题分析失败: {result.get('error', '未知错误')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

@router.get("/mistake/history/{student_id}")
async def get_mistake_history(
    student_id: str,
    limit: int = 10
):
    """
    获取学生错题历史
    
    - **student_id**: 学生ID
    - **limit**: 返回记录数量限制 (默认10)
    """
    try:
        history = await mistake_service.get_mistake_history(student_id, limit)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "student_id": student_id,
                    "history": history,
                    "total_count": len(history)
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取错题历史失败: {str(e)}"
        )

@router.get("/mistake/statistics/{student_id}")
async def get_mistake_statistics(student_id: str):
    """
    获取学生错题统计
    
    - **student_id**: 学生ID
    """
    try:
        statistics = await mistake_service.get_mistake_statistics(student_id)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "student_id": student_id,
                    "statistics": statistics
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取错题统计失败: {str(e)}"
        )

@router.get("/mistake/health")
async def mistake_health_check():
    """错题分析服务健康检查"""
    try:
        # 简单的健康检查
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "service": "mistake_analysis",
                "status": "healthy"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"错题分析服务异常: {str(e)}"
        )