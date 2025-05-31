"""
日志监控服务

负责监控main.py进程的实时日志输出，解析日志内容，
并通过WebSocket向前端推送日志信息。

主要功能：
1. 实时监控main.py的标准输出
2. 解析和格式化日志内容
3. 通过WebSocket推送日志到前端
4. 日志过滤和搜索功能

Author: AI Assistant
Created: 2024-01-XX
Version: 1.0.0
"""

import asyncio
import re
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from loguru import logger


class LogMonitor:
    """
    日志监控器
    
    负责监控main.py进程的日志输出，解析日志内容，
    并实时推送到Web界面。
    """
    
    def __init__(self, project_root: Path):
        """
        初始化日志监控器
        
        Args:
            project_root: 项目根目录路径
        """
        self.project_root = project_root
        self.log_file_path = project_root / "logs" / "app.log"
        
        # 监控相关状态
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self.log_callback: Optional[Callable] = None
        
        # 日志解析正则表达式
        self.log_patterns = {
            # Loguru日志格式: 2024-01-20 10:30:00.123 | INFO | module:function:line - message
            'loguru': re.compile(
                r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\s*\|\s*'
                r'(?P<level>\w+)\s*\|\s*'
                r'(?P<module>\w+):(?P<function>\w+):(?P<line>\d+)\s*-\s*'
                r'(?P<message>.*)'
            ),
            # 标准Python日志格式
            'standard': re.compile(
                r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})\s*'
                r'(?P<level>\w+)\s*'
                r'(?P<logger>\w+)\s*'
                r'(?P<message>.*)'
            ),
            # 简单日志格式
            'simple': re.compile(
                r'(?P<level>INFO|DEBUG|WARNING|ERROR|CRITICAL):\s*'
                r'(?P<message>.*)'
            )
        }
        
        # 日志缓存
        self.log_buffer: List[Dict[str, Any]] = []
        self.max_buffer_size = 1000
        
        # 监控配置
        self.tail_lines = 100  # 启动时读取的历史日志行数
        
    async def initialize(self):
        """
        初始化日志监控器
        
        创建日志目录，检查日志文件
        """
        logger.info("初始化日志监控器...")
        
        # 创建日志目录
        log_dir = self.log_file_path.parent
        log_dir.mkdir(exist_ok=True)
        
        # 初始化日志缓存
        await self._load_recent_logs()
        
        logger.info("日志监控器初始化完成")
    
    async def start_monitoring(self, log_callback: Callable):
        """
        开始监控日志
        
        Args:
            log_callback: 日志回调函数，用于推送日志到WebSocket
        """
        if self.is_monitoring:
            logger.warning("日志监控已在运行")
            return
        
        self.log_callback = log_callback
        self.is_monitoring = True
        
        # 启动监控任务
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info("日志监控已启动")
    
    async def stop_monitoring(self):
        """停止日志监控"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.log_callback = None
        logger.info("日志监控已停止")
    
    async def _monitoring_loop(self):
        """
        日志监控主循环
        
        持续监控日志文件的变化，解析新增的日志行
        """
        last_position = 0
        
        # 如果日志文件存在，获取当前文件大小
        if self.log_file_path.exists():
            last_position = self.log_file_path.stat().st_size
        
        while self.is_monitoring:
            try:
                # 检查日志文件是否存在
                if not self.log_file_path.exists():
                    await asyncio.sleep(1)
                    continue
                
                # 检查文件大小变化
                current_size = self.log_file_path.stat().st_size
                
                if current_size > last_position:
                    # 读取新增内容
                    new_content = await self._read_new_content(last_position, current_size)
                    
                    if new_content:
                        # 解析新日志行
                        new_logs = self._parse_log_content(new_content)
                        
                        # 处理新日志
                        for log_entry in new_logs:
                            await self._process_log_entry(log_entry)
                    
                    last_position = current_size
                
                elif current_size < last_position:
                    # 文件被截断或重新创建
                    logger.info("检测到日志文件被重置")
                    last_position = 0
                
                # 等待下次检查
                await asyncio.sleep(0.5)  # 500毫秒检查一次
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"日志监控循环出错: {e}")
                await asyncio.sleep(1)
    
    async def _read_new_content(self, start_pos: int, end_pos: int) -> str:
        """
        读取文件中的新增内容
        
        Args:
            start_pos: 开始位置
            end_pos: 结束位置
            
        Returns:
            str: 新增的文件内容
        """
        try:
            with open(self.log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(start_pos)
                content = f.read(end_pos - start_pos)
                return content
        except Exception as e:
            logger.error(f"读取日志文件新增内容失败: {e}")
            return ""
    
    def _parse_log_content(self, content: str) -> List[Dict[str, Any]]:
        """
        解析日志内容
        
        Args:
            content: 原始日志内容
            
        Returns:
            List[Dict]: 解析后的日志条目列表
        """
        log_entries = []
        lines = content.strip().split('\n')
        
        for line in lines:
            if not line.strip():
                continue
            
            log_entry = self._parse_log_line(line)
            if log_entry:
                log_entries.append(log_entry)
        
        return log_entries
    
    def _parse_log_line(self, line: str) -> Optional[Dict[str, Any]]:
        """
        解析单行日志
        
        Args:
            line: 日志行内容
            
        Returns:
            Dict: 解析后的日志条目，如果解析失败返回None
        """
        # 尝试使用不同的正则表达式解析
        for pattern_name, pattern in self.log_patterns.items():
            match = pattern.match(line.strip())
            if match:
                groups = match.groupdict()
                
                # 统一化时间戳格式
                timestamp = self._normalize_timestamp(groups.get('timestamp', ''))
                
                # 构建日志条目
                log_entry = {
                    'timestamp': timestamp,
                    'level': groups.get('level', 'INFO'),
                    'logger_name': groups.get('module', groups.get('logger', 'main')),
                    'message': groups.get('message', '').strip(),
                    'module': groups.get('module', ''),
                    'function': groups.get('function', ''),
                    'line': int(groups.get('line', 0)) if groups.get('line') else None,
                    'raw_line': line,
                    'pattern_type': pattern_name
                }
                
                return log_entry
        
        # 如果无法解析，创建一个基本的日志条目
        return {
            'timestamp': datetime.now().isoformat(),
            'level': 'INFO',
            'logger_name': 'unknown',
            'message': line.strip(),
            'module': '',
            'function': '',
            'line': None,
            'raw_line': line,
            'pattern_type': 'unknown'
        }
    
    def _normalize_timestamp(self, timestamp_str: str) -> str:
        """
        标准化时间戳格式
        
        Args:
            timestamp_str: 原始时间戳字符串
            
        Returns:
            str: ISO格式的时间戳
        """
        if not timestamp_str:
            return datetime.now().isoformat()
        
        try:
            # 尝试解析不同格式的时间戳
            formats = [
                '%Y-%m-%d %H:%M:%S.%f',  # 2024-01-20 10:30:00.123456
                '%Y-%m-%d %H:%M:%S,%f',  # 2024-01-20 10:30:00,123
                '%Y-%m-%d %H:%M:%S',     # 2024-01-20 10:30:00
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(timestamp_str, fmt)
                    return dt.isoformat()
                except ValueError:
                    continue
            
            # 如果所有格式都失败，返回当前时间
            return datetime.now().isoformat()
            
        except Exception:
            return datetime.now().isoformat()
    
    async def _process_log_entry(self, log_entry: Dict[str, Any]):
        """
        处理日志条目
        
        Args:
            log_entry: 日志条目字典
        """
        # 添加到缓存
        self._add_to_buffer(log_entry)
        
        # 推送到WebSocket
        if self.log_callback:
            try:
                await self.log_callback(log_entry)
            except Exception as e:
                logger.warning(f"推送日志到WebSocket失败: {e}")
    
    def _add_to_buffer(self, log_entry: Dict[str, Any]):
        """
        添加日志条目到缓存
        
        Args:
            log_entry: 日志条目
        """
        self.log_buffer.append(log_entry)
        
        # 保持缓存大小限制
        if len(self.log_buffer) > self.max_buffer_size:
            self.log_buffer = self.log_buffer[-self.max_buffer_size:]
    
    async def _load_recent_logs(self):
        """加载最近的日志到缓存"""
        if not self.log_file_path.exists():
            return
        
        try:
            # 读取文件的最后N行
            with open(self.log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # 获取最后的tail_lines行
            recent_lines = lines[-self.tail_lines:] if len(lines) > self.tail_lines else lines
            
            # 解析并添加到缓存
            for line in recent_lines:
                if line.strip():
                    log_entry = self._parse_log_line(line)
                    if log_entry:
                        self.log_buffer.append(log_entry)
            
            logger.info(f"已加载{len(self.log_buffer)}条历史日志到缓存")
            
        except Exception as e:
            logger.warning(f"加载历史日志失败: {e}")
    
    def get_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取最近的日志条目
        
        Args:
            limit: 返回的日志条目数量限制
            
        Returns:
            List[Dict]: 最近的日志条目列表
        """
        return self.log_buffer[-limit:] if len(self.log_buffer) > limit else self.log_buffer
    
    def search_logs(self, 
                   keyword: Optional[str] = None,
                   level: Optional[str] = None,
                   start_time: Optional[str] = None,
                   end_time: Optional[str] = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        """
        搜索日志条目
        
        Args:
            keyword: 关键词搜索
            level: 日志级别过滤
            start_time: 开始时间
            end_time: 结束时间
            limit: 返回条目数限制
            
        Returns:
            List[Dict]: 匹配的日志条目列表
        """
        filtered_logs = []
        
        for log_entry in self.log_buffer:
            # 关键词过滤
            if keyword and keyword.lower() not in log_entry['message'].lower():
                continue
            
            # 级别过滤
            if level and log_entry['level'] != level.upper():
                continue
            
            # 时间范围过滤
            if start_time:
                try:
                    log_time = datetime.fromisoformat(log_entry['timestamp'])
                    filter_start = datetime.fromisoformat(start_time)
                    if log_time < filter_start:
                        continue
                except ValueError:
                    pass
            
            if end_time:
                try:
                    log_time = datetime.fromisoformat(log_entry['timestamp'])
                    filter_end = datetime.fromisoformat(end_time)
                    if log_time > filter_end:
                        continue
                except ValueError:
                    pass
            
            filtered_logs.append(log_entry)
        
        # 返回最新的limit条记录
        return filtered_logs[-limit:] if len(filtered_logs) > limit else filtered_logs
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """
        获取日志统计信息
        
        Returns:
            Dict: 日志统计信息
        """
        if not self.log_buffer:
            return {
                'total_count': 0,
                'level_counts': {},
                'recent_errors': []
            }
        
        # 统计各级别的日志数量
        level_counts = {}
        recent_errors = []
        
        for log_entry in self.log_buffer:
            level = log_entry['level']
            level_counts[level] = level_counts.get(level, 0) + 1
            
            # 收集最近的错误日志
            if level in ['ERROR', 'CRITICAL'] and len(recent_errors) < 10:
                recent_errors.append({
                    'timestamp': log_entry['timestamp'],
                    'message': log_entry['message'][:100]  # 截取前100个字符
                })
        
        return {
            'total_count': len(self.log_buffer),
            'level_counts': level_counts,
            'recent_errors': recent_errors[-10:]  # 最近10条错误
        } 