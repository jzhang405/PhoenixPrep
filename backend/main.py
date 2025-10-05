from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .src.api.endpoints import upload, questions, analysis, dashboard, mistake, question_answer_matching

app = FastAPI(
    title="凤凰备考系统API",
    description="面向高考复读生的个性化学习系统",
    version="0.1.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(upload.router, prefix="/api", tags=["文件上传"])
app.include_router(questions.router, prefix="/api", tags=["题目管理"])
app.include_router(analysis.router, prefix="/api", tags=["学习分析"])
app.include_router(dashboard.router, prefix="/api", tags=["仪表板"])
app.include_router(mistake.router, prefix="/api", tags=["错题分析"])
app.include_router(question_answer_matching.router, prefix="/api", tags=["试题-答案匹配"])

@app.get("/")
async def root():
    return {"message": "凤凰备考系统API服务运行中"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)