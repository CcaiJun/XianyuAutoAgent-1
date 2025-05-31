# 咸鱼外挂AI客服系统 - 项目架构文档

## 📋 项目概述
咸鱼外挂AI客服系统，通过登录cookie操作用户账户进行AI客服回复行为。系统包含命令行客户端和Web前端管理界面。

## 🏗️ 项目架构概览

### 目录结构
```
XianyuAutoAgent/
├── main.py                     # 主程序入口 - 咸鱼WebSocket客服服务
├── XianyuAgent.py              # AI回复机器人核心逻辑
├── XianyuApis.py               # 咸鱼API接口封装
├── context_manager.py          # 聊天上下文管理器
├── web_frontend/               # Web前端目录
│   ├── app.py                 # Flask主应用
│   ├── services/              # 业务逻辑层
│   │   └── log_service.py     # 日志处理服务
│   ├── static/                # 静态资源
│   │   ├── css/
│   │   │   └── styles.css     # 样式文件
│   │   ├── js/
│   │   │   └── main.js        # 前端交互逻辑
│   │   └── images/            # 图片资源
│   ├── templates/             # HTML模板
│   │   └── index.html         # 主页面
│   └── requirements_web.txt   # Web端依赖
├── utils/                      # 工具函数目录
│   ├── __init__.py
│   └── xianyu_utils.py        # 咸鱼相关工具函数
├── logs/                       # 日志目录
├── data/                       # 数据存储目录
├── prompts/                    # AI提示词目录
├── config_backups/             # 配置备份目录
├── prompt_backups/             # 提示词备份目录
├── web_manager/                # Web管理相关
├── images/                     # 图片资源
├── requirements.txt            # 主程序依赖
├── ENV_CONFIG.md              # 环境配置说明
├── PROJECT_FRAMEWORK.md       # 本文档
├── .env                       # 环境变量配置
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── LICENSE
└── README.md
```

## 🔧 核心组件说明

### 1. 主程序模块 (main.py)
- **功能**: 咸鱼WebSocket连接管理，实时消息处理
- **日志输出**: 
  - 连接心跳信息
  - 用户消息接收日志
  - AI回复发送日志
  - 系统状态信息
- **技术栈**: asyncio, websockets, loguru

### 2. AI代理模块 (XianyuAgent.py)
- **功能**: AI回复逻辑，智能客服对话生成
- **集成**: OpenAI API接口调用
- **上下文管理**: 多轮对话上下文维护

### 3. API接口模块 (XianyuApis.py)
- **功能**: 咸鱼平台API封装
- **包含**: 用户认证、商品信息获取、消息发送等

### 4. 上下文管理 (context_manager.py)
- **功能**: 聊天会话上下文管理
- **特性**: 多用户会话隔离，上下文持久化

### 5. Web前端模块 (web_frontend/)
- **app.py**: Flask主应用，提供Web服务和WebSocket通信
- **log_service.py**: 日志处理服务，实时读取main.py日志输出
- **前端页面**: 实时日志显示界面，支持WebSocket实时推送

### 6. 工具模块 (utils/)
- **xianyu_utils.py**: 咸鱼平台相关工具函数
- **包含**: UUID生成、设备ID生成、Cookie处理、加密解密等

## 🔍 系统运行流程

### 主程序运行流程
1. **初始化阶段** → 加载环境配置，初始化API客户端
2. **Token获取** → 通过Cookie获取访问令牌
3. **WebSocket连接** → 建立与咸鱼服务器的实时连接
4. **消息监听** → 实时接收用户消息和系统通知
5. **AI处理** → 调用AI代理生成回复内容
6. **消息发送** → 通过WebSocket发送回复消息
7. **日志记录** → 记录所有操作和状态信息

### Web前端运行流程
1. **服务启动** → Flask应用启动，监听Web端口
2. **日志监控** → 实时监控main.py的日志输出文件
3. **WebSocket推送** → 将日志内容实时推送到前端
4. **页面显示** → 浏览器实时显示格式化的日志信息

**✅ 实时日志显示功能已完成配置！**
- main.py已配置文件日志输出
- Web前端正在实时监控日志文件
- 支持心跳、用户消息、AI回复、错误等各种日志类型的实时显示
- 访问 http://localhost:8080 查看实时日志流

## 📊 日志系统架构

### 日志分类
- **INFO级别**: 
  - 用户消息接收: `用户: {用户名} (ID: {用户ID}), 商品: {商品ID}, 会话: {会话ID}, 消息: {消息内容}`
  - AI回复发送: `机器人回复: {回复内容}`
  - 连接状态: `连接注册完成`、`Token刷新成功`
  
- **WARNING级别**:
  - 连接异常: `心跳响应超时，可能连接已断开`
  - 数据异常: `无法获取商品ID`
  
- **ERROR级别**:
  - 系统错误: `Token刷新失败`、`处理消息时发生错误`
  - 连接错误: `连接发生错误`

### 日志格式
使用loguru库，支持彩色输出和结构化日志记录

## 🚀 部署和运行

### 主程序运行
```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env

# 运行主程序
python main.py
```

### Web前端运行
```bash
# 进入前端目录
cd web_frontend

# 安装Web端依赖
pip install -r requirements_web.txt

# 运行Web服务
python app.py
# 或使用简化启动脚本
python run_web.py
```

**注意：** 如果遇到启动失败，请确保：
- 所有依赖已正确安装
- Python路径配置正确
- 无端口冲突（默认8080端口）

## 📝 配置管理

### 环境变量配置 (.env)
- 咸鱼Cookie信息
- OpenAI API配置
- 心跳和重连参数
- 人工接管配置

### 功能开关
- 人工接管模式
- 自动回复开关
- 日志级别控制

## 🔄 扩展和维护

### 新增功能开发流程
1. **确定功能范围** → 分析需求，确定修改范围
2. **选择修改模块** → 根据功能类型选择对应模块
3. **实现核心逻辑** → 在相应模块中实现功能
4. **更新日志输出** → 添加必要的日志记录
5. **测试验证** → 验证功能正常运行
6. **更新文档** → 同步更新架构文档

### 问题排查指南
| 问题类型 | 检查项目 | 相关文件 |
|---------|----------|----------|
| 连接问题 | Cookie有效性、Token状态 | main.py, .env |
| AI回复问题 | OpenAI API配置、提示词 | XianyuAgent.py, prompts/ |
| 消息处理问题 | WebSocket状态、消息解析 | main.py, XianyuApis.py |
| Web前端问题 | Flask服务、日志读取 | web_frontend/ |

## 📋 注意事项

### 安全要求
- Cookie信息必须保密，存储在.env文件中
- 不要将敏感信息提交到代码仓库
- 定期更新访问令牌

### 性能考虑
- 日志文件定期清理，避免占用过多磁盘空间
- WebSocket连接异常时自动重连
- 合理设置心跳间隔，平衡性能和稳定性

### 开发规范
- 所有新增代码必须包含详细的中文注释
- 重要操作必须添加日志记录
- 遵循现有的代码风格和架构设计 