# 日志记录规范文档

## 🎯 日志的重要性
日志是项目中最重要的问题诊断和性能监控工具，特别是在AI协助开发的环境中。详细、结构化的日志可以帮助AI快速定位问题根源，提高问题解决的效率。

## 📊 日志级别定义

### 级别优先级和使用场景
```python
# 日志级别从高到低
CRITICAL = 50  # 系统崩溃级别错误
ERROR = 40     # 严重错误，但系统仍可运行
WARNING = 30   # 警告信息，潜在问题
INFO = 20      # 一般信息，业务流程记录
DEBUG = 10     # 调试信息，详细的执行步骤
```

### 各级别使用指南

#### CRITICAL（严重错误）
**使用场景：** 系统无法继续运行的致命错误
```python
try:
    database_connection = create_database_connection()
except DatabaseConnectionError as e:
    logger.critical(f"数据库连接完全失败，系统无法启动: {str(e)}")
    sys.exit(1)
```

#### ERROR（错误）
**使用场景：** 功能执行失败，但不影响系统整体运行
```python
def process_payment(order_id: int, amount: float) -> dict:
    """处理支付请求"""
    logger.info(f"开始处理支付: order_id={order_id}, amount={amount}")
    
    try:
        payment_result = payment_gateway.charge(order_id, amount)
        logger.info(f"支付处理成功: order_id={order_id}, transaction_id={payment_result['id']}")
        return payment_result
    except PaymentGatewayError as e:
        logger.error(f"支付网关错误: order_id={order_id}, error={str(e)}, error_code={e.code}")
        return {'success': False, 'error': 'payment_gateway_error'}
    except InsufficientFundsError as e:
        logger.error(f"余额不足: order_id={order_id}, required={amount}, available={e.available_balance}")
        return {'success': False, 'error': 'insufficient_funds'}
```

#### WARNING（警告）
**使用场景：** 潜在问题，需要注意但不影响当前功能
```python
def send_email_notification(user_id: int, subject: str, content: str) -> bool:
    """发送邮件通知"""
    logger.info(f"准备发送邮件通知: user_id={user_id}, subject={subject}")
    
    # 检查邮件发送频率限制
    recent_emails = get_recent_email_count(user_id, minutes=60)
    if recent_emails >= 10:
        logger.warning(f"用户邮件发送频率过高: user_id={user_id}, recent_count={recent_emails}")
        return False
    
    # 检查邮箱有效性
    user_email = get_user_email(user_id)
    if not validate_email_format(user_email):
        logger.warning(f"用户邮箱格式无效: user_id={user_id}, email={user_email}")
        return False
    
    try:
        email_service.send(user_email, subject, content)
        logger.info(f"邮件发送成功: user_id={user_id}")
        return True
    except Exception as e:
        logger.error(f"邮件发送失败: user_id={user_id}, error={str(e)}")
        return False
```

#### INFO（信息）
**使用场景：** 重要的业务流程和状态变化
```python
def user_login_process(username: str, password: str) -> dict:
    """用户登录流程"""
    logger.info(f"用户登录尝试开始: username={username}")
    
    # 验证用户身份
    user = authenticate_user(username, password)
    if user:
        logger.info(f"用户身份验证成功: user_id={user.id}, username={username}")
        
        # 生成会话token
        session_token = generate_session_token(user.id)
        logger.info(f"会话token生成成功: user_id={user.id}, token_id={session_token.id}")
        
        # 更新最后登录时间
        update_last_login_time(user.id)
        logger.info(f"用户最后登录时间已更新: user_id={user.id}")
        
        return {'success': True, 'token': session_token.value}
    else:
        logger.warning(f"用户身份验证失败: username={username}")
        return {'success': False, 'error': 'invalid_credentials'}
```

#### DEBUG（调试）
**使用场景：** 详细的执行步骤和变量状态，主要用于开发调试
```python
def calculate_order_total(order_id: int) -> float:
    """计算订单总金额"""
    logger.debug(f"开始计算订单总金额: order_id={order_id}")
    
    # 获取订单项目
    order_items = get_order_items(order_id)
    logger.debug(f"获取到订单项目: order_id={order_id}, item_count={len(order_items)}")
    
    subtotal = 0.0
    for item in order_items:
        item_total = item.quantity * item.unit_price
        subtotal += item_total
        logger.debug(f"订单项目计算: item_id={item.id}, quantity={item.quantity}, "
                    f"unit_price={item.unit_price}, item_total={item_total}")
    
    logger.debug(f"订单小计计算完成: order_id={order_id}, subtotal={subtotal}")
    
    # 计算税费
    tax_rate = get_tax_rate_for_order(order_id)
    tax_amount = subtotal * tax_rate
    logger.debug(f"税费计算: order_id={order_id}, tax_rate={tax_rate}, tax_amount={tax_amount}")
    
    # 计算总金额
    total_amount = subtotal + tax_amount
    logger.info(f"订单总金额计算完成: order_id={order_id}, total={total_amount}")
    
    return total_amount
```

## 🏗️ 日志系统架构

### Winston风格日志配置
```python
"""
日志工具模块

提供统一的日志记录功能，支持多种输出格式和目标。
采用Winston风格的设计理念，支持结构化日志记录。

Author: AI Assistant
Created: 2024-01-XX
"""

import logging
import logging.handlers
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

class LogLevel(Enum):
    """日志级别枚举"""
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10

class StructuredFormatter(logging.Formatter):
    """
    结构化日志格式化器
    
    将日志记录格式化为JSON格式，便于日志分析和AI处理
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录为JSON字符串
        
        Args:
            record (logging.LogRecord): 日志记录对象
            
        Returns:
            str: JSON格式的日志字符串
        """
        # 构建基础日志信息
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # 添加异常信息（如果存在）
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # 添加自定义字段（如果存在）
        if hasattr(record, 'extra_data'):
            log_entry['extra'] = record.extra_data
        
        return json.dumps(log_entry, ensure_ascii=False)

class ProjectLogger:
    """
    项目日志管理器
    
    提供统一的日志配置和管理功能，支持多种输出目标和格式
    """
    
    def __init__(self, 
                 name: str = 'project_logger',
                 log_level: LogLevel = LogLevel.INFO,
                 log_dir: str = 'logs'):
        """
        初始化日志管理器
        
        Args:
            name (str): 日志器名称
            log_level (LogLevel): 日志记录级别
            log_dir (str): 日志文件存储目录
        """
        self.name = name
        self.log_level = log_level
        self.log_dir = log_dir
        
        # 确保日志目录存在
        os.makedirs(log_dir, exist_ok=True)
        
        # 创建日志器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level.value)
        
        # 防止重复添加处理器
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """设置日志处理器"""
        # 控制台处理器（开发环境友好格式）
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        
        # 文件处理器（结构化JSON格式）
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(self.log_dir, 'application.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(StructuredFormatter())
        file_handler.setLevel(logging.DEBUG)
        
        # 错误文件处理器（只记录ERROR及以上级别）
        error_handler = logging.handlers.RotatingFileHandler(
            os.path.join(self.log_dir, 'error.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setFormatter(StructuredFormatter())
        error_handler.setLevel(logging.ERROR)
        
        # 添加处理器到日志器
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
    
    def get_logger(self, module_name: Optional[str] = None) -> logging.Logger:
        """
        获取日志器实例
        
        Args:
            module_name (Optional[str]): 模块名称，用于标识日志来源
            
        Returns:
            logging.Logger: 配置好的日志器实例
        """
        if module_name:
            return logging.getLogger(f"{self.name}.{module_name}")
        return self.logger

# 全局日志管理器实例
_global_logger_manager = ProjectLogger()

def get_logger(module_name: str = None) -> logging.Logger:
    """
    获取项目日志器的便捷函数
    
    Args:
        module_name (str): 模块名称
        
    Returns:
        logging.Logger: 配置好的日志器实例
    """
    return _global_logger_manager.get_logger(module_name)

def log_function_call(func):
    """
    函数调用日志装饰器
    
    自动记录函数的调用和返回信息
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        
        # 记录函数调用开始
        logger.debug(f"函数调用开始: {func.__name__}, args={args}, kwargs={kwargs}")
        
        try:
            # 执行函数
            result = func(*args, **kwargs)
            
            # 记录函数调用成功
            logger.debug(f"函数调用成功: {func.__name__}, result_type={type(result).__name__}")
            
            return result
        except Exception as e:
            # 记录函数调用异常
            logger.error(f"函数调用异常: {func.__name__}, exception={str(e)}")
            raise
    
    return wrapper
```

## 📝 日志记录最佳实践

### 1. 业务流程关键节点记录
```python
def process_user_order(user_id: int, order_data: dict) -> dict:
    """处理用户订单"""
    logger = get_logger(__name__)
    
    # 流程开始
    logger.info(f"订单处理流程开始: user_id={user_id}, order_type={order_data.get('type')}")
    
    try:
        # 第一步：验证用户
        logger.info(f"开始验证用户: user_id={user_id}")
        user = validate_user(user_id)
        if not user:
            logger.warning(f"用户验证失败: user_id={user_id}")
            return {'success': False, 'error': 'invalid_user'}
        logger.info(f"用户验证成功: user_id={user_id}")
        
        # 第二步：验证订单数据
        logger.info(f"开始验证订单数据: user_id={user_id}")
        validation_result = validate_order_data(order_data)
        if not validation_result['valid']:
            logger.warning(f"订单数据验证失败: user_id={user_id}, errors={validation_result['errors']}")
            return {'success': False, 'error': 'invalid_order_data', 'details': validation_result['errors']}
        logger.info(f"订单数据验证成功: user_id={user_id}")
        
        # 第三步：检查库存
        logger.info(f"开始检查库存: user_id={user_id}")
        inventory_check = check_inventory(order_data['items'])
        if not inventory_check['available']:
            logger.warning(f"库存不足: user_id={user_id}, unavailable_items={inventory_check['unavailable_items']}")
            return {'success': False, 'error': 'insufficient_inventory'}
        logger.info(f"库存检查通过: user_id={user_id}")
        
        # 第四步：创建订单
        logger.info(f"开始创建订单: user_id={user_id}")
        order = create_order(user_id, order_data)
        logger.info(f"订单创建成功: user_id={user_id}, order_id={order.id}")
        
        # 第五步：处理支付
        logger.info(f"开始处理支付: user_id={user_id}, order_id={order.id}")
        payment_result = process_payment(order.id, order.total_amount)
        if not payment_result['success']:
            logger.error(f"支付处理失败: user_id={user_id}, order_id={order.id}, error={payment_result['error']}")
            # 取消订单
            cancel_order(order.id)
            logger.info(f"订单已取消: order_id={order.id}")
            return {'success': False, 'error': 'payment_failed'}
        logger.info(f"支付处理成功: user_id={user_id}, order_id={order.id}, transaction_id={payment_result['transaction_id']}")
        
        # 流程成功完成
        logger.info(f"订单处理流程成功完成: user_id={user_id}, order_id={order.id}")
        return {'success': True, 'order_id': order.id}
        
    except Exception as e:
        logger.error(f"订单处理流程发生异常: user_id={user_id}, exception={str(e)}")
        return {'success': False, 'error': 'system_error'}
```

### 2. 性能监控日志记录
```python
import time
from functools import wraps

def log_performance(threshold_seconds: float = 1.0):
    """
    性能监控装饰器
    
    Args:
        threshold_seconds (float): 性能警告阈值（秒）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            
            start_time = time.time()
            logger.debug(f"性能监控开始: function={func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                if execution_time > threshold_seconds:
                    logger.warning(f"函数执行时间超过阈值: function={func.__name__}, "
                                 f"execution_time={execution_time:.3f}s, threshold={threshold_seconds}s")
                else:
                    logger.debug(f"函数执行完成: function={func.__name__}, "
                               f"execution_time={execution_time:.3f}s")
                
                return result
                
            except Exception as e:
                end_time = time.time()
                execution_time = end_time - start_time
                logger.error(f"函数执行异常: function={func.__name__}, "
                           f"execution_time={execution_time:.3f}s, exception={str(e)}")
                raise
        
        return wrapper
    return decorator

# 使用示例
@log_performance(threshold_seconds=2.0)
def complex_calculation(data_size: int) -> list:
    """复杂计算函数"""
    logger = get_logger(__name__)
    logger.info(f"开始复杂计算: data_size={data_size}")
    
    # 模拟复杂计算
    result = []
    for i in range(data_size):
        # 一些复杂的计算逻辑
        result.append(i * i)
    
    logger.info(f"复杂计算完成: data_size={data_size}, result_length={len(result)}")
    return result
```

### 3. 数据库操作日志记录
```python
def log_database_operation(operation_type: str):
    """
    数据库操作日志装饰器
    
    Args:
        operation_type (str): 操作类型（SELECT, INSERT, UPDATE, DELETE）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            
            logger.debug(f"数据库操作开始: operation={operation_type}, function={func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                
                # 根据操作类型记录不同级别的日志
                if operation_type in ['INSERT', 'UPDATE', 'DELETE']:
                    logger.info(f"数据库修改操作成功: operation={operation_type}, function={func.__name__}")
                else:
                    logger.debug(f"数据库查询操作成功: operation={operation_type}, function={func.__name__}")
                
                return result
                
            except Exception as e:
                logger.error(f"数据库操作失败: operation={operation_type}, function={func.__name__}, error={str(e)}")
                raise
        
        return wrapper
    return decorator

# 使用示例
@log_database_operation('INSERT')
def create_user(username: str, email: str, password_hash: str) -> User:
    """创建新用户"""
    logger = get_logger(__name__)
    
    logger.info(f"开始创建用户: username={username}, email={email}")
    
    try:
        # 检查用户名是否存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            logger.warning(f"用户名已存在: username={username}")
            raise ValueError("用户名已被使用")
        
        # 创建新用户
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        logger.info(f"用户创建成功: user_id={new_user.id}, username={username}")
        return new_user
        
    except Exception as e:
        logger.error(f"用户创建失败: username={username}, error={str(e)}")
        db.session.rollback()
        raise
```

## 🔍 AI友好的日志格式

### 结构化日志示例
```python
def log_structured_event(event_type: str, event_data: dict, user_id: int = None):
    """
    记录结构化事件日志
    
    这种格式特别适合AI分析和问题诊断
    """
    logger = get_logger(__name__)
    
    # 构建结构化日志数据
    log_data = {
        'event_type': event_type,
        'timestamp': datetime.now().isoformat(),
        'data': event_data
    }
    
    if user_id:
        log_data['user_id'] = user_id
    
    # 使用extra参数传递结构化数据
    logger.info(f"结构化事件: {event_type}", extra={'extra_data': log_data})

# 使用示例
def user_login_event(user_id: int, login_method: str, ip_address: str):
    """记录用户登录事件"""
    log_structured_event(
        event_type='user_login',
        event_data={
            'login_method': login_method,
            'ip_address': ip_address,
            'user_agent': request.headers.get('User-Agent'),
            'success': True
        },
        user_id=user_id
    )

def api_request_event(endpoint: str, method: str, response_time: float, status_code: int):
    """记录API请求事件"""
    log_structured_event(
        event_type='api_request',
        event_data={
            'endpoint': endpoint,
            'method': method,
            'response_time_ms': response_time * 1000,
            'status_code': status_code,
            'success': status_code < 400
        }
    )
```

## 📋 日志记录检查清单

### 每个函数必须包含的日志
- [ ] **函数开始执行**：记录函数名和关键参数
- [ ] **主要业务节点**：记录重要的业务逻辑执行状态
- [ ] **异常处理**：记录所有异常的详细信息
- [ ] **函数执行结果**：记录执行成功或失败的结果

### AI友好的日志特征
- [ ] **结构化格式**：使用JSON格式便于解析
- [ ] **详细的上下文信息**：包含足够的诊断信息
- [ ] **一致的字段命名**：使用统一的字段名称规范
- [ ] **合适的日志级别**：根据重要性选择正确的级别
- [ ] **时间戳信息**：包含精确的时间信息
- [ ] **模块和函数定位**：清楚标识日志来源

### 错误日志必须包含的信息
- [ ] **错误类型**：具体的异常类型
- [ ] **错误消息**：详细的错误描述
- [ ] **错误发生的上下文**：相关的变量值和状态
- [ ] **堆栈跟踪**：完整的调用栈信息
- [ ] **用户标识**：如果涉及用户操作
- [ ] **请求标识**：如果是API请求相关

## 🚀 日志分析和监控

### 常见问题的日志模式
```python
# 1. 性能问题模式
def identify_performance_issues():
    """识别性能问题的日志模式"""
    patterns = [
        "execution_time.*[5-9]\\d+\\.\\d+s",  # 执行时间超过5秒
        "database.*timeout",                   # 数据库超时
        "memory.*usage.*9[0-9]%"              # 内存使用率超过90%
    ]

# 2. 错误频发模式
def identify_frequent_errors():
    """识别频繁错误的日志模式"""
    patterns = [
        "ConnectionError.*occurred.*times",    # 连接错误频发
        "ValidationError.*user_id=\\d+",      # 特定用户频繁出错
        "PaymentGateway.*error.*rate.*high"   # 支付网关错误率高
    ]

# 3. 安全问题模式
def identify_security_issues():
    """识别安全问题的日志模式"""
    patterns = [
        "login_attempts.*exceeded.*user_id",  # 暴力破解尝试
        "suspicious_activity.*ip_address",    # 可疑活动
        "unauthorized_access.*attempt"        # 未授权访问尝试
    ]
```

---

**遵循这些日志规范，让AI能够更快速、准确地诊断和解决问题！** 