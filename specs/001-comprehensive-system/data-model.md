# 数据模型文档：凤凰备考综合学习系统

**功能分支**: `001-comprehensive-system`  
**创建日期**: 2025-10-04  
**输入**: 功能规格中的关键实体和需求

## 实体定义

### 用户实体 (User)
**描述**: 系统用户，包括学生、教师和内容管理员

**字段**:
- `user_id`: UUID, 主键
- `username`: String(50), 唯一, 用户名
- `email`: String(100), 唯一, 邮箱
- `password_hash`: String(255), 密码哈希
- `role`: Enum('student', 'teacher', 'admin'), 用户角色
- `real_name`: String(50), 真实姓名
- `school`: String(100), 学校
- `grade`: String(20), 年级
- `created_at`: DateTime, 创建时间
- `updated_at`: DateTime, 更新时间

**验证规则**:
- 用户名: 3-50字符，字母数字下划线
- 邮箱: 有效邮箱格式
- 密码: 最少8字符，包含字母和数字

### 知识点实体 (KnowledgePoint)
**描述**: 课程知识点，用于题目分类和能力评估

**字段**:
- `point_id`: UUID, 主键
- `name`: String(100), 知识点名称
- `subject`: Enum('math', 'chinese', 'english', 'physics', 'chemistry', 'biology'), 学科
- `difficulty_level`: Integer(1-5), 难度等级
- `weight`: Float, 高考权重 (0.0-1.0)
- `parent_id`: UUID, 外键, 父知识点
- `description`: Text, 知识点描述
- `created_at`: DateTime, 创建时间

**验证规则**:
- 权重总和不超过1.0
- 难度等级在1-5范围内

### 问题资源实体 (QuestionResource)
**描述**: 单个测试题目，包含内容和元数据

**字段**:
- `question_id`: UUID, 主键
- `content`: Text, 题目内容
- `question_type`: Enum('single_choice', 'multiple_choice', 'fill_blank', 'essay'), 题型
- `difficulty`: Integer(1-5), 难度
- `subject`: String(50), 学科
- `knowledge_points`: JSON, 关联知识点列表
- `media_attachments`: JSON, 媒体附件 (图片、公式等)
- `answer`: Text, 标准答案
- `explanation`: Text, 解析
- `source`: String(200), 来源
- `year`: Integer, 年份
- `created_by`: UUID, 外键, 创建者
- `created_at`: DateTime, 创建时间

**验证规则**:
- 内容不能为空
- 至少关联一个知识点
- 难度在1-5范围内

### 试卷实体 (TestPaper)
**描述**: 定制的问题集合

**字段**:
- `paper_id`: UUID, 主键
- `title`: String(200), 试卷标题
- `description`: Text, 试卷描述
- `subject`: String(50), 学科
- `total_score`: Integer, 总分
- `time_limit`: Integer, 时间限制(分钟)
- `questions`: JSON, 题目列表及分值
- `criteria`: JSON, 生成标准 (知识点、难度等)
- `created_by`: UUID, 外键, 创建者
- `created_at`: DateTime, 创建时间

**验证规则**:
- 总分必须大于0
- 时间限制必须大于0

### 学生档案实体 (StudentProfile)
**描述**: 学生个人学习档案

**字段**:
- `profile_id`: UUID, 主键
- `user_id`: UUID, 外键, 关联用户
- `target_score`: Integer, 目标分数
- `study_plan`: JSON, 学习计划
- `weak_areas`: JSON, 薄弱知识点
- `learning_style`: Enum('visual', 'auditory', 'kinesthetic'), 学习风格
- `created_at`: DateTime, 创建时间
- `updated_at`: DateTime, 更新时间

### 答题记录实体 (AnswerRecord)
**描述**: 学生答题记录

**字段**:
- `record_id`: UUID, 主键
- `user_id`: UUID, 外键, 学生
- `question_id`: UUID, 外键, 题目
- `paper_id`: UUID, 外键, 试卷
- `user_answer`: Text, 学生答案
- `is_correct`: Boolean, 是否正确
- `time_spent`: Integer, 用时(秒)
- `confidence_level`: Integer(1-5), 自信程度
- `answered_at`: DateTime, 答题时间

### 表现分析实体 (PerformanceAnalysis)
**描述**: 学生表现分析结果

**字段**:
- `analysis_id`: UUID, 主键
- `user_id`: UUID, 外键, 学生
- `knowledge_point_id`: UUID, 外键, 知识点
- `proficiency_level`: Float, 掌握程度 (0.0-1.0)
- `accuracy_rate`: Float, 正确率
- `average_time`: Float, 平均用时
- `weak_indicator`: Boolean, 是否薄弱点
- `recommendation_priority`: Integer(1-5), 推荐优先级
- `analyzed_at`: DateTime, 分析时间

### 文件上传实体 (FileUpload)
**描述**: 文件上传记录

**字段**:
- `upload_id`: UUID, 主键
- `user_id`: UUID, 外键, 上传者
- `filename`: String(255), 文件名
- `file_type`: String(50), 文件类型
- `file_size`: Integer, 文件大小
- `status`: Enum('uploading', 'parsing', 'completed', 'failed'), 状态
- `parsed_content`: JSON, 解析内容
- `error_message`: Text, 错误信息
- `uploaded_at`: DateTime, 上传时间
- `completed_at`: DateTime, 完成时间

## 关系定义

### 一对多关系
- User → QuestionResource (created_by)
- User → TestPaper (created_by) 
- User → StudentProfile (user_id)
- User → AnswerRecord (user_id)
- User → PerformanceAnalysis (user_id)
- User → FileUpload (user_id)
- KnowledgePoint → PerformanceAnalysis (knowledge_point_id)
- QuestionResource → AnswerRecord (question_id)
- TestPaper → AnswerRecord (paper_id)

### 多对多关系
- QuestionResource ↔ KnowledgePoint (通过knowledge_points字段)

## 状态转换

### 文件上传状态
```
uploading → parsing → completed
uploading → parsing → failed
```

### 学生掌握程度状态
```
weak (proficiency < 0.6) → improving (0.6-0.8) → mastered (>0.8)
```

## 索引策略

### 主要索引
- User: username, email
- QuestionResource: subject, difficulty, year
- KnowledgePoint: subject, difficulty_level
- AnswerRecord: user_id, answered_at
- PerformanceAnalysis: user_id, knowledge_point_id

### 复合索引
- QuestionResource: (subject, difficulty, year)
- AnswerRecord: (user_id, question_id, answered_at)
- PerformanceAnalysis: (user_id, weak_indicator, analyzed_at)

## 数据验证规则

### 业务规则
1. 学生只能查看自己的答题记录和分析结果
2. 教师可以查看所教学生的数据
3. 管理员可以管理所有内容
4. 知识点权重总和不能超过1.0
5. 题目难度必须在1-5范围内
6. 答题时间必须大于0

### 完整性约束
- 用户删除时级联删除相关记录
- 知识点删除时更新关联题目的knowledge_points字段
- 题目删除时标记关联答题记录为已删除

## 数据迁移考虑

### 版本1.0
- 初始表结构创建
- 基础数据导入 (知识点、示例题目)

### 未来扩展
- 支持更多学科
- 添加视频讲解功能
- 集成更多学习资源