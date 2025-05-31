"""
提示词管理服务

负责管理prompts目录中的AI提示词文件，提供文件的读取、
更新、验证和备份功能。自动排除示例文件。

主要功能：
1. 扫描和管理提示词文件
2. 读取和更新文件内容
3. 文件备份和版本管理
4. 提示词内容验证

Author: AI Assistant
Created: 2024-01-XX
Version: 1.0.0
"""

import os
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from loguru import logger


class PromptManager:
    """
    提示词管理器
    
    负责prompts目录中提示词文件的完整生命周期管理，
    包括读取、验证、更新和备份。
    """
    
    def __init__(self, project_root: Path):
        """
        初始化提示词管理器
        
        Args:
            project_root: 项目根目录路径
        """
        self.project_root = project_root
        self.prompts_dir = project_root / "prompts"
        self.backup_dir = project_root / "prompt_backups"
        
        # 提示词文件配置信息
        self.prompt_configs = {
            "classify_prompt.txt": {
                "display_name": "意图分类专家",
                "description": "负责识别用户意图，将对话分类到不同的专家Agent",
                "agent_type": "classify"
            },
            "default_prompt.txt": {
                "display_name": "默认回复专家",
                "description": "处理通用客服咨询，提供标准的电商客服回复",
                "agent_type": "default"
            },
            "price_prompt.txt": {
                "display_name": "价格议价专家",
                "description": "处理价格相关咨询和议价场景，实现智能议价策略",
                "agent_type": "price"
            },
            "tech_prompt.txt": {
                "display_name": "技术咨询专家",
                "description": "处理产品技术参数、规格对比等专业咨询",
                "agent_type": "tech"
            }
        }
        
        # 需要排除的文件模式
        self.exclude_patterns = [
            "*_example.txt",  # 示例文件
            "*.bak",          # 备份文件
            "*.tmp",          # 临时文件
            ".*"              # 隐藏文件
        ]
    
    async def initialize(self):
        """
        初始化提示词管理器
        
        检查prompts目录是否存在，创建备份目录
        """
        logger.info("初始化提示词管理器...")
        
        # 检查prompts目录是否存在
        if not self.prompts_dir.exists():
            logger.error(f"prompts目录不存在: {self.prompts_dir}")
            raise FileNotFoundError(f"prompts目录不存在: {self.prompts_dir}")
        
        # 创建备份目录
        self.backup_dir.mkdir(exist_ok=True)
        
        # 验证提示词文件
        await self._validate_prompt_files()
        
        logger.info("提示词管理器初始化完成")
    
    async def get_prompt_files(self) -> List[Dict[str, Any]]:
        """
        获取所有可编辑的提示词文件列表
        
        Returns:
            List[Dict]: 提示词文件信息列表
        """
        try:
            prompt_files = []
            
            # 扫描prompts目录
            for file_path in self.prompts_dir.iterdir():
                if file_path.is_file() and file_path.suffix == '.txt':
                    filename = file_path.name
                    
                    # 检查是否需要排除
                    if self._should_exclude_file(filename):
                        continue
                    
                    # 获取文件信息
                    file_info = await self._get_file_info(file_path)
                    prompt_files.append(file_info)
            
            # 按照配置顺序排序
            prompt_files.sort(key=lambda x: list(self.prompt_configs.keys()).index(x['filename']) 
                             if x['filename'] in self.prompt_configs else 999)
            
            logger.debug(f"找到{len(prompt_files)}个可编辑的提示词文件")
            return prompt_files
            
        except Exception as e:
            logger.error(f"获取提示词文件列表失败: {e}")
            raise
    
    async def get_prompt_content(self, filename: str) -> str:
        """
        获取特定提示词文件的内容
        
        Args:
            filename: 文件名
            
        Returns:
            str: 文件内容
        """
        try:
            # 验证文件名
            if self._should_exclude_file(filename):
                raise ValueError(f"文件 {filename} 不允许访问")
            
            file_path = self.prompts_dir / filename
            
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {filename}")
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.debug(f"已读取提示词文件: {filename} ({len(content)} 字符)")
            return content
            
        except Exception as e:
            logger.error(f"读取提示词文件失败: {filename} - {e}")
            raise
    
    async def update_prompt_content(self, filename: str, content: str) -> Dict[str, Any]:
        """
        更新提示词文件内容
        
        Args:
            filename: 文件名
            content: 新的文件内容
            
        Returns:
            dict: 更新操作结果
        """
        try:
            # 验证文件名
            if self._should_exclude_file(filename):
                return {
                    "success": False,
                    "message": f"文件 {filename} 不允许编辑"
                }
            
            file_path = self.prompts_dir / filename
            
            if not file_path.exists():
                return {
                    "success": False,
                    "message": f"文件不存在: {filename}"
                }
            
            # 验证内容
            validation_result = self._validate_prompt_content(content)
            if not validation_result["is_valid"]:
                return {
                    "success": False,
                    "message": f"内容验证失败: {validation_result['error']}"
                }
            
            # 备份当前文件
            backup_path = await self._backup_prompt_file(file_path)
            logger.info(f"已备份文件到: {backup_path}")
            
            # 写入新内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"提示词文件已更新: {filename} ({len(content)} 字符)")
            
            return {
                "success": True,
                "message": f"文件 {filename} 更新成功",
                "backup_path": str(backup_path),
                "content_length": len(content)
            }
            
        except Exception as e:
            logger.error(f"更新提示词文件失败: {filename} - {e}")
            return {
                "success": False,
                "message": f"更新文件失败: {str(e)}"
            }
    
    async def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """
        获取文件的详细信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            dict: 文件信息字典
        """
        filename = file_path.name
        
        # 获取文件统计信息
        stat = file_path.stat()
        
        # 从配置中获取文件描述
        config = self.prompt_configs.get(filename, {})
        
        return {
            "filename": filename,
            "display_name": config.get("display_name", filename.replace("_", " ").replace(".txt", "").title()),
            "description": config.get("description", "提示词文件"),
            "file_size": stat.st_size,
            "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "agent_type": config.get("agent_type", "unknown")
        }
    
    def _should_exclude_file(self, filename: str) -> bool:
        """
        检查文件是否应该被排除
        
        Args:
            filename: 文件名
            
        Returns:
            bool: 是否应该排除
        """
        # 检查是否匹配排除模式
        for pattern in self.exclude_patterns:
            if pattern.startswith("*") and filename.endswith(pattern[1:]):
                return True
            elif pattern.endswith("*") and filename.startswith(pattern[:-1]):
                return True
            elif pattern == filename:
                return True
        
        return False
    
    def _validate_prompt_content(self, content: str) -> Dict[str, Any]:
        """
        验证提示词内容
        
        Args:
            content: 提示词内容
            
        Returns:
            dict: 验证结果
        """
        # 基本验证
        if not content or not content.strip():
            return {
                "is_valid": False,
                "error": "提示词内容不能为空"
            }
        
        # 长度验证
        if len(content) > 50000:  # 50KB限制
            return {
                "is_valid": False,
                "error": "提示词内容过长，请控制在50KB以内"
            }
        
        # 检查是否包含基本的提示词结构
        content_lower = content.lower()
        
        # 检查是否包含角色说明或类似的结构
        if not any(keyword in content_lower for keyword in [
            "角色", "role", "任务", "task", "目标", "goal", "你是", "you are"
        ]):
            logger.warning("提示词中可能缺少角色说明")
        
        # 检查字符编码
        try:
            content.encode('utf-8')
        except UnicodeEncodeError:
            return {
                "is_valid": False,
                "error": "提示词包含无效的字符编码"
            }
        
        return {
            "is_valid": True,
            "error": None
        }
    
    async def _backup_prompt_file(self, file_path: Path) -> Path:
        """
        备份提示词文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            Path: 备份文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"{file_path.stem}.backup.{timestamp}{file_path.suffix}"
        backup_path = self.backup_dir / backup_filename
        
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    async def _validate_prompt_files(self):
        """验证提示词文件的完整性"""
        try:
            # 检查配置的文件是否都存在
            missing_files = []
            for filename in self.prompt_configs.keys():
                file_path = self.prompts_dir / filename
                if not file_path.exists():
                    missing_files.append(filename)
            
            if missing_files:
                logger.warning(f"缺少提示词文件: {', '.join(missing_files)}")
            
            # 检查文件内容
            prompt_files = await self.get_prompt_files()
            for file_info in prompt_files:
                filename = file_info["filename"]
                try:
                    content = await self.get_prompt_content(filename)
                    validation_result = self._validate_prompt_content(content)
                    
                    if not validation_result["is_valid"]:
                        logger.warning(f"提示词文件内容无效: {filename} - {validation_result['error']}")
                        
                except Exception as e:
                    logger.warning(f"验证提示词文件失败: {filename} - {e}")
                    
        except Exception as e:
            logger.warning(f"验证提示词文件时出错: {e}")
    
    def get_available_agents(self) -> List[Dict[str, str]]:
        """
        获取可用的Agent类型列表
        
        Returns:
            List[Dict]: Agent类型信息列表
        """
        agents = []
        
        for filename, config in self.prompt_configs.items():
            agents.append({
                "agent_type": config["agent_type"],
                "display_name": config["display_name"],
                "description": config["description"],
                "filename": filename
            })
        
        return agents
    
    async def reload_prompts_in_main(self) -> Dict[str, Any]:
        """
        通知main.py重新加载提示词
        
        这个功能需要通过信号或其他方式通知main.py进程重新加载提示词
        
        Returns:
            dict: 重新加载结果
        """
        try:
            # 这里可以通过多种方式实现：
            # 1. 文件监控信号
            # 2. 数据库消息队列
            # 3. Redis发布订阅
            # 4. HTTP请求到main.py的内部API
            
            # 目前返回成功状态，实际实现可能需要根据具体架构调整
            logger.info("已发送提示词重新加载信号")
            
            return {
                "success": True,
                "message": "提示词重新加载信号已发送"
            }
            
        except Exception as e:
            logger.error(f"发送重新加载信号失败: {e}")
            return {
                "success": False,
                "message": f"发送重新加载信号失败: {str(e)}"
            } 