# 环境变量配置说明

## 必需配置

### 1. COOKIES_STR（必需）
咸鱼账户的Cookie字符串，用于身份验证。

**获取方法：**
1. 用浏览器登录咸鱼网站
2. 打开开发者工具（F12）
3. 进入Network选项卡
4. 刷新页面
5. 找到请求头中的Cookie字段，复制完整的Cookie字符串

**示例：**
```bash
COOKIES_STR="cna=xxxxx; cookie2=xxxxx; _tb_token_=xxxxx; unb=xxxxx; ..."
```

### 2. API_KEY（必需）
AI模型的API密钥，用于调用AI接口生成回复。

**示例：**
```bash
API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

## 可选配置

### 3. MODEL_BASE_URL（可选）
AI模型的基础URL，默认使用阿里云的DashScope。

**默认值：**
```bash
MODEL_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
```

### 4. LOG_LEVEL（可选）
日志级别，控制输出的日志详细程度。

**可选值：** DEBUG, INFO, WARNING, ERROR
**默认值：** DEBUG

```bash
LOG_LEVEL="INFO"
```

### 5. 心跳配置（可选）
```bash
HEARTBEAT_INTERVAL=15  # 心跳间隔（秒）
HEARTBEAT_TIMEOUT=5    # 心跳超时（秒）
```

### 6. Token配置（可选）
```bash
TOKEN_REFRESH_INTERVAL=3600  # Token刷新间隔（秒）
TOKEN_RETRY_INTERVAL=300     # Token重试间隔（秒）
```

### 7. 人工接管配置（可选）
```bash
MANUAL_MODE_TIMEOUT=3600  # 人工接管超时时间（秒）
TOGGLE_KEYWORDS="。"      # 切换关键词
```

### 8. 消息配置（可选）
```bash
MESSAGE_EXPIRE_TIME=300000  # 消息过期时间（毫秒）
```

## 配置文件创建

创建 `.env` 文件在项目根目录：

```bash
# 必需配置
COOKIES_STR="你的咸鱼Cookie字符串"
API_KEY="你的AI模型API密钥"

# 可选配置
LOG_LEVEL=INFO
MODEL_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
HEARTBEAT_INTERVAL=15
HEARTBEAT_TIMEOUT=5
TOKEN_REFRESH_INTERVAL=3600
TOKEN_RETRY_INTERVAL=300
MANUAL_MODE_TIMEOUT=3600
TOGGLE_KEYWORDS=。
MESSAGE_EXPIRE_TIME=300000
```

## 注意事项

1. **Cookie安全性：** Cookie包含您的账户信息，请妥善保管，不要泄露给他人
2. **API密钥安全性：** API密钥具有计费功能，请确保安全使用
3. **合法使用：** 请确保您的使用符合咸鱼平台的服务条款
4. **测试环境：** 建议先在测试环境中验证配置的正确性 