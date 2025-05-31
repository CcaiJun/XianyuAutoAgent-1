"""
API数据模型定义

定义Web管理界面API的所有请求和响应数据结构，
使用Pydantic进行数据验证和序列化。

包含的模型：
- 进程状态相关模型
- 配置管理相关模型
- 提示词管理相关模型
- 日志相关模型

Author: AI Assistant
Created: 2024-01-XX
Version: 1.0.0
"""

from datetime import datetime
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field, validator


# ======================= 进程管理相关模型 =======================

class ProcessStatusResponse(BaseModel):
    """
    进程状态响应模型
    
    用于返回main.py进程的详细状态信息
    """
    is_running: bool = Field(..., description="进程是否正在运行")
    pid: Optional[int] = Field(None, description="进程ID，如果进程未运行则为None")
    start_time: Optional[str] = Field(None, description="进程启动时间，ISO格式字符串")
    cpu_percent: Optional[float] = Field(None, description="CPU使用率百分比")
    memory_percent: Optional[float] = Field(None, description="内存使用率百分比")
    status: str = Field(..., description="进程状态描述")
    uptime: Optional[str] = Field(None, description="运行时长描述")
    
    class Config:
        """Pydantic配置"""
        schema_extra = {
            "example": {
                "is_running": True,
                "pid": 12345,
                "start_time": "2024-01-20T10:30:00",
                "cpu_percent": 2.5,
                "memory_percent": 1.8,
                "status": "运行中",
                "uptime": "2小时15分钟"
            }
        }


class ProcessOperationResult(BaseModel):
    """
    进程操作结果模型
    
    用于返回启动、停止、重启等操作的结果
    """
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="操作结果描述信息")
    pid: Optional[int] = Field(None, description="操作后的进程ID")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="操作时间")
    
    class Config:
        """Pydantic配置"""
        schema_extra = {
            "example": {
                "success": True,
                "message": "进程启动成功",
                "pid": 12345,
                "timestamp": "2024-01-20T10:30:00"
            }
        }


# ======================= 配置管理相关模型 =======================

class ConfigItem(BaseModel):
    """
    配置项模型
    
    表示.env文件中的单个配置项
    """
    key: str = Field(..., description="配置项键名")
    value: str = Field(..., description="配置项值")
    description: Optional[str] = Field(None, description="配置项说明")
    is_required: bool = Field(False, description="是否为必需配置项")
    is_sensitive: bool = Field(False, description="是否为敏感信息")
    
    @validator('key')
    def validate_key(cls, v):
        """验证配置项键名格式"""
        if not v or not v.strip():
            raise ValueError('配置项键名不能为空')
        return v.strip()
    
    class Config:
        """Pydantic配置"""
        schema_extra = {
            "example": {
                "key": "API_KEY",
                "value": "your-api-key-here",
                "description": "AI模型的API密钥",
                "is_required": True,
                "is_sensitive": True
            }
        }


class ConfigUpdateRequest(BaseModel):
    """
    配置更新请求模型
    
    用于批量更新多个配置项
    """
    configs: List[ConfigItem] = Field(..., description="要更新的配置项列表")
    
    @validator('configs')
    def validate_configs(cls, v):
        """验证配置项列表"""
        if not v:
            raise ValueError('配置项列表不能为空')
        
        # 检查是否有重复的键名
        keys = [config.key for config in v]
        if len(keys) != len(set(keys)):
            raise ValueError('配置项中存在重复的键名')
        
        return v
    
    class Config:
        """Pydantic配置"""
        schema_extra = {
            "example": {
                "configs": [
                    {
                        "key": "API_KEY",
                        "value": "new-api-key",
                        "description": "AI模型的API密钥",
                        "is_required": True,
                        "is_sensitive": True
                    },
                    {
                        "key": "MODEL_NAME",
                        "value": "gpt-4",
                        "description": "使用的AI模型名称",
                        "is_required": True,
                        "is_sensitive": False
                    }
                ]
            }
        }


# ======================= 提示词管理相关模型 =======================

class PromptFile(BaseModel):
    """
    提示词文件模型
    
    表示prompts目录中的单个提示词文件信息
    """
    filename: str = Field(..., description="文件名")
    display_name: str = Field(..., description="显示名称")
    description: str = Field(..., description="文件描述")
    file_size: int = Field(..., description="文件大小（字节）")
    last_modified: str = Field(..., description="最后修改时间")
    agent_type: str = Field(..., description="Agent类型")
    
    class Config:
        """Pydantic配置"""
        schema_extra = {
            "example": {
                "filename": "default_prompt.txt",
                "display_name": "默认回复专家",
                "description": "处理通用客服咨询的AI提示词",
                "file_size": 1024,
                "last_modified": "2024-01-20T10:30:00",
                "agent_type": "default"
            }
        }


class PromptUpdateRequest(BaseModel):
    """
    提示词更新请求模型
    
    用于更新提示词文件的内容
    """
    content: str = Field(..., description="新的文件内容")
    
    @validator('content')
    def validate_content(cls, v):
        """验证提示词内容"""
        if not v or not v.strip():
            raise ValueError('提示词内容不能为空')
        
        # 检查内容长度限制
        if len(v) > 50000:  # 50KB限制
            raise ValueError('提示词内容过长，请控制在50KB以内')
        
        return v
    
    class Config:
        """Pydantic配置"""
        schema_extra = {
            "example": {
                "content": "【角色说明】\n你是一位资深的电商卖家...\n\n【回复要求】\n..."
            }
        }


class PromptFileContent(BaseModel):
    """
    提示词文件内容模型
    
    用于返回提示词文件的完整内容
    """
    filename: str = Field(..., description="文件名")
    content: str = Field(..., description="文件内容")
    file_info: PromptFile = Field(..., description="文件信息")
    
    class Config:
        """Pydantic配置"""
        schema_extra = {
            "example": {
                "filename": "default_prompt.txt",
                "content": "【角色说明】\n你是一位资深的电商卖家...",
                "file_info": {
                    "filename": "default_prompt.txt",
                    "display_name": "默认回复专家",
                    "description": "处理通用客服咨询的AI提示词",
                    "file_size": 1024,
                    "last_modified": "2024-01-20T10:30:00",
                    "agent_type": "default"
                }
            }
        }


# ======================= 日志相关模型 =======================

class LogEntry(BaseModel):
    """
    日志条目模型
    
    表示单条日志记录的数据结构
    """
    timestamp: str = Field(..., description="时间戳")
    level: str = Field(..., description="日志级别")
    logger_name: str = Field(..., description="日志记录器名称")
    message: str = Field(..., description="日志消息")
    module: Optional[str] = Field(None, description="模块名")
    function: Optional[str] = Field(None, description="函数名")
    line: Optional[int] = Field(None, description="行号")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="额外数据")
    
    class Config:
        """Pydantic配置"""
        schema_extra = {
            "example": {
                "timestamp": "2024-01-20T10:30:00.123456",
                "level": "INFO",
                "logger_name": "main",
                "message": "用户登录尝试开始: username=test_user",
                "module": "main",
                "function": "user_login_process",
                "line": 125,
                "extra_data": {"user_id": "12345"}
            }
        }


class LogFilter(BaseModel):
    """
    日志过滤器模型
    
    用于过滤和搜索日志条目
    """
    level: Optional[str] = Field(None, description="日志级别过滤")
    start_time: Optional[str] = Field(None, description="开始时间过滤")
    end_time: Optional[str] = Field(None, description="结束时间过滤")
    keyword: Optional[str] = Field(None, description="关键词搜索")
    module: Optional[str] = Field(None, description="模块名过滤")
    limit: int = Field(100, description="返回条目数限制", ge=1, le=1000)
    
    class Config:
        """Pydantic配置"""
        schema_extra = {
            "example": {
                "level": "ERROR",
                "start_time": "2024-01-20T00:00:00",
                "end_time": "2024-01-20T23:59:59",
                "keyword": "用户登录",
                "module": "main",
                "limit": 50
            }
        }


# ======================= 通用响应模型 =======================

class ApiResponse(BaseModel):
    """
    通用API响应模型
    
    标准化的API响应格式
    """
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="响应时间")
    
    class Config:
        """Pydantic配置"""
        schema_extra = {
            "example": {
                "success": True,
                "message": "操作成功",
                "data": {"key": "value"},
                "timestamp": "2024-01-20T10:30:00"
            }
        }


class ErrorResponse(BaseModel):
    """
    错误响应模型
    
    标准化的错误响应格式
    """
    success: bool = Field(False, description="操作是否成功")
    error_code: str = Field(..., description="错误代码")
    error_message: str = Field(..., description="错误消息")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="错误时间")
    
    class Config:
        """Pydantic配置"""
        schema_extra = {
            "example": {
                "success": False,
                "error_code": "PROCESS_START_FAILED",
                "error_message": "进程启动失败",
                "details": {"reason": "端口已被占用"},
                "timestamp": "2024-01-20T10:30:00"
            }
        }


# ======================= 系统信息相关模型 =======================

class SystemInfo(BaseModel):
    """
    系统信息模型
    
    返回系统运行状态和资源使用情况
    """
    cpu_count: int = Field(..., description="CPU核心数")
    cpu_percent: float = Field(..., description="CPU使用率")
    memory_total: int = Field(..., description="总内存大小（字节）")
    memory_available: int = Field(..., description="可用内存大小（字节）")
    memory_percent: float = Field(..., description="内存使用率")
    disk_total: int = Field(..., description="磁盘总大小（字节）")
    disk_used: int = Field(..., description="磁盘已用大小（字节）")
    disk_percent: float = Field(..., description="磁盘使用率")
    uptime: str = Field(..., description="系统运行时间")
    python_version: str = Field(..., description="Python版本")
    
    class Config:
        """Pydantic配置"""
        schema_extra = {
            "example": {
                "cpu_count": 8,
                "cpu_percent": 25.5,
                "memory_total": 16777216000,
                "memory_available": 8388608000,
                "memory_percent": 50.0,
                "disk_total": 1000000000000,
                "disk_used": 500000000000,
                "disk_percent": 50.0,
                "uptime": "2天3小时45分钟",
                "python_version": "3.9.7"
            }
        } 