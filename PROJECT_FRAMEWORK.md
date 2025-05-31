# XianyuAutoAgent 项目框架文档

## 📋 文档目的
本文档记录XianyuAutoAgent（智能闲鱼客服机器人系统）的核心框架信息，使AI工具能够快速理解项目架构并生成相关代码。

## 🏗️ 项目架构概览

### 实际目录结构
```
XianyuAutoAgent/
├── main.py                    # 主程序入口 - WebSocket连接和消息处理
├── XianyuAgent.py            # AI回复机器人核心逻辑
├── XianyuApis.py             # 闲鱼API接口封装
├── context_manager.py        # 聊天上下文管理器
├── utils/                    # 工具函数目录
│   ├── __init__.py
│   └── xianyu_utils.py      # 闲鱼平台专用工具函数
├── prompts/                  # AI提示词模板目录
│   ├── classify_prompt.txt   # 意图分类提示词
│   ├── default_prompt.txt    # 默认回复提示词
│   ├── price_prompt.txt      # 价格专家提示词
│   ├── tech_prompt.txt       # 技术专家提示词
│   └── *_example.txt         # 对应的示例模板文件
├── data/                     # 数据存储目录
│   └── chat_history.db       # SQLite聊天历史数据库
├── images/                   # 图片资源目录
│   ├── demo*.png            # 效果演示图
│   ├── wx_group*.png        # 微信群二维码
│   └── *pay.jpg             # 支付二维码
├── PROJECT_FRAMEWORK.md     # 项目框架文档（本文档）
├── CODING_STANDARDS.md      # 编码规范文档
├── LOGGING_GUIDELINES.md    # 日志记录规范
├── ENV_CONFIG.md            # 环境配置说明
├── requirements.txt         # Python依赖包列表
├── .env                     # 环境变量配置文件
├── .gitignore              # Git忽略文件配置
├── .dockerignore           # Docker忽略文件配置
├── Dockerfile              # Docker容器配置
├── docker-compose.yml      # Docker Compose配置
├── LICENSE                 # 开源许可证
└── README.md              # 项目说明文档
```

## 🔧 核心组件说明

### 1. 主要模块架构

#### main.py - 主程序控制器
- **核心类**: `XianyuLive`
- **主要功能**:
  - WebSocket连接管理和心跳机制
  - Token自动刷新和会话保持
  - 消息路由和分发
  - 人工接管模式控制
- **关键配置**: 心跳间隔、Token刷新机制、人工接管关键词

#### XianyuAgent.py - AI智能体系统
- **核心类**: 
  - `XianyuReplyBot`: 主要的AI回复机器人
  - `IntentRouter`: 意图识别路由器
  - `BaseAgent`: Agent基类
  - `PriceAgent`: 价格专家Agent
  - `TechAgent`: 技术专家Agent
  - `ClassifyAgent`: 分类专家Agent
  - `DefaultAgent`: 默认回复Agent
- **设计模式**: 策略模式 + 多专家协同决策
- **路由策略**: 技术类优先 → 价格类 → 大模型兜底

#### XianyuApis.py - API接口层
- **核心类**: `XianyuApis`
- **主要功能**:
  - 闲鱼平台Token获取和刷新
  - Cookie管理和自动更新
  - 登录状态检查和维护
  - 商品信息获取

#### context_manager.py - 上下文管理
- **核心类**: `ChatContextManager`
- **数据存储**: SQLite数据库
- **主要表结构**:
  - `messages`: 聊天消息记录
  - `chat_bargain_counts`: 议价次数统计
  - `items`: 商品信息缓存
- **功能特性**: 会话ID管理、历史消息限制、议价计数

### 2. 工具和配置模块

#### utils/xianyu_utils.py - 平台工具函数
- **功能**: 设备ID生成、UUID生成、签名算法、Cookie转换、数据解密

#### prompts/ - AI提示词管理
- **模板分类**: 分类、价格、技术、默认四大专家领域
- **格式**: 纯文本文件，支持热重载

## 🔍 核心业务流程

### 消息处理流程
1. **WebSocket接收** → 消息解析和过滤
2. **上下文加载** → 从数据库获取对话历史
3. **意图识别** → 多级路由决策（关键词→正则→LLM）
4. **专家分发** → 根据意图调用对应Agent
5. **回复生成** → LLM生成回复并应用安全过滤
6. **上下文更新** → 保存新消息到数据库
7. **消息发送** → 通过WebSocket发送回复

### 人工接管机制
- **触发**: 检测到特定关键词（默认为句号"。"）
- **状态管理**: 基于会话ID的接管状态跟踪
- **超时机制**: 自动退出人工模式（默认1小时）

### Token管理机制
- **自动刷新**: 定时检查Token有效期（默认1小时）
- **失败重试**: Token获取失败时的重试机制
- **连接重建**: Token刷新后自动重新建立WebSocket连接

## 🚀 开发和扩展指南

### 新增专家Agent流程
1. **定义提示词** → 在prompts/目录创建新的提示词文件
2. **创建Agent类** → 继承BaseAgent并实现generate方法
3. **注册Agent** → 在XianyuReplyBot._init_agents()中注册
4. **更新路由** → 在IntentRouter中添加相应路由规则

### 配置管理最佳实践
- **敏感配置**: 使用.env文件存储API密钥、Cookie等
- **功能开关**: 通过环境变量控制功能启用/禁用
- **超时配置**: 所有超时参数都可通过环境变量调整

### 数据库扩展
- **新表创建**: 在ChatContextManager._init_db()中添加
- **索引优化**: 为查询频繁的字段添加索引
- **数据迁移**: 兼容处理旧版本数据库结构

## 🔍 问题定位指南

### 常见问题类型及定位方法

| 问题类型 | 首先检查 | 相关文件 | 日志关键词 |
|---------|----------|----------|----------|
| 连接问题 | .env配置、Cookie有效性 | main.py, XianyuApis.py | "Token", "Cookie", "WebSocket" |
| AI回复问题 | 提示词文件、模型配置 | XianyuAgent.py, prompts/ | "Agent", "generate", "LLM" |
| 上下文问题 | 数据库文件、权限 | context_manager.py | "SQLite", "chat_history" |
| API调用问题 | 网络连接、接口变更 | XianyuApis.py | "API", "请求异常" |

### 快速排查步骤
1. **查看日志** - 使用loguru的彩色日志快速定位问题层级
2. **检查配置** - 验证.env文件中的关键配置项
3. **测试连接** - 确认网络和Cookie有效性
4. **数据库检查** - 验证SQLite文件完整性和权限
5. **提示词验证** - 确认提示词文件存在且格式正确

## 📝 开发规范要点

### 代码组织原则
- **单一职责**: 每个类和模块职责明确
- **依赖注入**: 通过构造函数传递依赖
- **配置外置**: 所有配置通过环境变量管理
- **异常处理**: 完整的异常捕获和日志记录

### 日志记录规范
- **结构化日志**: 使用loguru进行结构化日志记录
- **关键节点**: 在重要业务流程节点记录日志
- **错误追踪**: 详细记录异常堆栈和上下文信息
- **性能监控**: 记录关键操作的耗时信息

### AI集成规范
- **提示词管理**: 使用文件系统管理，支持热重载
- **安全过滤**: 对AI生成内容进行安全检查
- **错误恢复**: AI调用失败时的降级策略
- **上下文控制**: 合理控制输入上下文长度

## 🔄 文档维护
- 项目架构变更时及时更新本文档
- 新增核心组件时补充相应说明
- 定期审查和优化问题定位指南
- 保持与实际代码的同步更新 