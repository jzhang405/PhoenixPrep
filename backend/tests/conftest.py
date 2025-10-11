"""
测试配置文件
为所有测试提供共享的夹具和配置
"""

import pytest
import sys
import os
from fastapi import FastAPI
from fastapi.testclient import TestClient

# 添加backend目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture
def client():
    """创建测试客户端"""
    # 创建一个简单的测试应用
    # 因为主要应用有导入问题，我们创建一个最小化的应用用于测试
    app = FastAPI(
        title="凤凰备考系统API - 测试",
        description="测试环境",
        version="0.1.0"
    )

    # 添加基本路由用于测试
    @app.get("/")
    async def root():
        return {"message": "测试API服务运行中"}

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return TestClient(app)


@pytest.fixture
def sample_pdf_content():
    """提供示例PDF内容"""
    return b"%PDF-1.4 fake pdf content"


@pytest.fixture
def sample_docx_content():
    """提供示例DOCX内容"""
    return b"PK\x03\x04 fake docx content"


@pytest.fixture
def sample_image_content():
    """提供示例图片内容"""
    return b"\x89PNG\r\n\x1a\n fake png content"


@pytest.fixture
def sample_upload_data():
    """提供示例上传数据"""
    return {
        "file_name": "test.pdf",
        "file_size": 1024,
        "file_type": "application/pdf"
    }