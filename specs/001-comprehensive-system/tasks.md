# 任务：凤凰备考综合学习系统

**输入**: 设计文档来自 `/specs/001-comprehensive-system/`
**前提条件**: plan.md (必需), research.md, data-model.md, contracts/

## 执行流程 (main)
```
1. 从功能目录加载plan.md
   → 如果未找到: 错误 "未找到实现计划"
   → 提取: 技术栈、库、结构
2. 加载可选设计文档:
   → data-model.md: 提取实体 → 模型任务
   → contracts/: 每个文件 → 契约测试任务
   → research.md: 提取决策 → 设置任务
3. 按类别生成任务:
   → 设置: 项目初始化、依赖项、代码检查
   → 测试: 契约测试、集成测试
   → 核心: 模型、服务、CLI命令
   → 集成: 数据库、中间件、日志
   → 优化: 单元测试、性能、文档
4. 应用任务规则:
   → 不同文件 = 标记 [P] 用于并行
   → 相同文件 = 顺序 (无 [P])
   → 测试在实现之前 (TDD)
5. 按顺序编号任务 (T001, T002...)
6. 生成依赖图
7. 创建并行执行示例
8. 验证任务完整性:
   → 所有契约都有测试吗？
   → 所有实体都有模型吗？
   → 所有端点都实现了吗？
9. 返回: 成功 (任务准备执行)
```

## 格式: `[ID] [P?] 描述`
- **[P]**: 可以并行运行 (不同文件，无依赖)
- 在描述中包含确切文件路径

## 路径约定
- **单个项目**: `src/`, `tests/` 在仓库根目录
- **Web应用**: `backend/src/`, `frontend/src/`
- **移动端**: `api/src/`, `ios/src/` 或 `android/src/`
- 下面显示的路径假设单个项目 - 根据plan.md结构调整

## 阶段3.1: 设置
- [ ] T001 根据实现计划创建项目结构
- [ ] T002 使用FastAPI依赖初始化Python项目
- [ ] T003 使用React + TypeScript依赖初始化前端项目
- [ ] T004 [P] 配置后端代码检查和格式化工具
- [ ] T005 [P] 配置前端代码检查和格式化工具

## 阶段3.2: 测试优先 (TDD) ⚠️ 必须在3.3之前完成
**关键: 这些测试必须在任何实现之前编写并且必须失败**
- [ ] T006 [P] 契约测试 POST /api/upload 在 tests/contract/test_upload_post.py
- [ ] T007 [P] 契约测试 GET /api/upload/{upload_id}/status 在 tests/contract/test_upload_status.py
- [ ] T008 [P] 契约测试 GET /api/upload/{upload_id}/result 在 tests/contract/test_upload_result.py
- [ ] T009 [P] 契约测试 GET /api/questions 在 tests/contract/test_questions_get.py
- [ ] T010 [P] 契约测试 POST /api/questions 在 tests/contract/test_questions_post.py
- [ ] T011 [P] 契约测试 GET /api/questions/{question_id} 在 tests/contract/test_questions_detail.py
- [ ] T012 [P] 契约测试 PUT /api/questions/{question_id} 在 tests/contract/test_questions_update.py
- [ ] T013 [P] 契约测试 POST /api/questions/batch 在 tests/contract/test_questions_batch.py
- [ ] T014 [P] 契约测试 GET /api/analysis/performance 在 tests/contract/test_analysis_performance.py
- [ ] T015 [P] 契约测试 POST /api/analysis/predict-score 在 tests/contract/test_analysis_predict.py
- [ ] T016 [P] 契约测试 GET /api/analysis/recommendations 在 tests/contract/test_analysis_recommendations.py
- [ ] T017 [P] 契约测试 GET /api/analysis/progress 在 tests/contract/test_analysis_progress.py
- [ ] T018 [P] 契约测试 POST /api/analysis/generate-test 在 tests/contract/test_analysis_generate_test.py
- [ ] T019 [P] 集成测试用户注册在 tests/integration/test_user_registration.py
- [ ] T020 [P] 集成测试试卷上传在 tests/integration/test_paper_upload.py
- [ ] T021 [P] 集成测试学生练习在 tests/integration/test_student_practice.py
- [ ] T022 [P] 集成测试学习分析在 tests/integration/test_learning_analysis.py

## 阶段3.3: 核心实现 (仅在测试失败后)
- [ ] T023 [P] 用户模型在 backend/src/models/user.py
- [ ] T024 [P] 知识点模型在 backend/src/models/knowledge_point.py
- [ ] T025 [P] 问题资源模型在 backend/src/models/question.py
- [ ] T026 [P] 试卷模型在 backend/src/models/test_paper.py
- [ ] T027 [P] 学生档案模型在 backend/src/models/student_profile.py
- [ ] T028 [P] 答题记录模型在 backend/src/models/answer_record.py
- [ ] T029 [P] 表现分析模型在 backend/src/models/performance.py
- [ ] T030 [P] 文件上传模型在 backend/src/models/file_upload.py
- [ ] T031 [P] 文件上传服务在 backend/src/services/file_upload.py
- [ ] T032 [P] PDF解析服务在 backend/src/services/pdf_parser.py
- [ ] T033 [P] Word文档解析服务在 backend/src/services/word_parser.py
- [ ] T034 [P] 图片解析服务在 backend/src/services/image_parser.py
- [ ] T035 [P] 文档解析管理器在 backend/src/services/document_parser.py
- [ ] T036 [P] 问题服务在 backend/src/services/question_service.py
- [ ] T037 [P] 分析服务在 backend/src/services/analysis_service.py
- [ ] T038 [P] 推荐服务在 backend/src/services/recommendation_service.py
- [ ] T039 [P] 错题分析服务在 backend/src/services/mistake_analysis.py
- [ ] T040 [P] 试题-答案匹配服务在 backend/src/services/question_answer_matcher.py
- [ ] T041 [P] 知识分析智能体在 backend/src/agents/knowledge_analyzer.py
- [ ] T042 [P] 问题生成智能体在 backend/src/agents/question_generator.py
- [ ] T043 [P] 表现预测智能体在 backend/src/agents/performance_predictor.py
- [ ] T044 [P] 文档解析智能体在 backend/src/agents/document_analyzer.py
- [ ] T045 [P] 智能体管理器在 backend/src/agents/agent_manager.py
- [ ] T046 [P] 数据库迁移配置在 backend/alembic/
- [ ] T047 [P] ChromaDB向量存储配置在 backend/src/storage/chroma_db.py
- [ ] T048 [P] Logics-Parsing集成配置在 backend/src/integrations/logics_parsing.py
- [ ] T049 [P] LangChain + CrewAI配置在 backend/src/integrations/langchain_crewai.py
- [ ] T050 POST /api/upload 端点
- [ ] T051 GET /api/upload/{upload_id}/status 端点
- [ ] T052 GET /api/upload/{upload_id}/result 端点
- [ ] T053 GET /api/questions 端点
- [ ] T054 POST /api/questions 端点
- [ ] T055 GET /api/questions/{question_id} 端点
- [ ] T056 PUT /api/questions/{question_id} 端点
- [ ] T057 POST /api/questions/batch 端点
- [ ] T058 GET /api/analysis/performance 端点
- [ ] T059 POST /api/analysis/predict-score 端点
- [ ] T060 GET /api/analysis/recommendations 端点
- [ ] T061 GET /api/analysis/progress 端点
- [ ] T062 POST /api/analysis/generate-test 端点
- [ ] T063 POST /api/mistake/analyze 端点
- [ ] T064 GET /api/mistake/history/{student_id} 端点
- [ ] T065 GET /api/mistake/statistics/{student_id} 端点
- [ ] T066 POST /api/question-answer/match 端点
- [ ] T067 GET /api/question-answer/match/{match_id} 端点
- [ ] T068 POST /api/question-answer/validate-match 端点
- [ ] T069 GET /api/question-answer/matching-methods 端点
- [ ] T070 输入验证
- [ ] T071 错误处理和日志
- [ ] T072 [P] 命令行接口在 backend/cli.py

## 阶段3.4: 前端实现
- [ ] T073 [P] 通用组件在 frontend/src/components/common/
- [ ] T074 [P] 上传组件在 frontend/src/components/upload/
- [ ] T075 [P] 仪表板组件在 frontend/src/components/dashboard/
- [ ] T076 [P] 分析组件在 frontend/src/components/analysis/
- [ ] T077 [P] 练习组件在 frontend/src/components/practice/
- [ ] T078 [P] 错题分析组件在 frontend/src/components/mistake/
- [ ] T079 [P] 上传页面在 frontend/src/pages/UploadPage.tsx
- [ ] T080 [P] 仪表板页面在 frontend/src/pages/DashboardPage.tsx
- [ ] T081 [P] 分析页面在 frontend/src/pages/AnalysisPage.tsx
- [ ] T082 [P] 练习页面在 frontend/src/pages/PracticePage.tsx
- [ ] T083 [P] 错题分析页面在 frontend/src/pages/MistakePage.tsx
- [ ] T084 [P] 设置页面在 frontend/src/pages/SettingsPage.tsx
- [ ] T085 [P] API服务在 frontend/src/services/api.ts
- [ ] T086 [P] 上传服务在 frontend/src/services/upload.ts
- [ ] T087 [P] 分析服务在 frontend/src/services/analysis.ts
- [ ] T088 [P] 错题分析服务在 frontend/src/services/mistake.ts
- [ ] T089 [P] 缓存服务在 frontend/src/services/cache.ts
- [ ] T090 [P] 类型定义在 frontend/src/types/
- [ ] T091 [P] 工具函数在 frontend/src/utils/

## 阶段3.5: 集成
- [ ] T092 连接服务到SQLite数据库
- [ ] T093 设置ChromaDB向量存储
- [ ] T094 认证中间件
- [ ] T095 请求/响应日志
- [ ] T096 CORS和安全头
- [ ] T097 文件存储配置

## 阶段3.6: 优化
- [ ] T098 [P] 验证单元测试在 tests/unit/test_validation.py
- [ ] T099 [P] 服务单元测试在 tests/unit/test_services.py
- [ ] T100 [P] 模型单元测试在 tests/unit/test_models.py
- [ ] T101 [P] 组件单元测试在 frontend/tests/unit/
- [ ] T102 性能测试 (<200ms)
- [ ] T103 [P] 更新 docs/api.md
- [ ] T104 移除重复代码
- [ ] T105 运行 manual-testing.md

## 依赖关系
- 测试 (T006-T022) 在实现 (T023-T072) 之前
- T023-T030 阻塞 T031-T049 (文档解析、Agent和集成配置)
- T031-T049 阻塞 T050-T072 (端点实现和CLI)
- T073-T091 阻塞 T092-T097 (集成)
- 实现在优化 (T098-T105) 之前

## 并行示例
```
# 同时启动 T006-T022:
任务: "契约测试 POST /api/upload 在 tests/contract/test_upload_post.py"
任务: "契约测试 GET /api/upload/{upload_id}/status 在 tests/contract/test_upload_status.py"
任务: "契约测试 GET /api/upload/{upload_id}/result 在 tests/contract/test_upload_result.py"
任务: "契约测试 GET /api/questions 在 tests/contract/test_questions_get.py"
任务: "契约测试 POST /api/questions 在 tests/contract/test_questions_post.py"
任务: "契约测试 GET /api/questions/{question_id} 在 tests/contract/test_questions_detail.py"
任务: "契约测试 PUT /api/questions/{question_id} 在 tests/contract/test_questions_update.py"
任务: "契约测试 POST /api/questions/batch 在 tests/contract/test_questions_batch.py"
任务: "契约测试 GET /api/analysis/performance 在 tests/contract/test_analysis_performance.py"
任务: "契约测试 POST /api/analysis/predict-score 在 tests/contract/test_analysis_predict.py"
任务: "契约测试 GET /api/analysis/recommendations 在 tests/contract/test_analysis_recommendations.py"
任务: "契约测试 GET /api/analysis/progress 在 tests/contract/test_analysis_progress.py"
任务: "契约测试 POST /api/analysis/generate-test 在 tests/contract/test_analysis_generate_test.py"
任务: "集成测试用户注册在 tests/integration/test_user_registration.py"
任务: "集成测试试卷上传在 tests/integration/test_paper_upload.py"
任务: "集成测试学生练习在 tests/integration/test_student_practice.py"
任务: "集成测试学习分析在 tests/integration/test_learning_analysis.py"

# 同时启动 T023-T030:
任务: "用户模型在 backend/src/models/user.py"
任务: "知识点模型在 backend/src/models/knowledge_point.py"
任务: "问题资源模型在 backend/src/models/question.py"
任务: "试卷模型在 backend/src/models/test_paper.py"
任务: "学生档案模型在 backend/src/models/student_profile.py"
任务: "答题记录模型在 backend/src/models/answer_record.py"
任务: "表现分析模型在 backend/src/models/performance.py"
任务: "文件上传模型在 backend/src/models/file_upload.py"

# 同时启动 T031-T047 (文档解析、Agent和集成配置):
任务: "文件上传服务在 backend/src/services/file_upload.py"
任务: "PDF解析服务在 backend/src/services/pdf_parser.py"
任务: "Word文档解析服务在 backend/src/services/word_parser.py"
任务: "图片解析服务在 backend/src/services/image_parser.py"
任务: "文档解析管理器在 backend/src/services/document_parser.py"
任务: "问题服务在 backend/src/services/question_service.py"
任务: "分析服务在 backend/src/services/analysis_service.py"
任务: "推荐服务在 backend/src/services/recommendation_service.py"
任务: "知识分析智能体在 backend/src/agents/knowledge_analyzer.py"
任务: "问题生成智能体在 backend/src/agents/question_generator.py"
任务: "表现预测智能体在 backend/src/agents/performance_predictor.py"
任务: "文档解析智能体在 backend/src/agents/document_analyzer.py"
任务: "智能体管理器在 backend/src/agents/agent_manager.py"
任务: "数据库迁移配置在 backend/alembic/"
任务: "ChromaDB向量存储配置在 backend/src/storage/chroma_db.py"
任务: "Logics-Parsing集成配置在 backend/src/integrations/logics_parsing.py"
任务: "LangChain + CrewAI配置在 backend/src/integrations/langchain_crewai.py"

# 同时启动 T068-T086:
任务: "通用组件在 frontend/src/components/common/"
任务: "上传组件在 frontend/src/components/upload/"
任务: "仪表板组件在 frontend/src/components/dashboard/"
任务: "分析组件在 frontend/src/components/analysis/"
任务: "练习组件在 frontend/src/components/practice/"
任务: "错题分析组件在 frontend/src/components/mistake/"
任务: "上传页面在 frontend/src/pages/UploadPage.tsx"
任务: "仪表板页面在 frontend/src/pages/DashboardPage.tsx"
任务: "分析页面在 frontend/src/pages/AnalysisPage.tsx"
任务: "练习页面在 frontend/src/pages/PracticePage.tsx"
任务: "错题分析页面在 frontend/src/pages/MistakePage.tsx"
任务: "设置页面在 frontend/src/pages/SettingsPage.tsx"
任务: "API服务在 frontend/src/services/api.ts"
任务: "上传服务在 frontend/src/services/upload.ts"
任务: "分析服务在 frontend/src/services/analysis.ts"
任务: "错题分析服务在 frontend/src/services/mistake.ts"
任务: "缓存服务在 frontend/src/services/cache.ts"
任务: "类型定义在 frontend/src/types/"
任务: "工具函数在 frontend/src/utils/"
```

## 备注
- [P] 任务 = 不同文件，无依赖
- 在实现之前验证测试失败
- 每个任务后提交
- 避免: 模糊任务，相同文件冲突

## 任务生成规则
*在main()执行期间应用*

1. **从契约**:
   - 每个契约文件 → 契约测试任务 [P]
   - 每个端点 → 实现任务
   
2. **从数据模型**:
   - 每个实体 → 模型创建任务 [P]
   - 关系 → 服务层任务
   
3. **从用户故事**:
   - 每个故事 → 集成测试 [P]
   - 快速入门场景 → 验证任务

4. **排序**:
   - 设置 → 测试 → 模型 → 服务 → 端点 → 优化
   - 依赖关系阻止并行执行

## 验证清单
*关卡: 在main()返回前检查*

- [ ] 所有契约都有相应的测试
- [ ] 所有实体都有模型任务
- [ ] 所有测试都在实现之前
- [ ] 并行任务真正独立
- [ ] 每个任务指定确切文件路径
- [ ] 没有任务修改与另一个[P]任务相同的文件

---

**任务生成完成**: 105个编号任务已创建，遵循TDD原则和依赖顺序。