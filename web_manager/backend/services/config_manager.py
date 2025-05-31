"""
配置管理服务

负责管理.env文件中的环境变量配置，提供配置的读取、
更新、验证和备份功能。

主要功能：
1. 读取和解析.env文件
2. 更新和保存配置项
3. 配置项验证和类型检查
4. 配置备份和恢复

Author: AI Assistant
Created: 2024-01-XX
Version: 1.0.0
"""

import os
import re
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from loguru import logger


class ConfigManager:
    """
    配置管理器
    
    负责.env文件的完整生命周期管理，包括读取、验证、
    更新和备份配置项。
    """
    
    def __init__(self, project_root: Path):
        """
        初始化配置管理器
        
        Args:
            project_root: 项目根目录路径
        """
        self.project_root = project_root
        self.env_file_path = project_root / ".env"
        self.backup_dir = project_root / "config_backups"
        
        # 配置项描述和验证规则
        self.config_definitions = {
            "API_KEY": {
                "description": "AI模型的API密钥",
                "is_required": True,
                "is_sensitive": True,
                "validator": self._validate_api_key
            },
            "MODEL_BASE_URL": {
                "description": "AI模型的基础URL地址",
                "is_required": False,
                "is_sensitive": False,
                "validator": self._validate_url,
                "default": "https://dashscope.aliyuncs.com/compatible-mode/v1"
            },
            "MODEL_NAME": {
                "description": "使用的AI模型名称",
                "is_required": False,
                "is_sensitive": False,
                "validator": self._validate_model_name,
                "default": "qwen-turbo"
            },
            "COOKIES_STR": {
                "description": "闲鱼网站的Cookie字符串",
                "is_required": True,
                "is_sensitive": True,
                "validator": self._validate_cookies
            },
            "HEARTBEAT_INTERVAL": {
                "description": "心跳检测间隔（秒）",
                "is_required": False,
                "is_sensitive": False,
                "validator": self._validate_positive_integer,
                "default": "15"
            },
            "HEARTBEAT_TIMEOUT": {
                "description": "心跳超时时间（秒）",
                "is_required": False,
                "is_sensitive": False,
                "validator": self._validate_positive_integer,
                "default": "5"
            },
            "TOKEN_REFRESH_INTERVAL": {
                "description": "Token刷新间隔（秒）",
                "is_required": False,
                "is_sensitive": False,
                "validator": self._validate_positive_integer,
                "default": "3600"
            },
            "TOKEN_RETRY_INTERVAL": {
                "description": "Token重试间隔（秒）",
                "is_required": False,
                "is_sensitive": False,
                "validator": self._validate_positive_integer,
                "default": "300"
            },
            "MANUAL_MODE_TIMEOUT": {
                "description": "人工接管模式超时时间（秒）",
                "is_required": False,
                "is_sensitive": False,
                "validator": self._validate_positive_integer,
                "default": "3600"
            },
            "MESSAGE_EXPIRE_TIME": {
                "description": "消息过期时间（毫秒）",
                "is_required": False,
                "is_sensitive": False,
                "validator": self._validate_positive_integer,
                "default": "300000"
            },
            "TOGGLE_KEYWORDS": {
                "description": "人工接管切换关键词",
                "is_required": False,
                "is_sensitive": False,
                "validator": self._validate_toggle_keywords,
                "default": "。"
            }
        }
    
    async def initialize(self):
        """
        初始化配置管理器
        
        检查.env文件是否存在，创建备份目录
        """
        logger.info("初始化配置管理器...")
        
        # 检查.env文件是否存在
        if not self.env_file_path.exists():
            logger.warning(f".env文件不存在: {self.env_file_path}")
            # 创建一个基础的.env文件模板
            await self._create_default_env_file()
        
        # 创建备份目录
        self.backup_dir.mkdir(exist_ok=True)
        
        # 验证现有配置
        await self._validate_existing_config()
        
        logger.info("配置管理器初始化完成")
    
    async def get_config(self) -> List[Dict[str, Any]]:
        """
        获取所有配置项
        
        Returns:
            List[Dict]: 配置项列表，每个配置项包含键、值、描述等信息
        """
        try:
            config_items = []
            
            # 读取.env文件
            env_content = await self._read_env_file()
            current_config = self._parse_env_content(env_content)
            
            # 处理每个已定义的配置项
            for key, definition in self.config_definitions.items():
                value = current_config.get(key, "")
                
                # 如果配置项不存在且有默认值，使用默认值
                if not value and "default" in definition:
                    value = definition["default"]
                
                config_item = {
                    "key": key,
                    "value": value,
                    "description": definition["description"],
                    "is_required": definition["is_required"],
                    "is_sensitive": definition["is_sensitive"]
                }
                
                config_items.append(config_item)
            
            # 处理未定义的配置项（可能是用户自定义的）
            for key, value in current_config.items():
                if key not in self.config_definitions:
                    config_item = {
                        "key": key,
                        "value": value,
                        "description": "用户自定义配置项",
                        "is_required": False,
                        "is_sensitive": False
                    }
                    config_items.append(config_item)
            
            logger.debug(f"获取到{len(config_items)}个配置项")
            return config_items
            
        except Exception as e:
            logger.error(f"获取配置失败: {e}")
            raise
    
    async def update_config(self, configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        更新配置项
        
        Args:
            configs: 要更新的配置项列表
            
        Returns:
            dict: 更新操作结果
        """
        try:
            logger.info(f"准备更新{len(configs)}个配置项")
            
            # 验证配置项
            validation_errors = []
            for config in configs:
                key = config["key"]
                value = config["value"]
                
                # 如果有验证器，进行验证
                if key in self.config_definitions:
                    definition = self.config_definitions[key]
                    if "validator" in definition:
                        is_valid, error_msg = definition["validator"](value)
                        if not is_valid:
                            validation_errors.append(f"{key}: {error_msg}")
            
            if validation_errors:
                return {
                    "success": False,
                    "message": "配置验证失败",
                    "errors": validation_errors
                }
            
            # 备份当前配置
            backup_path = await self._backup_env_file()
            logger.info(f"已备份当前配置到: {backup_path}")
            
            # 读取当前.env文件
            env_content = await self._read_env_file()
            current_config = self._parse_env_content(env_content)
            
            # 更新配置项
            updated_count = 0
            for config in configs:
                key = config["key"]
                new_value = config["value"]
                old_value = current_config.get(key, "")
                
                if old_value != new_value:
                    current_config[key] = new_value
                    updated_count += 1
                    
                    # 记录配置变更（敏感信息不记录具体值）
                    if key in self.config_definitions and self.config_definitions[key]["is_sensitive"]:
                        logger.info(f"配置项已更新: {key} = [敏感信息已隐藏]")
                    else:
                        logger.info(f"配置项已更新: {key} = {new_value}")
            
            # 生成新的.env文件内容
            new_env_content = self._generate_env_content(current_config)
            
            # 写入.env文件
            await self._write_env_file(new_env_content)
            
            logger.info(f"配置更新完成，共更新{updated_count}个配置项")
            
            return {
                "success": True,
                "message": f"配置更新成功，共更新{updated_count}个配置项",
                "updated_count": updated_count,
                "backup_path": str(backup_path)
            }
            
        except Exception as e:
            logger.error(f"更新配置失败: {e}")
            return {
                "success": False,
                "message": f"更新配置失败: {str(e)}"
            }
    
    async def _read_env_file(self) -> str:
        """
        读取.env文件内容
        
        Returns:
            str: .env文件的内容
        """
        try:
            with open(self.env_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"读取.env文件失败: {e}")
            raise
    
    async def _write_env_file(self, content: str):
        """
        写入.env文件内容
        
        Args:
            content: 要写入的内容
        """
        try:
            with open(self.env_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            logger.error(f"写入.env文件失败: {e}")
            raise
    
    def _parse_env_content(self, content: str) -> Dict[str, str]:
        """
        解析.env文件内容
        
        Args:
            content: .env文件内容
            
        Returns:
            dict: 解析后的配置字典
        """
        config = {}
        
        for line in content.split('\n'):
            line = line.strip()
            
            # 跳过空行和注释行
            if not line or line.startswith('#'):
                continue
            
            # 解析键值对
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # 移除值周围的引号
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                
                config[key] = value
        
        return config
    
    def _generate_env_content(self, config: Dict[str, str]) -> str:
        """
        生成.env文件内容
        
        Args:
            config: 配置字典
            
        Returns:
            str: 生成的.env文件内容
        """
        lines = []
        lines.append("# XianyuAutoAgent 配置文件")
        lines.append(f"# 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # 按照定义顺序输出已定义的配置项
        for key, definition in self.config_definitions.items():
            value = config.get(key, "")
            
            # 添加配置项说明
            lines.append(f"# {definition['description']}")
            if definition['is_required']:
                lines.append("# 必需配置项")
            
            # 添加配置项
            if value:
                lines.append(f"{key}={value}")
            else:
                lines.append(f"# {key}=")
            lines.append("")
        
        # 输出未定义的配置项
        undefined_items = []
        for key, value in config.items():
            if key not in self.config_definitions:
                undefined_items.append(f"{key}={value}")
        
        if undefined_items:
            lines.append("# 用户自定义配置项")
            lines.extend(undefined_items)
            lines.append("")
        
        return '\n'.join(lines)
    
    async def _backup_env_file(self) -> Path:
        """
        备份当前.env文件
        
        Returns:
            Path: 备份文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f".env.backup.{timestamp}"
        backup_path = self.backup_dir / backup_filename
        
        shutil.copy2(self.env_file_path, backup_path)
        return backup_path
    
    async def _create_default_env_file(self):
        """创建默认的.env文件模板"""
        logger.info("创建默认.env文件模板")
        
        default_config = {}
        
        # 添加有默认值的配置项
        for key, definition in self.config_definitions.items():
            if "default" in definition:
                default_config[key] = definition["default"]
            elif definition["is_required"]:
                default_config[key] = ""  # 必需配置项留空
        
        content = self._generate_env_content(default_config)
        await self._write_env_file(content)
        
        logger.info(f"默认.env文件已创建: {self.env_file_path}")
    
    async def _validate_existing_config(self):
        """验证现有配置的完整性"""
        try:
            config_items = await self.get_config()
            
            missing_required = []
            invalid_configs = []
            
            for item in config_items:
                key = item["key"]
                value = item["value"]
                
                # 检查必需配置项
                if item["is_required"] and not value:
                    missing_required.append(key)
                
                # 验证配置项格式
                if key in self.config_definitions and value:
                    definition = self.config_definitions[key]
                    if "validator" in definition:
                        is_valid, error_msg = definition["validator"](value)
                        if not is_valid:
                            invalid_configs.append(f"{key}: {error_msg}")
            
            if missing_required:
                logger.warning(f"缺少必需配置项: {', '.join(missing_required)}")
            
            if invalid_configs:
                logger.warning(f"配置项格式错误: {'; '.join(invalid_configs)}")
                
        except Exception as e:
            logger.warning(f"验证现有配置时出错: {e}")
    
    # ======================= 配置项验证器 =======================
    
    def _validate_api_key(self, value: str) -> Tuple[bool, str]:
        """验证API密钥格式"""
        if not value:
            return False, "API密钥不能为空"
        if len(value) < 10:
            return False, "API密钥长度不能少于10个字符"
        return True, ""
    
    def _validate_url(self, value: str) -> Tuple[bool, str]:
        """验证URL格式"""
        if not value:
            return True, ""  # URL不是必需的
        
        url_pattern = re.compile(
            r'^https?://'  # http:// 或 https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # 域名
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP地址
            r'(?::\d+)?'  # 可选端口号
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(value):
            return False, "URL格式无效"
        return True, ""
    
    def _validate_model_name(self, value: str) -> Tuple[bool, str]:
        """验证模型名称格式"""
        if not value:
            return True, ""  # 模型名称不是必需的
        
        # 简单的模型名称格式检查
        if not re.match(r'^[a-zA-Z0-9._-]+$', value):
            return False, "模型名称只能包含字母、数字、点、下划线和连字符"
        return True, ""
    
    def _validate_cookies(self, value: str) -> Tuple[bool, str]:
        """验证Cookie字符串格式"""
        if not value:
            return False, "Cookie字符串不能为空"
        
        # 检查Cookie格式（简单验证）
        if '=' not in value:
            return False, "Cookie格式无效，应包含键值对"
        
        # 检查必要的Cookie字段
        required_cookies = ['unb', '_m_h5_tk']
        for cookie_name in required_cookies:
            if cookie_name not in value:
                return False, f"Cookie中缺少必要字段: {cookie_name}"
        
        return True, ""
    
    def _validate_positive_integer(self, value: str) -> Tuple[bool, str]:
        """验证正整数"""
        if not value:
            return True, ""  # 可以为空，会使用默认值
        
        try:
            num = int(value)
            if num <= 0:
                return False, "必须是正整数"
            return True, ""
        except ValueError:
            return False, "必须是有效的整数"
    
    def _validate_toggle_keywords(self, value: str) -> Tuple[bool, str]:
        """验证切换关键词"""
        if not value:
            return False, "切换关键词不能为空"
        
        # 关键词长度限制
        if len(value) > 10:
            return False, "切换关键词长度不能超过10个字符"
        
        return True, "" 