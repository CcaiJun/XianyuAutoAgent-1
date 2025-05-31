"""
进程管理服务

负责管理main.py进程的启动、停止、重启和状态监控。
提供进程生命周期管理和系统资源监控功能。

主要功能：
1. 进程启动和停止控制
2. 进程状态监控
3. 系统资源使用情况统计
4. 进程健康检查

Author: AI Assistant
Created: 2024-01-XX
Version: 1.0.0
"""

import os
import sys
import asyncio
import subprocess
import signal
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from pathlib import Path
from loguru import logger


class ProcessManager:
    """
    进程管理器
    
    负责main.py进程的完整生命周期管理，包括启动、停止、
    状态监控和资源使用统计。
    """
    
    def __init__(self, project_root: Path):
        """
        初始化进程管理器
        
        Args:
            project_root: 项目根目录路径
        """
        self.project_root = project_root
        self.main_py_path = project_root / "main.py"
        self.process: Optional[subprocess.Popen] = None
        self.process_info: Dict[str, Any] = {}
        self.start_time: Optional[datetime] = None
        
        # 进程监控相关配置
        self.check_interval = 5  # 状态检查间隔（秒）
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_monitoring = False
        
    async def initialize(self):
        """
        初始化进程管理器
        
        检查环境和依赖，验证main.py文件是否存在
        """
        logger.info("初始化进程管理器...")
        
        # 检查main.py文件是否存在
        if not self.main_py_path.exists():
            logger.error(f"main.py文件不存在: {self.main_py_path}")
            raise FileNotFoundError(f"main.py文件不存在: {self.main_py_path}")
        
        # 检查Python环境
        try:
            python_version = sys.version
            logger.info(f"Python版本: {python_version}")
        except Exception as e:
            logger.error(f"Python环境检查失败: {e}")
            raise
        
        # 检查是否有已运行的进程
        await self._check_existing_process()
        
        logger.info("进程管理器初始化完成")
    
    async def _check_existing_process(self):
        """
        检查是否有已经运行的main.py进程
        
        扫描系统进程，查找正在运行的main.py实例
        """
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_info = proc.info
                    cmdline = proc_info.get('cmdline', [])
                    
                    # 检查是否为Python进程且运行的是main.py
                    if (cmdline and 
                        ('python' in cmdline[0].lower() or 'python3' in cmdline[0].lower()) and
                        any('main.py' in arg for arg in cmdline)):
                        
                        logger.info(f"发现已运行的main.py进程: PID={proc_info['pid']}")
                        
                        # 尝试获取进程对象
                        try:
                            existing_proc = psutil.Process(proc_info['pid'])
                            self.process_info = {
                                'pid': existing_proc.pid,
                                'status': existing_proc.status(),
                                'create_time': existing_proc.create_time(),
                                'cpu_percent': 0.0,
                                'memory_percent': 0.0
                            }
                            self.start_time = datetime.fromtimestamp(existing_proc.create_time())
                            logger.info("已连接到现有进程")
                            return
                        except psutil.NoSuchProcess:
                            logger.warning("进程已不存在")
                            continue
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            logger.warning(f"检查现有进程时出错: {e}")
    
    async def get_status(self) -> Dict[str, Any]:
        """
        获取进程状态信息
        
        Returns:
            dict: 包含进程状态、资源使用情况等信息的字典
        """
        try:
            # 如果有进程信息，检查进程是否仍在运行
            if self.process_info and 'pid' in self.process_info:
                try:
                    proc = psutil.Process(self.process_info['pid'])
                    
                    # 更新进程状态信息
                    self.process_info.update({
                        'status': proc.status(),
                        'cpu_percent': proc.cpu_percent(),
                        'memory_percent': proc.memory_percent(),
                        'memory_info': proc.memory_info()._asdict(),
                        'num_threads': proc.num_threads(),
                    })
                    
                    # 计算运行时长
                    if self.start_time:
                        uptime = datetime.now() - self.start_time
                        uptime_str = self._format_timedelta(uptime)
                    else:
                        uptime_str = "未知"
                    
                    return {
                        'is_running': True,
                        'pid': self.process_info['pid'],
                        'start_time': self.start_time.isoformat() if self.start_time else None,
                        'cpu_percent': round(self.process_info['cpu_percent'], 2),
                        'memory_percent': round(self.process_info['memory_percent'], 2),
                        'status': '运行中',
                        'uptime': uptime_str
                    }
                    
                except psutil.NoSuchProcess:
                    # 进程已不存在，清理状态
                    logger.warning("进程已不存在，清理状态信息")
                    self._cleanup_process_info()
                    
            # 进程未运行
            return {
                'is_running': False,
                'pid': None,
                'start_time': None,
                'cpu_percent': None,
                'memory_percent': None,
                'status': '未运行',
                'uptime': None
            }
            
        except Exception as e:
            logger.error(f"获取进程状态失败: {e}")
            return {
                'is_running': False,
                'pid': None,
                'start_time': None,
                'cpu_percent': None,
                'memory_percent': None,
                'status': f'状态检查失败: {str(e)}',
                'uptime': None
            }
    
    async def start_process(self) -> Dict[str, Any]:
        """
        启动main.py进程
        
        Returns:
            dict: 启动操作结果
        """
        try:
            # 检查进程是否已在运行
            status = await self.get_status()
            if status['is_running']:
                return {
                    'success': False,
                    'message': f'进程已在运行 (PID: {status["pid"]})',
                    'pid': status['pid']
                }
            
            logger.info("准备启动main.py进程...")
            
            # 构建启动命令
            python_executable = sys.executable
            cmd = [python_executable, str(self.main_py_path)]
            
            # 设置工作目录为项目根目录
            cwd = str(self.project_root)
            
            # 设置环境变量
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.project_root)
            
            # 启动进程
            self.process = subprocess.Popen(
                cmd,
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1  # 行缓冲
            )
            
            # 等待进程启动
            await asyncio.sleep(1)
            
            # 检查进程是否成功启动
            if self.process.poll() is None:
                # 进程成功启动
                self.start_time = datetime.now()
                self.process_info = {
                    'pid': self.process.pid,
                    'status': 'running',
                    'create_time': time.time(),
                    'cpu_percent': 0.0,
                    'memory_percent': 0.0
                }
                
                logger.info(f"进程启动成功: PID={self.process.pid}")
                
                # 启动进程监控
                await self._start_monitoring()
                
                return {
                    'success': True,
                    'message': '进程启动成功',
                    'pid': self.process.pid
                }
            else:
                # 进程启动失败
                return_code = self.process.poll()
                error_output = ""
                
                try:
                    # 尝试读取错误输出
                    if self.process.stdout:
                        error_output = self.process.stdout.read()
                except Exception:
                    pass
                
                logger.error(f"进程启动失败，退出码: {return_code}")
                if error_output:
                    logger.error(f"错误输出: {error_output}")
                
                self._cleanup_process_info()
                
                return {
                    'success': False,
                    'message': f'进程启动失败，退出码: {return_code}',
                    'pid': None
                }
                
        except Exception as e:
            logger.error(f"启动进程时发生异常: {e}")
            self._cleanup_process_info()
            
            return {
                'success': False,
                'message': f'启动进程时发生异常: {str(e)}',
                'pid': None
            }
    
    async def stop_process(self) -> Dict[str, Any]:
        """
        停止main.py进程
        
        Returns:
            dict: 停止操作结果
        """
        try:
            # 检查进程是否在运行
            status = await self.get_status()
            if not status['is_running']:
                return {
                    'success': True,
                    'message': '进程未在运行',
                    'pid': None
                }
            
            pid = status['pid']
            logger.info(f"准备停止进程: PID={pid}")
            
            # 停止进程监控
            await self._stop_monitoring()
            
            try:
                proc = psutil.Process(pid)
                
                # 首先尝试优雅关闭（SIGTERM）
                proc.terminate()
                logger.info(f"已发送SIGTERM信号到进程: PID={pid}")
                
                # 等待进程关闭
                try:
                    proc.wait(timeout=10)  # 等待最多10秒
                    logger.info(f"进程已优雅关闭: PID={pid}")
                except psutil.TimeoutExpired:
                    # 如果进程未在指定时间内关闭，强制终止
                    logger.warning(f"进程未在10秒内关闭，强制终止: PID={pid}")
                    proc.kill()
                    proc.wait(timeout=5)
                    logger.info(f"进程已强制终止: PID={pid}")
                
            except psutil.NoSuchProcess:
                logger.info(f"进程已不存在: PID={pid}")
            
            # 清理进程信息
            self._cleanup_process_info()
            
            return {
                'success': True,
                'message': '进程已停止',
                'pid': pid
            }
            
        except Exception as e:
            logger.error(f"停止进程时发生异常: {e}")
            return {
                'success': False,
                'message': f'停止进程时发生异常: {str(e)}',
                'pid': None
            }
    
    async def _start_monitoring(self):
        """启动进程监控任务"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            logger.info("进程监控已启动")
    
    async def _stop_monitoring(self):
        """停止进程监控任务"""
        if self.is_monitoring:
            self.is_monitoring = False
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            logger.info("进程监控已停止")
    
    async def _monitoring_loop(self):
        """进程监控循环"""
        while self.is_monitoring:
            try:
                # 更新进程状态信息
                await self.get_status()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"进程监控循环出错: {e}")
                await asyncio.sleep(self.check_interval)
    
    def _cleanup_process_info(self):
        """清理进程信息"""
        self.process = None
        self.process_info = {}
        self.start_time = None
    
    def _format_timedelta(self, td: timedelta) -> str:
        """
        格式化时间间隔为可读字符串
        
        Args:
            td: 时间间隔对象
            
        Returns:
            str: 格式化的时间字符串
        """
        total_seconds = int(td.total_seconds())
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        parts = []
        if days > 0:
            parts.append(f"{days}天")
        if hours > 0:
            parts.append(f"{hours}小时")
        if minutes > 0:
            parts.append(f"{minutes}分钟")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}秒")
        
        return "".join(parts)
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        获取系统信息
        
        Returns:
            dict: 系统资源使用情况
        """
        try:
            # CPU信息
            cpu_count = psutil.cpu_count()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存信息
            memory = psutil.virtual_memory()
            
            # 磁盘信息
            disk = psutil.disk_usage('/')
            
            # 系统启动时间
            boot_time = psutil.boot_time()
            uptime = datetime.now() - datetime.fromtimestamp(boot_time)
            
            return {
                'cpu_count': cpu_count,
                'cpu_percent': round(cpu_percent, 2),
                'memory_total': memory.total,
                'memory_available': memory.available,
                'memory_percent': round(memory.percent, 2),
                'disk_total': disk.total,
                'disk_used': disk.used,
                'disk_percent': round((disk.used / disk.total) * 100, 2),
                'uptime': self._format_timedelta(uptime),
                'python_version': sys.version.split()[0]
            }
            
        except Exception as e:
            logger.error(f"获取系统信息失败: {e}")
            return {
                'error': f'获取系统信息失败: {str(e)}'
            } 