"""
契约测试: GET /api/questions
测试题目查询端点的契约
"""

import pytest
import httpx
from fastapi.testclient import TestClient


class TestQuestionsGet:
    """测试 GET /api/questions 端点契约"""

    def test_questions_endpoint_exists(self, client: TestClient):
        """测试题目查询端点是否存在"""
        # 这个测试应该失败，因为端点尚未实现
        response = client.get("/api/questions")

        # 端点应该存在（即使返回错误）
        assert response.status_code != 404, "题目查询端点未实现"

    def test_questions_returns_list_structure(self, client: TestClient):
        """测试题目查询返回列表结构"""
        response = client.get("/api/questions")

        if response.status_code == 200:
            # 如果端点已实现，检查返回结构
            data = response.json()

            # 验证响应结构
            assert isinstance(data, (list, dict)), "响应应该是列表或字典"

            if isinstance(data, dict):
                # 如果是字典结构，应该包含questions字段
                assert "questions" in data, "响应字典应该包含questions字段"
                questions = data["questions"]
                assert isinstance(questions, list), "questions应该是列表"
            else:
                # 如果是列表结构，直接使用
                questions = data

            # 验证题目结构
            for question in questions:
                self._validate_question_structure(question)

    def _validate_question_structure(self, question: dict):
        """验证题目结构"""
        # 必需字段
        required_fields = ["id", "content", "type"]
        for field in required_fields:
            assert field in question, f"题目中缺少 {field} 字段"

        # 验证字段类型
        assert isinstance(question["id"], (str, int)), "id应该是字符串或整数"
        assert isinstance(question["content"], str), "content应该是字符串"
        assert len(question["content"]) > 0, "content不应该为空"
        assert question["type"] in ["single_choice", "multiple_choice", "essay", "calculation"], \
            "type应该是有效的题目类型"

        # 验证可选字段
        optional_fields = [
            "difficulty", "knowledge_points", "options", "correct_answer",
            "explanation", "source", "created_at", "updated_at"
        ]

        for field in optional_fields:
            if field in question:
                if field == "difficulty":
                    assert question[field] in ["easy", "medium", "hard"], \
                        "difficulty应该是easy、medium或hard"
                elif field == "knowledge_points":
                    assert isinstance(question[field], list), "knowledge_points应该是列表"
                elif field == "options":
                    assert isinstance(question[field], list), "options应该是列表"
                    for option in question[field]:
                        assert isinstance(option, dict), "选项应该是字典"
                        assert "id" in option and "content" in option, "选项应该包含id和content"

    def test_questions_filtering(self, client: TestClient):
        """测试题目过滤功能"""
        # 测试各种过滤参数
        filter_params = [
            {"type": "single_choice"},
            {"difficulty": "medium"},
            {"knowledge_point": "数学"},
            {"type": "multiple_choice", "difficulty": "hard"}
        ]

        for params in filter_params:
            response = client.get("/api/questions", params=params)

            if response.status_code == 200:
                data = response.json()
                questions = data if isinstance(data, list) else data.get("questions", [])

                # 验证过滤结果
                for question in questions:
                    for key, value in params.items():
                        if key in question:
                            assert question[key] == value, \
                                f"题目应该匹配过滤条件 {key}={value}"

    def test_questions_pagination(self, client: TestClient):
        """测试题目分页功能"""
        pagination_params = [
            {"page": 1, "page_size": 10},
            {"page": 2, "page_size": 20},
            {"page": 1, "page_size": 5}
        ]

        for params in pagination_params:
            response = client.get("/api/questions", params=params)

            if response.status_code == 200:
                data = response.json()

                # 验证分页响应结构
                if isinstance(data, dict):
                    assert "questions" in data, "分页响应应该包含questions字段"
                    assert "pagination" in data, "分页响应应该包含pagination字段"

                    pagination = data["pagination"]
                    required_pagination_fields = ["page", "page_size", "total", "total_pages"]
                    for field in required_pagination_fields:
                        assert field in pagination, f"分页信息中缺少 {field} 字段"

                    # 验证分页值
                    assert pagination["page"] == params["page"], "页码应该匹配"
                    assert pagination["page_size"] == params["page_size"], "页面大小应该匹配"
                    assert pagination["total"] >= 0, "总数应该大于等于0"
                    assert pagination["total_pages"] >= 0, "总页数应该大于等于0"

    def test_questions_search(self, client: TestClient):
        """测试题目搜索功能"""
        search_queries = [
            {"q": "数学"},
            {"q": "函数"},
            {"q": "选择题"}
        ]

        for params in search_queries:
            response = client.get("/api/questions", params=params)

            if response.status_code == 200:
                data = response.json()
                questions = data if isinstance(data, list) else data.get("questions", [])

                # 验证搜索结果包含搜索词
                search_term = params["q"]
                found_match = False
                for question in questions:
                    if search_term in question.get("content", ""):
                        found_match = True
                        break
                    if "knowledge_points" in question:
                        for kp in question["knowledge_points"]:
                            if search_term in kp:
                                found_match = True
                                break

                # 如果有结果，至少应该有一个匹配
                if len(questions) > 0:
                    assert found_match, f"搜索结果应该包含搜索词 '{search_term}'"

    def test_questions_sorting(self, client: TestClient):
        """测试题目排序功能"""
        sort_params = [
            {"sort_by": "created_at", "sort_order": "desc"},
            {"sort_by": "difficulty", "sort_order": "asc"},
            {"sort_by": "id", "sort_order": "desc"}
        ]

        for params in sort_params:
            response = client.get("/api/questions", params=params)

            if response.status_code == 200:
                data = response.json()
                questions = data if isinstance(data, list) else data.get("questions", [])

                # 如果有多个题目，验证排序
                if len(questions) > 1:
                    sort_field = params["sort_by"]
                    sort_order = params["sort_order"]

                    # 检查排序字段是否存在于题目中
                    if all(sort_field in q for q in questions):
                        # 验证排序顺序
                        values = [q[sort_field] for q in questions]
                        if sort_order == "asc":
                            assert values == sorted(values), f"{sort_field} 应该按升序排列"
                        else:
                            assert values == sorted(values, reverse=True), \
                                f"{sort_field} 应该按降序排列"

    def test_questions_empty_results(self, client: TestClient):
        """测试空结果处理"""
        # 使用不存在的过滤条件
        params = {"type": "nonexistent_type", "difficulty": "impossible"}
        response = client.get("/api/questions", params=params)

        if response.status_code == 200:
            data = response.json()
            questions = data if isinstance(data, list) else data.get("questions", [])

            # 空结果应该是空列表
            assert questions == [], "没有匹配结果时应该返回空列表"

    def test_questions_error_handling(self, client: TestClient):
        """测试错误处理"""
        # 测试无效参数
        invalid_params = [
            {"page": 0},  # 无效页码
            {"page_size": 0},  # 无效页面大小
            {"page": -1},  # 负页码
        ]

        for params in invalid_params:
            response = client.get("/api/questions", params=params)

            if response.status_code == 400:
                error_data = response.json()
                assert "detail" in error_data, "错误响应应该包含detail字段"
                assert isinstance(error_data["detail"], str), "detail应该是字符串"

    def test_questions_response_performance(self, client: TestClient):
        """测试响应性能"""
        import time

        start_time = time.time()
        response = client.get("/api/questions")
        end_time = time.time()

        response_time = end_time - start_time

        # 题目查询应该是快速的
        if response.status_code == 200:
            assert response_time < 2.0, "题目查询应该在2秒内完成"