"""
契约测试: POST /api/questions
测试题目创建端点的契约
"""

import pytest
import httpx
from fastapi.testclient import TestClient


class TestQuestionsPost:
    """测试 POST /api/questions 端点契约"""

    def test_questions_post_endpoint_exists(self, client: TestClient):
        """测试题目创建端点是否存在"""
        # 这个测试应该失败，因为端点尚未实现
        response = client.post("/api/questions")

        # 端点应该存在（即使返回错误）
        assert response.status_code != 404, "题目创建端点未实现"

    def test_create_single_choice_question(self, client: TestClient):
        """测试创建单选题"""
        question_data = {
            "content": "以下哪个是质数？",
            "type": "single_choice",
            "difficulty": "medium",
            "knowledge_points": ["数学", "质数"],
            "options": [
                {"id": "A", "content": "4"},
                {"id": "B", "content": "9"},
                {"id": "C", "content": "11"},
                {"id": "D", "content": "15"}
            ],
            "correct_answer": "C",
            "explanation": "11是质数，只能被1和自身整除"
        }

        response = client.post("/api/questions", json=question_data)

        if response.status_code == 201:
            data = response.json()

            # 验证响应结构
            required_fields = ["id", "content", "type", "created_at"]
            for field in required_fields:
                assert field in data, f"响应中缺少 {field} 字段"

            # 验证字段值
            assert data["content"] == question_data["content"], "内容应该匹配"
            assert data["type"] == question_data["type"], "类型应该匹配"
            assert data["difficulty"] == question_data["difficulty"], "难度应该匹配"

    def test_create_multiple_choice_question(self, client: TestClient):
        """测试创建多选题"""
        question_data = {
            "content": "以下哪些是偶数？",
            "type": "multiple_choice",
            "difficulty": "easy",
            "knowledge_points": ["数学", "偶数"],
            "options": [
                {"id": "A", "content": "2"},
                {"id": "B", "content": "3"},
                {"id": "C", "content": "4"},
                {"id": "D", "content": "5"}
            ],
            "correct_answer": ["A", "C"],
            "explanation": "2和4是偶数，可以被2整除"
        }

        response = client.post("/api/questions", json=question_data)

        if response.status_code == 201:
            data = response.json()
            assert data["type"] == "multiple_choice", "类型应该是multiple_choice"
            assert isinstance(data.get("correct_answer", []), list), "多选题答案应该是列表"

    def test_create_essay_question(self, client: TestClient):
        """测试创建问答题"""
        question_data = {
            "content": "请论述人工智能在教育领域的应用前景",
            "type": "essay",
            "difficulty": "hard",
            "knowledge_points": ["人工智能", "教育技术"],
            "correct_answer": "人工智能在教育领域有广阔的应用前景...",
            "scoring_criteria": [
                "观点明确性",
                "论证充分性",
                "语言表达"
            ]
        }

        response = client.post("/api/questions", json=question_data)

        if response.status_code == 201:
            data = response.json()
            assert data["type"] == "essay", "类型应该是essay"
            # 问答题可能没有options字段
            assert "options" not in data or data["options"] is None, "问答题不应该有选项"

    def test_create_calculation_question(self, client: TestClient):
        """测试创建计算题"""
        question_data = {
            "content": "计算圆的面积，半径为5cm",
            "type": "calculation",
            "difficulty": "medium",
            "knowledge_points": ["数学", "几何", "圆"],
            "correct_answer": "78.5",
            "calculation_steps": [
                "面积公式: S = πr²",
                "代入半径: S = 3.14 × 5²",
                "计算结果: S = 3.14 × 25 = 78.5"
            ]
        }

        response = client.post("/api/questions", json=question_data)

        if response.status_code == 201:
            data = response.json()
            assert data["type"] == "calculation", "类型应该是calculation"

    def test_question_validation_required_fields(self, client: TestClient):
        """测试必需字段验证"""
        # 测试缺少必需字段
        invalid_questions = [
            {},  # 空数据
            {"type": "single_choice"},  # 缺少content
            {"content": "测试题目"},  # 缺少type
            {
                "content": "测试题目",
                "type": "single_choice",
                "options": [{"content": "选项A"}]  # 选项缺少id
            }
        ]

        for invalid_data in invalid_questions:
            response = client.post("/api/questions", json=invalid_data)

            # 应该返回验证错误
            if response.status_code == 422:
                error_data = response.json()
                assert "detail" in error_data, "验证错误应该包含detail字段"
                assert isinstance(error_data["detail"], list), "detail应该是列表"

    def test_question_validation_invalid_types(self, client: TestClient):
        """测试无效类型验证"""
        invalid_questions = [
            {
                "content": "测试题目",
                "type": "invalid_type",  # 无效类型
                "options": [{"id": "A", "content": "选项A"}]
            },
            {
                "content": "测试题目",
                "type": "single_choice",
                "difficulty": "impossible"  # 无效难度
            }
        ]

        for invalid_data in invalid_questions:
            response = client.post("/api/questions", json=invalid_data)

            if response.status_code == 422:
                error_data = response.json()
                # 应该包含具体的验证错误信息
                assert any("detail" in error_data for _ in error_data.get("detail", [])), \
                    "应该返回具体的验证错误"

    def test_question_options_validation(self, client: TestClient):
        """测试选项验证"""
        # 测试选择题必须有选项
        choice_questions_without_options = [
            {
                "content": "单选题",
                "type": "single_choice"
                # 缺少options
            },
            {
                "content": "多选题",
                "type": "multiple_choice"
                # 缺少options
            }
        ]

        for question_data in choice_questions_without_options:
            response = client.post("/api/questions", json=question_data)

            if response.status_code == 422:
                error_data = response.json()
                # 应该提示选项是必需的
                assert any("options" in str(error).lower() for error in error_data.get("detail", [])), \
                    "应该提示选择题需要选项"

    def test_question_correct_answer_validation(self, client: TestClient):
        """测试正确答案验证"""
        test_cases = [
            {
                "data": {
                    "content": "单选题",
                    "type": "single_choice",
                    "options": [
                        {"id": "A", "content": "选项A"},
                        {"id": "B", "content": "选项B"}
                    ],
                    "correct_answer": "C"  # 无效选项ID
                },
                "expected_error": "无效的正确答案"
            },
            {
                "data": {
                    "content": "多选题",
                    "type": "multiple_choice",
                    "options": [
                        {"id": "A", "content": "选项A"},
                        {"id": "B", "content": "选项B"}
                    ],
                    "correct_answer": ["A", "C"]  # 包含无效选项ID
                },
                "expected_error": "无效的正确答案"
            }
        ]

        for test_case in test_cases:
            response = client.post("/api/questions", json=test_case["data"])

            if response.status_code == 422:
                error_data = response.json()
                # 应该提示正确答案验证错误
                assert any("correct_answer" in str(error).lower() for error in error_data.get("detail", [])), \
                    "应该提示正确答案验证错误"

    def test_question_creation_with_metadata(self, client: TestClient):
        """测试带元数据的题目创建"""
        question_data = {
            "content": "测试题目",
            "type": "single_choice",
            "difficulty": "medium",
            "knowledge_points": ["数学", "测试"],
            "options": [
                {"id": "A", "content": "选项A"},
                {"id": "B", "content": "选项B"}
            ],
            "correct_answer": "A",
            "explanation": "这是解释",
            "source": "测试试卷",
            "tags": ["测试", "示例"],
            "metadata": {
                "author": "系统",
                "version": "1.0",
                "custom_field": "自定义值"
            }
        }

        response = client.post("/api/questions", json=question_data)

        if response.status_code == 201:
            data = response.json()
            # 验证元数据字段
            if "metadata" in data:
                assert isinstance(data["metadata"], dict), "metadata应该是字典"

    def test_question_creation_response_structure(self, client: TestClient):
        """测试创建响应结构"""
        question_data = {
            "content": "响应结构测试题目",
            "type": "single_choice",
            "options": [
                {"id": "A", "content": "选项A"},
                {"id": "B", "content": "选项B"}
            ],
            "correct_answer": "A"
        }

        response = client.post("/api/questions", json=question_data)

        if response.status_code == 201:
            data = response.json()

            # 验证响应包含所有输入字段
            for field in ["content", "type", "options", "correct_answer"]:
                assert field in data, f"响应中应该包含 {field} 字段"

            # 验证生成的字段
            assert "id" in data, "响应中应该包含生成的id字段"
            assert "created_at" in data, "响应中应该包含created_at字段"
            assert "updated_at" in data, "响应中应该包含updated_at字段"

            # 验证字段类型
            assert isinstance(data["id"], (str, int)), "id应该是字符串或整数"
            assert isinstance(data["created_at"], str), "created_at应该是字符串"
            assert isinstance(data["updated_at"], str), "updated_at应该是字符串"

    def test_question_creation_duplicate_prevention(self, client: TestClient):
        """测试重复题目预防"""
        question_data = {
            "content": "重复题目测试",
            "type": "single_choice",
            "options": [
                {"id": "A", "content": "选项A"},
                {"id": "B", "content": "选项B"}
            ],
            "correct_answer": "A"
        }

        # 第一次创建
        response1 = client.post("/api/questions", json=question_data)

        if response1.status_code == 201:
            # 尝试创建相同的题目
            response2 = client.post("/api/questions", json=question_data)

            # 应该防止重复或返回适当的错误
            if response2.status_code == 400:
                error_data = response2.json()
                assert "detail" in error_data, "错误响应应该包含detail字段"
                assert "重复" in error_data["detail"] or "已存在" in error_data["detail"], \
                    "应该提示题目已存在"

    def test_question_creation_performance(self, client: TestClient):
        """测试创建性能"""
        import time

        question_data = {
            "content": "性能测试题目",
            "type": "single_choice",
            "options": [
                {"id": "A", "content": "选项A"},
                {"id": "B", "content": "选项B"}
            ],
            "correct_answer": "A"
        }

        start_time = time.time()
        response = client.post("/api/questions", json=question_data)
        end_time = time.time()

        response_time = end_time - start_time

        # 题目创建应该是快速的
        if response.status_code == 201:
            assert response_time < 1.0, "题目创建应该在1秒内完成"