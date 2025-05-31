# Python编码规范文档

## 📖 规范目的
本文档定义了项目中Python代码的编写规范，确保代码的一致性、可读性和可维护性。所有AI生成的代码都必须严格遵循这些规范。

## 🎯 编码基本原则

### 1. 可读性第一
- 代码是写给人看的，机器只是恰好能执行
- 宁可啰嗦一点，也要保证清晰明了
- 优先使用描述性的变量名和函数名

### 2. 一致性原则
- 整个项目使用统一的编码风格
- 遵循PEP8规范的同时适应项目特点
- 保持命名规范的一致性

### 3. 安全第一
- 所有用户输入都必须验证
- 敏感信息不得硬编码
- 异常处理必须完整覆盖

## 📝 命名规范

### 变量命名
```python
# ✅ 推荐做法：使用描述性名称
user_login_count = 0
database_connection_string = ""
api_response_data = {}

# ❌ 避免做法：使用缩写或无意义名称
usr_cnt = 0
db_str = ""
data = {}
```

### 函数命名
```python
# ✅ 推荐做法：动词开头，描述具体功能
def calculate_user_total_score(user_id: int) -> float:
    """计算用户的总分数"""
    pass

def validate_email_format(email: str) -> bool:
    """验证邮箱格式是否正确"""
    pass

def send_notification_email(recipient: str, subject: str, content: str) -> bool:
    """发送通知邮件"""
    pass

# ❌ 避免做法：名称过于简单或不明确
def calc(x):
    pass

def check(data):
    pass
```

### 类命名
```python
# ✅ 推荐做法：使用大驼峰命名法，名词为主
class UserManager:
    """用户管理器类，负责用户相关的业务逻辑"""
    pass

class DatabaseConnection:
    """数据库连接类，封装数据库操作"""
    pass

class EmailNotificationService:
    """邮件通知服务类"""
    pass

# ❌ 避免做法：使用下划线或小写
class user_manager:
    pass
```

### 常量命名
```python
# ✅ 推荐做法：全大写字母，下划线分隔
MAX_LOGIN_ATTEMPTS = 3
DEFAULT_TIMEOUT_SECONDS = 30
DATABASE_CONNECTION_TIMEOUT = 60
API_BASE_URL = "https://api.example.com"

# 配置相关常量
CONFIG_FILE_PATH = "config/settings.json"
LOG_FILE_PATH = "logs/application.log"
```

### 模块和包命名
```python
# ✅ 推荐做法：小写字母，下划线分隔
# 文件名示例
user_service.py
database_manager.py
email_notification.py
api_client.py

# 包名示例
utils/
models/
services/
controllers/
```

## 📋 代码结构规范

### 文件头部注释模板
```python
"""
模块名称：用户认证服务

功能描述：
    提供用户登录、注册、密码重置等认证相关功能。
    包含用户权限验证和session管理。

主要类/函数：
    - UserAuthService: 用户认证服务主类
    - authenticate_user(): 用户登录认证
    - register_new_user(): 新用户注册
    - reset_user_password(): 密码重置

依赖模块：
    - database_manager: 数据库操作
    - password_utils: 密码加密工具
    - logger: 日志记录

作者：AI Assistant
创建时间：2024-01-XX
最后修改：2024-01-XX
版本：1.0.0
"""

import os
import sys
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta

# 第三方库导入
import bcrypt
import jwt
from sqlalchemy import create_engine

# 项目内部导入
from utils.logger import get_logger
from utils.validators import validate_email, validate_password
from config.settings import get_database_config
from models.user_model import User

# 初始化日志记录器
logger = get_logger(__name__)
```

### 函数定义规范
```python
def process_user_registration(
    username: str, 
    email: str, 
    password: str,
    profile_data: Optional[Dict[str, str]] = None
) -> Dict[str, Union[bool, str, Dict]]:
    """
    处理用户注册请求
    
    验证用户提供的注册信息，创建新用户账户，并发送确认邮件。
    如果注册过程中出现任何错误，会记录详细日志并返回错误信息。
    
    Args:
        username (str): 用户名，3-20个字符，只能包含字母、数字和下划线
        email (str): 邮箱地址，必须是有效的邮箱格式
        password (str): 密码，至少8个字符，包含字母和数字
        profile_data (Optional[Dict[str, str]]): 可选的用户资料信息
            - full_name (str): 用户全名
            - phone (str): 手机号码
            - address (str): 地址信息
    
    Returns:
        Dict[str, Union[bool, str, Dict]]: 注册结果字典
            - success (bool): 注册是否成功
            - message (str): 操作结果消息
            - user_id (int): 新用户ID（成功时）
            - errors (List[str]): 错误列表（失败时）
    
    Raises:
        ValueError: 当输入参数格式不正确时
        DatabaseError: 当数据库操作失败时
        EmailError: 当发送确认邮件失败时
    
    Example:
        >>> result = process_user_registration(
        ...     username="john_doe",
        ...     email="john@example.com", 
        ...     password="secure123",
        ...     profile_data={"full_name": "John Doe"}
        ... )
        >>> if result['success']:
        ...     print(f"用户注册成功，ID: {result['user_id']}")
    
    Note:
        - 用户名必须在系统中唯一
        - 邮箱地址必须在系统中唯一
        - 密码会使用bcrypt进行安全加密
        - 注册成功后会自动发送确认邮件
    """
    # 记录注册尝试开始
    logger.info(f"开始处理用户注册: username={username}, email={email}")
    
    # 输入参数验证
    validation_errors = []
    
    # 验证用户名格式
    if not username or len(username) < 3 or len(username) > 20:
        validation_errors.append("用户名长度必须在3-20个字符之间")
        logger.warning(f"用户名格式无效: {username}")
    
    # 验证邮箱格式
    if not validate_email(email):
        validation_errors.append("邮箱格式不正确")
        logger.warning(f"邮箱格式无效: {email}")
    
    # 验证密码强度
    if not validate_password(password):
        validation_errors.append("密码至少8个字符，必须包含字母和数字")
        logger.warning("密码强度不符合要求")
    
    # 如果有验证错误，直接返回
    if validation_errors:
        logger.error(f"用户注册验证失败: {validation_errors}")
        return {
            'success': False,
            'message': '输入信息验证失败',
            'errors': validation_errors
        }
    
    try:
        # 检查用户名是否已存在
        existing_user = user_service.get_user_by_username(username)
        if existing_user:
            logger.warning(f"用户名已存在: {username}")
            return {
                'success': False,
                'message': '用户名已被使用',
                'errors': ['用户名已被其他用户使用']
            }
        
        # 检查邮箱是否已注册
        existing_email = user_service.get_user_by_email(email)
        if existing_email:
            logger.warning(f"邮箱已注册: {email}")
            return {
                'success': False,
                'message': '邮箱已被注册',
                'errors': ['该邮箱已被其他用户注册']
            }
        
        # 创建新用户
        logger.info("开始创建新用户账户")
        new_user = user_service.create_user(
            username=username,
            email=email,
            password=password,
            profile_data=profile_data or {}
        )
        
        # 发送确认邮件
        logger.info(f"为新用户发送确认邮件: user_id={new_user.id}")
        email_sent = email_service.send_registration_confirmation(
            email=email,
            username=username,
            confirmation_token=new_user.confirmation_token
        )
        
        if not email_sent:
            logger.warning(f"确认邮件发送失败: user_id={new_user.id}")
        
        # 注册成功
        logger.info(f"用户注册成功: user_id={new_user.id}, username={username}")
        return {
            'success': True,
            'message': '注册成功，请查收确认邮件',
            'user_id': new_user.id
        }
        
    except DatabaseError as e:
        # 数据库相关错误
        logger.error(f"数据库错误导致注册失败: {str(e)}")
        return {
            'success': False,
            'message': '系统暂时不可用，请稍后重试',
            'errors': ['数据库连接异常']
        }
        
    except EmailError as e:
        # 邮件发送错误（但用户已创建成功）
        logger.error(f"用户创建成功但邮件发送失败: user_id={new_user.id}, error={str(e)}")
        return {
            'success': True,
            'message': '注册成功，但确认邮件发送失败，请联系客服',
            'user_id': new_user.id
        }
        
    except Exception as e:
        # 其他未预期的错误
        logger.error(f"用户注册过程中发生未知错误: {str(e)}")
        return {
            'success': False,
            'message': '注册失败，请稍后重试',
            'errors': ['系统内部错误']
        }
```

### 类定义规范
```python
class UserAuthenticationService:
    """
    用户认证服务类
    
    提供用户登录、登出、权限验证等认证相关功能。
    支持多种认证方式：用户名密码、邮箱密码、第三方登录。
    
    Attributes:
        _db_manager (DatabaseManager): 数据库管理器实例
        _token_manager (TokenManager): JWT令牌管理器
        _password_manager (PasswordManager): 密码加密管理器
        _session_timeout (int): 会话超时时间（秒）
        
    Example:
        >>> auth_service = UserAuthenticationService()
        >>> result = auth_service.login("john_doe", "password123")
        >>> if result['success']:
        ...     token = result['access_token']
    """
    
    def __init__(self, 
                 db_manager: DatabaseManager, 
                 session_timeout: int = 3600):
        """
        初始化用户认证服务
        
        Args:
            db_manager (DatabaseManager): 数据库管理器实例
            session_timeout (int): 会话超时时间（秒），默认1小时
        """
        # 记录服务初始化
        logger.info("初始化用户认证服务")
        
        # 注入依赖
        self._db_manager = db_manager
        self._token_manager = TokenManager()
        self._password_manager = PasswordManager()
        
        # 配置参数
        self._session_timeout = session_timeout
        self._max_login_attempts = 5
        self._lockout_duration = 900  # 15分钟锁定时间
        
        logger.info(f"认证服务初始化完成: session_timeout={session_timeout}")
    
    def authenticate_user(self, 
                         login_identifier: str, 
                         password: str,
                         remember_me: bool = False) -> Dict[str, Union[bool, str, int]]:
        """
        用户身份认证
        
        支持使用用户名或邮箱进行登录认证。
        包含防暴力破解机制，多次失败后会锁定账户。
        
        Args:
            login_identifier (str): 登录标识符（用户名或邮箱）
            password (str): 用户密码
            remember_me (bool): 是否记住登录状态，影响token有效期
            
        Returns:
            Dict[str, Union[bool, str, int]]: 认证结果
                - success (bool): 认证是否成功
                - access_token (str): 访问令牌（成功时）
                - user_id (int): 用户ID（成功时）
                - message (str): 结果消息
                - locked_until (int): 锁定到期时间戳（账户被锁时）
        """
        # 记录认证尝试
        logger.info(f"用户认证尝试: identifier={login_identifier}")
        
        # 输入验证
        if not login_identifier or not password:
            logger.warning("认证失败: 用户名或密码为空")
            return {
                'success': False,
                'message': '用户名和密码不能为空'
            }
        
        try:
            # 查找用户（支持用户名或邮箱登录）
            user = self._find_user_by_identifier(login_identifier)
            if not user:
                logger.warning(f"认证失败: 用户不存在, identifier={login_identifier}")
                return {
                    'success': False,
                    'message': '用户名或密码错误'
                }
            
            # 检查账户是否被锁定
            if self._is_account_locked(user.id):
                locked_until = self._get_account_lock_time(user.id)
                logger.warning(f"认证失败: 账户被锁定, user_id={user.id}")
                return {
                    'success': False,
                    'message': '账户已被锁定，请稍后重试',
                    'locked_until': locked_until
                }
            
            # 验证密码
            if self._password_manager.verify_password(password, user.password_hash):
                # 密码正确，重置失败计数
                self._reset_login_attempts(user.id)
                
                # 生成访问令牌
                token_expires = self._session_timeout * (24 if remember_me else 1)
                access_token = self._token_manager.generate_token(
                    user_id=user.id,
                    expires_in=token_expires
                )
                
                # 更新最后登录时间
                self._update_last_login(user.id)
                
                logger.info(f"用户认证成功: user_id={user.id}")
                return {
                    'success': True,
                    'access_token': access_token,
                    'user_id': user.id,
                    'message': '登录成功'
                }
            else:
                # 密码错误，记录失败尝试
                attempts = self._record_failed_attempt(user.id)
                logger.warning(f"认证失败: 密码错误, user_id={user.id}, attempts={attempts}")
                
                # 检查是否需要锁定账户
                if attempts >= self._max_login_attempts:
                    self._lock_account(user.id)
                    logger.warning(f"账户已被锁定: user_id={user.id}")
                    return {
                        'success': False,
                        'message': f'密码错误次数过多，账户已被锁定{self._lockout_duration//60}分钟'
                    }
                
                remaining_attempts = self._max_login_attempts - attempts
                return {
                    'success': False,
                    'message': f'用户名或密码错误，还有{remaining_attempts}次尝试机会'
                }
                
        except Exception as e:
            logger.error(f"认证过程中发生错误: {str(e)}")
            return {
                'success': False,
                'message': '认证服务暂时不可用'
            }
    
    def _find_user_by_identifier(self, identifier: str) -> Optional[User]:
        """
        根据标识符查找用户（私有方法）
        
        支持使用用户名或邮箱查找用户
        
        Args:
            identifier (str): 用户名或邮箱
            
        Returns:
            Optional[User]: 用户对象或None
        """
        # 判断标识符类型并查找用户
        if '@' in identifier:
            # 邮箱格式
            return self._db_manager.get_user_by_email(identifier)
        else:
            # 用户名格式
            return self._db_manager.get_user_by_username(identifier)
```

## 🔧 导入规范

### 导入顺序
```python
# 1. 标准库导入
import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

# 2. 第三方库导入
import bcrypt
import jwt
import requests
from sqlalchemy import create_engine
from flask import Flask, request, jsonify

# 3. 项目内部导入
from config.settings import get_config
from utils.logger import get_logger
from utils.validators import validate_email
from models.user_model import User
from services.email_service import EmailService
```

### 导入别名规范
```python
# ✅ 推荐做法：使用清晰的别名
import pandas as pd
import numpy as np
from datetime import datetime as dt

# ❌ 避免做法：使用不清晰的别名
import pandas as p
import numpy as n
```

## 💬 注释规范

### 文档字符串（Docstring）
所有的模块、类、函数都必须有详细的文档字符串，使用Google风格：

```python
def calculate_compound_interest(
    principal: float, 
    rate: float, 
    time: int, 
    compound_frequency: int = 12
) -> float:
    """
    计算复利
    
    根据本金、利率、时间和复利频次计算最终金额。
    
    Args:
        principal (float): 本金金额，必须大于0
        rate (float): 年利率，以小数形式表示（如0.05表示5%）
        time (int): 投资时间，以年为单位
        compound_frequency (int, optional): 每年复利次数，默认为12（月复利）
        
    Returns:
        float: 计算后的最终金额
        
    Raises:
        ValueError: 当本金小于等于0或利率为负数时
        
    Example:
        >>> amount = calculate_compound_interest(1000, 0.05, 2, 12)
        >>> print(f"最终金额: {amount:.2f}")
        最终金额: 1104.89
    """
```

### 行内注释
```python
# ✅ 推荐做法：解释为什么这样做
user_age = current_year - birth_year  # 计算用户年龄用于权限判断

# 使用二分查找算法提高性能，数据量大时效果明显
result = binary_search(sorted_list, target_value)

# ❌ 避免做法：重复代码内容
user_age = current_year - birth_year  # 用当前年份减去出生年份
```

## 🚨 错误处理规范

### 异常处理层次
```python
# 具体异常处理 → 通用异常处理 → 记录日志
try:
    # 执行可能出错的操作
    result = risky_operation()
    
except ConnectionError as e:
    # 处理连接错误
    logger.error(f"连接错误: {str(e)}")
    raise ServiceUnavailableError("服务暂时不可用")
    
except TimeoutError as e:
    # 处理超时错误
    logger.error(f"操作超时: {str(e)}")
    raise RequestTimeoutError("请求超时，请重试")
    
except ValueError as e:
    # 处理数值错误
    logger.error(f"数值错误: {str(e)}")
    raise InvalidParameterError("参数格式不正确")
    
except Exception as e:
    # 处理其他未知错误
    logger.error(f"未知错误: {str(e)}")
    raise SystemError("系统内部错误")
```

### 自定义异常
```python
class ProjectBaseException(Exception):
    """项目基础异常类"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class AuthenticationError(ProjectBaseException):
    """认证失败异常"""
    def __init__(self, message: str = "认证失败"):
        super().__init__(message, "AUTH_001")

class ValidationError(ProjectBaseException):
    """数据验证异常"""
    def __init__(self, message: str = "数据验证失败"):
        super().__init__(message, "VALID_001")
```

## 📊 性能优化规范

### 数据库查询优化
```python
# ✅ 推荐做法：批量操作和预编译查询
def get_users_by_ids(user_ids: List[int]) -> List[User]:
    """批量获取用户信息，避免N+1查询问题"""
    if not user_ids:
        return []
    
    # 使用IN查询批量获取
    query = """
        SELECT id, username, email, created_at 
        FROM users 
        WHERE id IN ({})
    """.format(','.join(['%s'] * len(user_ids)))
    
    return db.execute(query, user_ids).fetchall()

# ❌ 避免做法：循环执行单个查询
def get_users_by_ids_bad(user_ids: List[int]) -> List[User]:
    users = []
    for user_id in user_ids:
        user = db.execute("SELECT * FROM users WHERE id = %s", [user_id])
        users.append(user)
    return users
```

### 内存使用优化
```python
# ✅ 推荐做法：使用生成器处理大数据
def process_large_dataset(file_path: str):
    """使用生成器处理大文件，避免内存溢出"""
    def read_lines():
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                yield line.strip()
    
    for line in read_lines():
        process_single_line(line)

# ❌ 避免做法：一次性加载所有数据
def process_large_dataset_bad(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        all_lines = file.readlines()  # 可能导致内存不足
    
    for line in all_lines:
        process_single_line(line)
```

## ✅ 代码检查清单

### 代码提交前检查
- [ ] 所有函数都有详细的文档字符串
- [ ] 变量和函数命名符合规范
- [ ] 添加了适当的类型提示
- [ ] 包含完整的错误处理
- [ ] 添加了必要的日志记录
- [ ] 敏感信息没有硬编码
- [ ] 遵循PEP8代码风格
- [ ] 添加了必要的单元测试

### 性能检查
- [ ] 避免了N+1查询问题
- [ ] 大数据处理使用了生成器
- [ ] 数据库连接有正确的管理
- [ ] 避免了不必要的循环嵌套
- [ ] 使用了合适的数据结构

### 安全检查
- [ ] 所有用户输入都经过验证
- [ ] SQL查询使用了参数化语句
- [ ] 密码等敏感信息经过加密
- [ ] 没有SQL注入漏洞
- [ ] 没有XSS漏洞

---

**遵循这些规范，让代码更加专业、安全、高效！** 