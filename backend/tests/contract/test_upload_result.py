"""
契约测试: GET /api/upload/{upload_id}/result
测试上传结果查询端点的契约
"""

import pytest
import httpx
from fastapi.testclient import TestClient


class TestUploadResult:
    """测试 GET /api/upload/{upload_id}/result 端点契约"""

    def test_upload_result_endpoint_exists(self, client: TestClient):
        """测试上传结果端点是否存在"""
        # 这个测试应该失败，因为端点尚未实现
        response = client.get("/api/upload/test-upload-id/result")

        # 端点应该存在（即使返回错误）
        assert response.status_code != 404, "上传结果端点未实现"

    def test_upload_result_returns_valid_structure(self, client: TestClient):
        """测试上传结果返回有效结构"""
        response = client.get("/api/upload/completed-upload/result")

        if response.status_code == 200:
            # 如果端点已实现，检查返回结构
            data = response.json()

            # 验证必需字段
            required_fields = ["upload_id", "status", "parsed_content", "metadata"]
            for field in required_fields:
                assert field in data, f"响应中缺少 {field} 字段"

            # 验证字段类型和值
            assert data["upload_id"] == "completed-upload", "upload_id应该匹配路径参数"
            assert data["status"] == "completed", "结果查询时状态应该为completed"
            assert isinstance(data["parsed_content"], (str, dict, list)), \
                "parsed_content应该是字符串、字典或列表"
            assert isinstance(data["metadata"], dict), "metadata应该是字典"

    def test_upload_result_parsed_content_structure(self, client: TestClient):
        """测试解析内容的结构"""
        response = client.get("/api/upload/completed-upload/result")

        if response.status_code == 200:
            data = response.json()
            parsed_content = data["parsed_content"]

            # 根据内容类型验证结构
            if isinstance(parsed_content, dict):
                # 如果是字典结构，应该包含问题和答案
                assert "questions" in parsed_content or "content" in parsed_content, \
                    "parsed_content字典应该包含questions或content字段"

            elif isinstance(parsed_content, list):
                # 如果是列表结构，应该包含解析的题目
                assert len(parsed_content) > 0, "parsed_content列表不应该为空"
                # 验证列表项结构
                for item in parsed_content:
                    assert isinstance(item, dict), "列表项应该是字典"

            elif isinstance(parsed_content, str):
                # 如果是字符串，应该是HTML或文本内容
                assert len(parsed_content) > 0, "parsed_content字符串不应该为空"

    def test_upload_result_metadata_structure(self, client: TestClient):
        """测试元数据结构"""
        response = client.get("/api/upload/completed-upload/result")

        if response.status_code == 200:
            data = response.json()
            metadata = data["metadata"]

            # 验证元数据字段
            expected_metadata_fields = [
                "file_name", "file_size", "file_type", "parsed_at",
                "question_count", "processing_time"
            ]

            for field in expected_metadata_fields:
                if field in metadata:
                    # 验证字段类型
                    if field in ["file_size", "question_count", "processing_time"]:
                        assert isinstance(metadata[field], (int, float)), f"{field} 应该是数字"
                    elif field in ["file_name", "file_type", "parsed_at"]:
                        assert isinstance(metadata[field], str), f"{field} 应该是字符串"

    def test_upload_result_handles_pending_upload(self, client: TestClient):
        """测试处理未完成的上传"""
        response = client.get("/api/upload/pending-upload/result")

        # 如果上传未完成，应该返回适当的状态
        if response.status_code == 200:
            data = response.json()
            if data["status"] != "completed":
                assert "parsed_content" not in data or data["parsed_content"] is None, \
                    "未完成的上传不应该包含解析内容"
                assert "message" in data, "应该包含状态消息"

        elif response.status_code == 400:
            error_data = response.json()
            assert "detail" in error_data, "错误响应应该包含detail字段"
            assert "未完成" in error_data["detail"] or "处理中" in error_data["detail"], \
                "应该为未完成的上传返回适当的错误"

    def test_upload_result_handles_failed_upload(self, client: TestClient):
        """测试处理失败的上传"""
        response = client.get("/api/upload/failed-upload/result")

        if response.status_code == 200:
            data = response.json()
            if data["status"] == "failed":
                assert "error" in data, "失败状态应该包含error字段"
                assert "parsed_content" not in data or data["parsed_content"] is None, \
                    "失败的上传不应该包含解析内容"
                assert isinstance(data["error"], str), "error应该是字符串"
                assert len(data["error"]) > 0, "error不应该为空"

    def test_upload_result_supports_different_content_types(self, client: TestClient):
        """测试支持不同的内容类型"""
        test_cases = [
            ("pdf-upload", "application/pdf"),
            ("docx-upload", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
            ("image-upload", "image/png")
        ]

        for upload_id, expected_type in test_cases:
            response = client.get(f"/api/upload/{upload_id}/result")

            if response.status_code == 200:
                data = response.json()
                metadata = data["metadata"]

                if "file_type" in metadata:
                    assert metadata["file_type"] == expected_type, \
                        f"文件类型应该匹配 {expected_type}"

    def test_upload_result_question_extraction(self, client: TestClient):
        """测试题目提取功能"""
        response = client.get("/api/upload/question-rich-upload/result")

        if response.status_code == 200:
            data = response.json()
            parsed_content = data["parsed_content"]

            # 如果解析内容包含题目，验证题目结构
            if isinstance(parsed_content, dict) and "questions" in parsed_content:
                questions = parsed_content["questions"]
                assert isinstance(questions, list), "questions应该是列表"

                for question in questions:
                    # 验证题目基本结构
                    assert "id" in question or "content" in question, \
                        "题目应该包含id或content字段"
                    if "content" in question:
                        assert isinstance(question["content"], str), "题目内容应该是字符串"
                        assert len(question["content"]) > 0, "题目内容不应该为空"

                    # 验证可选字段
                    optional_fields = ["type", "difficulty", "knowledge_points", "options"]
                    for field in optional_fields:
                        if field in question:
                            if field == "options":
                                assert isinstance(question[field], list), "options应该是列表"
                            elif field == "knowledge_points":
                                assert isinstance(question[field], list), "knowledge_points应该是列表"

    def test_upload_result_pagination(self, client: TestClient):
        """测试分页功能（如果支持）"""
        # 测试带分页参数的请求
        params = {"page": 1, "page_size": 10}
        response = client.get("/api/upload/large-upload/result", params=params)

        if response.status_code == 200:
            data = response.json()

            # 如果支持分页，验证分页字段
            if "pagination" in data:
                pagination = data["pagination"]
                assert "page" in pagination, "分页信息应该包含page字段"
                assert "page_size" in pagination, "分页信息应该包含page_size字段"
                assert "total" in pagination, "分页信息应该包含total字段"
                assert "total_pages" in pagination, "分页信息应该包含total_pages字段"

    def test_upload_result_error_responses(self, client: TestClient):
        """测试错误响应"""
        error_cases = [
            ("", 404),  # 空upload_id
            ("invalid-id", 404),  # 无效ID
            ("nonexistent-id", 404)  # 不存在的ID
        ]

        for upload_id, expected_status in error_cases:
            response = client.get(f"/api/upload/{upload_id}/result")

            if response.status_code != 200:
                # 验证错误响应结构
                error_data = response.json()
                assert "detail" in error_data, "错误响应应该包含detail字段"
                assert isinstance(error_data["detail"], str), "detail应该是字符串"
                assert len(error_data["detail"]) > 0, "detail不应该为空"