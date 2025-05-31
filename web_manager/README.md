# XianyuAutoAgent Web管理界面

为XianyuAutoAgent项目提供的现代化Web管理界面，实现了对main.py进程的可视化管理和监控。

## 🌟 功能特性

### 🎛️ 核心功能
- **进程管理**: 启动、停止、重启main.py进程
- **实时监控**: 进程状态、CPU/内存使用率监控
- **日志管理**: 实时日志推送和历史日志查看
- **配置管理**: 可视化编辑.env环境变量
- **提示词管理**: 在线编辑AI提示词文件
- **系统信息**: 系统资源使用情况展示

### 🎨 界面特色
- **现代化设计**: 基于Element Plus的美观界面
- **响应式布局**: 支持桌面和移动设备
- **实时更新**: WebSocket实时通信
- **中文友好**: 完整的中文本地化

## 🏗️ 技术架构

### 后端技术栈
- **FastAPI**: 现代、快速的Web框架
- **WebSocket**: 实时双向通信
- **Pydantic**: 数据验证和序列化
- **Loguru**: 结构化日志记录
- **PSUtil**: 系统和进程监控

### 前端技术栈
- **Vue 3**: 渐进式JavaScript框架
- **Element Plus**: Vue 3 UI组件库
- **Pinia**: Vue状态管理
- **Vite**: 前端构建工具
- **Axios**: HTTP客户端

## 📦 安装和配置

### 环境要求
- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 后端安装
```bash
# 进入后端目录
cd web_manager/backend

# 安装Python依赖
pip install -r requirements.txt

# 启动后端服务
python app.py
```

后端服务将在 `http://localhost:8000` 启动

### 前端安装
```bash
# 进入前端目录
cd web_manager/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 `http://localhost:3000` 启动

## 🚀 快速开始

### 1. 启动后端服务
```bash
cd web_manager/backend
python app.py
```

### 2. 启动前端服务
```bash
cd web_manager/frontend
npm run dev
```

### 3. 访问管理界面
打开浏览器访问：`http://localhost:3000`

## 📋 功能说明

### 仪表盘
- 系统概览和关键指标
- 进程运行状态总览
- 最近错误日志快速查看

### 进程控制
- **启动**: 启动main.py进程
- **停止**: 优雅停止进程
- **重启**: 重启进程服务
- **状态监控**: 实时显示进程状态、PID、运行时长等

### 实时日志
- **实时推送**: WebSocket实时推送日志
- **日志过滤**: 按级别、时间、关键词过滤
- **历史查看**: 查看历史日志记录
- **日志导出**: 导出日志到本地文件

### 配置管理
- **环境变量**: 可视化编辑.env文件
- **配置验证**: 自动验证配置项格式
- **配置备份**: 自动备份配置变更
- **批量更新**: 支持批量修改配置项

### 提示词管理
- **文件列表**: 显示所有可编辑的提示词文件
- **在线编辑**: 代码编辑器支持语法高亮
- **版本备份**: 自动备份修改前的版本
- **内容验证**: 验证提示词内容格式
- **热重载**: 通知main.py重新加载提示词

### 系统信息
- **资源监控**: CPU、内存、磁盘使用情况
- **系统状态**: 运行时间、Python版本等
- **性能图表**: 历史性能数据可视化

## 🔧 配置说明

### 后端配置
后端服务的主要配置在`web_manager/backend/app.py`中：

```python
# 服务端口
PORT = 8000

# CORS配置
CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]

# WebSocket配置
WEBSOCKET_ENDPOINT = "/ws/logs"
```

### 前端配置
前端API接口配置在`web_manager/frontend/src/api/config.js`中：

```javascript
// API基础URL
export const API_BASE_URL = 'http://localhost:8000'

// WebSocket地址
export const WS_BASE_URL = 'ws://localhost:8000'
```

## 🔐 安全说明

### 访问控制
- 目前为开发版本，无认证机制
- 生产环境建议添加用户认证
- 建议配置防火墙限制访问

### 数据安全
- 敏感配置项在界面中部分隐藏
- 所有配置变更都有备份机制
- 日志不包含敏感信息

## 🐛 故障排除

### 常见问题

#### 1. 后端启动失败
```bash
# 检查Python版本
python --version

# 检查依赖安装
pip list | grep fastapi

# 检查端口占用
netstat -an | grep 8000
```

#### 2. 前端无法连接后端
- 检查后端服务是否启动
- 确认API地址配置正确
- 检查CORS配置是否包含前端地址

#### 3. WebSocket连接失败
- 确认WebSocket地址配置正确
- 检查浏览器是否支持WebSocket
- 查看浏览器控制台错误信息

#### 4. 进程控制失败
- 确认有足够的系统权限
- 检查main.py文件是否存在
- 查看错误日志获取详细信息

### 日志调试
启用详细日志输出：
```bash
# 后端调试模式
python app.py --debug

# 查看详细日志
tail -f logs/web_manager.log
```

## 🔄 开发和扩展

### 添加新功能页面
1. 在`frontend/src/views/`创建新页面组件
2. 在`frontend/src/router/`添加路由配置
3. 在主应用导航中添加菜单项

### 添加新API接口
1. 在`backend/app.py`添加路由处理
2. 在`backend/models/`定义数据模型
3. 在`backend/services/`实现业务逻辑

### 自定义主题
修改`frontend/src/styles/`中的样式文件来自定义界面主题。

## 📄 API文档

后端服务启动后，可以访问自动生成的API文档：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📝 更新日志

### v1.0.0 (2024-01-XX)
- ✨ 初始版本发布
- 🎛️ 实现进程管理功能
- 📊 添加实时日志监控
- ⚙️ 支持配置管理
- 📝 提供提示词编辑
- 📈 集成系统监控

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

### 开发环境设置
1. Fork项目仓库
2. 克隆到本地
3. 安装依赖
4. 创建新分支
5. 提交更改
6. 创建Pull Request

## 📞 技术支持

如果您在使用过程中遇到问题，可以通过以下方式获取帮助：
- 提交GitHub Issue
- 查看项目文档
- 联系项目维护者

## 📜 许可证

本项目采用MIT许可证，详见LICENSE文件。 