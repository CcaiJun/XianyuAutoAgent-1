# 咸鱼AI客服系统 - Web前端

🐟 **实时日志监控界面**

## 📋 功能特性

- ✅ **实时日志显示** - 通过WebSocket实时推送main.py的日志输出
- 🔍 **日志分类** - 自动识别心跳、用户消息、AI回复、系统等不同类型日志
- 🎨 **美观界面** - 现代化设计，支持响应式布局
- ⏸️ **控制功能** - 暂停、清空、加载历史日志
- 🔧 **日志过滤** - 按级别过滤INFO、WARNING、ERROR、DEBUG日志
- 📱 **移动支持** - 支持手机和平板设备访问

## 🚀 快速开始

### 1. 安装依赖

```bash
# 进入web前端目录
cd web_frontend

# 安装Python依赖
pip install -r requirements_web.txt
```

### 2. 启动Web服务

```bash
# 方法1: 使用简化启动脚本
python run_web.py

# 方法2: 直接启动主应用
python app.py
```

### 3. 访问界面

打开浏览器访问: **http://localhost:8080**

## ⚙️ 配置选项

可以通过环境变量配置Web服务:

```bash
# 设置监听地址和端口
export WEB_HOST=0.0.0.0
export WEB_PORT=8080

# 设置调试模式
export WEB_DEBUG=true

# 启动服务
python app.py
```

## 📊 界面说明

### 页面组成

1. **顶部状态栏**
   - 连接状态指示器
   - 在线客户端数量
   - 日志总数统计

2. **控制面板**
   - 暂停/继续按钮
   - 清空日志按钮
   - 加载历史日志按钮
   - 日志级别过滤器

3. **日志显示区**
   - 实时日志流
   - 自动滚动控制
   - 日志条目悬停高亮

4. **底部状态栏**
   - 最后更新时间
   - 版本信息
   - 服务器状态

### 日志分类说明

| 分类 | 描述 | 颜色标识 |
|------|------|----------|
| 🫀 心跳 | 连接心跳、Token刷新等 | 绿色 |
| 👤 用户消息 | 用户发送的消息 | 蓝色 |
| 🤖 AI回复 | 机器人自动回复 | 紫色 |
| ✋ 人工接管 | 人工接管相关操作 | 橙色 |
| ⚙️ 系统 | 系统运行状态信息 | 灰色 |
| ❌ 错误 | 错误和异常信息 | 红色 |

## 🔧 技术架构

### 后端技术栈
- **Flask** - Web框架
- **Flask-SocketIO** - WebSocket支持
- **Watchdog** - 文件监控
- **Loguru** - 日志处理

### 前端技术栈
- **原生HTML/CSS/JavaScript** - 无框架依赖
- **Socket.IO** - 实时通信
- **CSS Grid/Flexbox** - 响应式布局

### 工作原理

```
main.py (loguru日志) 
    ↓
日志文件 (logs/xianyu_agent.log)
    ↓
LogService (文件监控)
    ↓
Flask-SocketIO (WebSocket)
    ↓
前端页面 (实时显示)
```

## 📝 API接口

### HTTP接口

- `GET /` - 主页面
- `GET /api/status` - 获取系统状态
- `GET /api/logs/clear` - 清空前端日志显示

### WebSocket事件

#### 客户端 → 服务器
- `connect` - 连接建立
- `disconnect` - 连接断开
- `request_log_history` - 请求历史日志
- `ping` - 心跳检测

#### 服务器 → 客户端
- `new_log` - 新日志推送
- `connection_status` - 连接状态更新
- `status_update` - 服务器状态更新
- `clear_logs` - 清空日志命令
- `log_history_loaded` - 历史日志加载完成
- `pong` - 心跳响应

## 🐛 故障排除

### 常见问题

**1. 无法连接到WebSocket**
```bash
# 检查端口是否被占用
netstat -tlnp | grep 8080

# 检查防火墙设置
sudo ufw status
```

**2. 日志不显示**
```bash
# 检查日志文件是否存在
ls -la logs/

# 检查main.py是否在运行
ps aux | grep main.py
```

**3. 页面无法访问**
```bash
# 检查Web服务状态
curl http://localhost:8080/api/status
```

### 调试模式

启用调试模式获取更多信息:

```bash
export WEB_DEBUG=true
python app.py
```

## 📂 目录结构

```
web_frontend/
├── app.py                  # Flask主应用
├── run_web.py              # 简化启动脚本
├── requirements_web.txt    # Python依赖
├── README.md              # 本文档
├── services/              # 业务逻辑层
│   └── log_service.py     # 日志处理服务
├── static/                # 静态资源
│   ├── css/
│   │   └── styles.css     # 样式文件
│   ├── js/
│   │   └── main.js        # 前端逻辑
│   └── images/            # 图片资源
└── templates/             # HTML模板
    └── index.html         # 主页面
```

## 🔗 相关文档

- [项目架构文档](../PROJECT_FRAMEWORK.md)
- [环境配置说明](../ENV_CONFIG.md)
- [主程序文档](../README.md)

## 📞 技术支持

如有问题，请检查:
1. Python环境和依赖包
2. 网络连接和端口配置
3. main.py是否正常运行
4. 日志文件权限设置

---

**咸鱼AI客服系统 Web前端 v1.0**  
*实时日志监控，让系统运行状态一目了然* 🐟 