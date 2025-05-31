import os
import time
import threading
import queue
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from loguru import logger
import re
from datetime import datetime
import json
import subprocess
import signal


class LogFileHandler(FileSystemEventHandler):
    """
    日志文件监控处理器
    
    监控日志文件的变化，实时读取新增的日志内容
    """
    
    def __init__(self, log_service):
        """
        初始化日志文件处理器
        
        Args:
            log_service: 日志服务实例
        """
        self.log_service = log_service
        self.last_position = 0  # 记录上次读取的文件位置
        
    def on_modified(self, event):
        """
        文件修改事件处理
        
        Args:
            event: 文件系统事件对象
        """
        if not event.is_directory and event.src_path == self.log_service.log_file_path:
            logger.debug(f"检测到日志文件变化: {event.src_path}")
            self.log_service.read_new_logs()


class LogService:
    """
    日志处理服务
    
    负责监控main.py的日志输出，解析日志内容，并通过WebSocket实时推送到前端
    """
    
    def __init__(self, socketio_instance):
        """
        初始化日志服务
        
        Args:
            socketio_instance: Flask-SocketIO实例，用于向前端推送消息
        """
        self.socketio = socketio_instance
        self.log_queue = queue.Queue()  # 日志消息队列
        self.is_monitoring = False  # 监控状态标志
        self.observer = None  # 文件系统监控器
        
        # 日志文件路径配置
        self.project_root = Path(__file__).parent.parent.parent
        self.logs_dir = self.project_root / "logs"
        self.log_file_path = self._find_log_file()
        
        # 日志解析相关配置
        self.last_position = 0  # 记录上次读取的文件位置
        self.log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        # 创建示例日志文件配置
        self._create_log_config_suggestion()
        
        logger.info(f"日志服务初始化完成，监控日志文件: {self.log_file_path}")
    
    def _find_log_file(self):
        """
        查找main.py的日志输出文件
        
        Returns:
            str: 日志文件的完整路径
        """
        # 尝试多种可能的日志文件位置
        possible_paths = [
            self.logs_dir / "xianyu_agent.log",  # 自定义日志文件
            self.logs_dir / "app.log",           # 通用应用日志
            self.project_root / "app.log",       # 项目根目录日志
            Path("/tmp/xianyu_agent.log"),       # 临时目录日志
        ]
        
        # 检查现有的日志文件
        for path in possible_paths:
            if path.exists() and path.stat().st_size > 0:
                logger.info(f"找到日志文件: {path}")
                return str(path)
        
        # 如果没有找到现有日志文件，创建默认日志文件
        self.logs_dir.mkdir(exist_ok=True)
        default_log_path = self.logs_dir / "xianyu_agent.log"
        
        # 创建空日志文件并写入提示信息
        with open(default_log_path, 'w', encoding='utf-8') as f:
            f.write(f"# 咸鱼AI客服系统日志文件\n")
            f.write(f"# 创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# 等待main.py写入日志...\n\n")
        
        logger.info(f"创建新的日志文件: {default_log_path}")
        return str(default_log_path)
    
    def _create_log_config_suggestion(self):
        """
        创建日志配置建议文件
        """
        config_path = self.project_root / "log_config_suggestion.py"
        if not config_path.exists():
            config_content = '''"""
咸鱼AI客服系统 - main.py日志配置建议

为了让Web前端能够显示实时日志，建议在main.py中添加文件日志输出：
"""

from loguru import logger
import sys
import os

# 在main.py的if __name__ == '__main__':部分替换现有的logger配置

if __name__ == '__main__':
    # 加载环境变量
    load_dotenv()
    
    # 配置日志级别
    log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()
    logger.remove()  # 移除默认handler
    
    # 添加控制台输出（保持原有功能）
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # 🔥 添加文件输出（Web前端需要）
    logger.add(
        "logs/xianyu_agent.log",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",      # 文件大小超过10MB时轮转
        retention="7 days",    # 保留7天的日志
        compression="zip",     # 压缩旧日志
        encoding="utf-8"
    )
    
    logger.info(f"日志级别设置为: {log_level}")
    logger.info("🌐 Web前端可访问: http://localhost:8080")
    
    # 其余代码保持不变...
'''
            
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            logger.info(f"已创建日志配置建议文件: {config_path}")
    
    def parse_log_line(self, line):
        """
        解析单行日志内容
        
        Args:
            line (str): 原始日志行
            
        Returns:
            dict: 解析后的日志信息字典
                - timestamp: 时间戳
                - level: 日志级别
                - message: 日志消息
                - raw_line: 原始日志行
                - category: 日志分类 (heartbeat, user_message, bot_reply, system, error)
        """
        try:
            # 跳过注释行和空行
            line = line.strip()
            if not line or line.startswith('#'):
                return None
            
            # 使用正则表达式解析loguru的日志格式
            # 格式1: 带颜色的格式 (stderr输出)
            # 格式2: 简单格式 (文件输出)
            patterns = [
                # 文件格式: 2024-01-15 10:30:45.123 | INFO     | main:401 - 消息内容
                r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) \| (\w+)\s+\| ([^:]+):(\d+) - (.+)',
                # 带颜色格式解析
                r'.*?(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}).*?\| (\w+).*?\| ([^:]+):(\d+) - (.+)',
                # 简化格式
                r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (\w+) - (.+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    if len(match.groups()) >= 5:
                        timestamp_str, level, module, line_num, message = match.groups()
                    else:
                        timestamp_str, level, message = match.groups()
                        module, line_num = 'main', '0'
                    
                    # 解析时间戳
                    try:
                        if '.' in timestamp_str:
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                        else:
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        timestamp = datetime.now()
                    
                    # 分类日志消息
                    category = self._categorize_message(message)
                    
                    return {
                        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'level': level.upper(),
                        'module': module,
                        'line_num': line_num if 'line_num' in locals() else '0',
                        'message': message.strip(),
                        'raw_line': line,
                        'category': category
                    }
            
            # 无法解析的日志行，尝试作为普通消息处理
            if any(level in line.upper() for level in self.log_levels):
                return {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'level': 'INFO',
                    'module': 'unknown',
                    'line_num': '0',
                    'message': line,
                    'raw_line': line,
                    'category': 'system'
                }
            
            return None
                
        except Exception as e:
            logger.error(f"解析日志行失败: {str(e)}, 原始内容: {line}")
            return {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'level': 'ERROR',
                'module': 'log_service',
                'line_num': '0',
                'message': f"日志解析错误: {str(e)}",
                'raw_line': line,
                'category': 'error'
            }
    
    def _categorize_message(self, message):
        """
        根据日志消息内容进行分类
        
        Args:
            message (str): 日志消息内容
            
        Returns:
            str: 消息分类
        """
        # 心跳相关消息
        if any(keyword in message for keyword in ['心跳', '连接', 'Token', 'WebSocket', '注册完成']):
            return 'heartbeat'
        
        # 用户消息
        if message.startswith('用户:') or '用户名' in message:
            return 'user_message'
        
        # 机器人回复
        if message.startswith('机器人回复:') or 'AI回复' in message:
            return 'bot_reply'
        
        # 人工接管相关
        if any(keyword in message for keyword in ['接管', '人工', '手动', '🔴', '🟢']):
            return 'manual_mode'
        
        # 错误消息
        if any(keyword in message for keyword in ['错误', '失败', '异常', 'error', 'Error', 'Exception']):
            return 'error'
        
        # 系统消息（默认）
        return 'system'
    
    def read_new_logs(self):
        """
        读取日志文件中的新增内容
        """
        try:
            if not os.path.exists(self.log_file_path):
                logger.warning(f"日志文件不存在: {self.log_file_path}")
                return
            
            with open(self.log_file_path, 'r', encoding='utf-8') as file:
                # 定位到上次读取的位置
                file.seek(self.last_position)
                
                # 读取新增的内容
                new_lines = file.readlines()
                
                # 更新读取位置
                self.last_position = file.tell()
                
                # 处理每一行新增的日志
                for line in new_lines:
                    parsed_log = self.parse_log_line(line)
                    if parsed_log:  # 只处理成功解析的日志
                        self._emit_log_to_frontend(parsed_log)
                        
        except Exception as e:
            logger.error(f"读取日志文件失败: {str(e)}")
    
    def _emit_log_to_frontend(self, log_data):
        """
        通过WebSocket向前端推送日志数据
        
        Args:
            log_data (dict): 解析后的日志数据
        """
        try:
            # 添加到消息队列
            self.log_queue.put(log_data)
            
            # 通过WebSocket发送到前端
            self.socketio.emit('new_log', log_data, namespace='/logs')
            logger.debug(f"推送日志到前端: {log_data['category']} - {log_data['message'][:50]}...")
            
        except Exception as e:
            logger.error(f"推送日志到前端失败: {str(e)}")
    
    def start_monitoring(self):
        """
        开始监控日志文件
        """
        if self.is_monitoring:
            logger.warning("日志监控已经在运行中")
            return
        
        try:
            # 确保日志文件存在
            if not os.path.exists(self.log_file_path):
                Path(self.log_file_path).touch()
                # 发送配置建议
                self._send_config_suggestion()
            
            # 读取现有日志内容
            self._read_existing_logs()
            
            # 设置文件系统监控
            self.observer = Observer()
            event_handler = LogFileHandler(self)
            
            # 监控日志文件所在目录
            watch_directory = os.path.dirname(self.log_file_path)
            self.observer.schedule(event_handler, watch_directory, recursive=False)
            
            # 启动监控
            self.observer.start()
            self.is_monitoring = True
            
            logger.info(f"开始监控日志文件: {self.log_file_path}")
            
        except Exception as e:
            logger.error(f"启动日志监控失败: {str(e)}")
            self.is_monitoring = False
    
    def _send_config_suggestion(self):
        """
        发送日志配置建议到前端
        """
        suggestion = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'level': 'WARNING',
            'module': 'log_service',
            'line_num': '0',
            'message': '⚠️ 未检测到日志文件，建议在main.py中添加文件日志输出配置。参考: log_config_suggestion.py',
            'raw_line': '',
            'category': 'system'
        }
        self._emit_log_to_frontend(suggestion)
    
    def stop_monitoring(self):
        """
        停止监控日志文件
        """
        if not self.is_monitoring:
            return
        
        try:
            if self.observer:
                self.observer.stop()
                self.observer.join()
                self.observer = None
            
            self.is_monitoring = False
            logger.info("已停止日志监控")
            
        except Exception as e:
            logger.error(f"停止日志监控失败: {str(e)}")
    
    def _read_existing_logs(self, lines_count=100):
        """
        读取现有的日志内容（最近的N行）
        
        Args:
            lines_count (int): 要读取的最近日志行数，默认100行
        """
        try:
            if not os.path.exists(self.log_file_path):
                logger.info("日志文件不存在，等待main.py生成日志...")
                self._send_config_suggestion()
                return
            
            file_size = os.path.getsize(self.log_file_path)
            if file_size == 0:
                logger.info("日志文件为空，等待main.py写入日志...")
                self._send_config_suggestion()
                return
            
            with open(self.log_file_path, 'r', encoding='utf-8') as file:
                # 读取所有行
                all_lines = file.readlines()
                
                # 过滤掉注释行和空行
                valid_lines = [line for line in all_lines if line.strip() and not line.strip().startswith('#')]
                
                # 获取最近的N行
                recent_lines = valid_lines[-lines_count:] if len(valid_lines) > lines_count else valid_lines
                
                # 设置读取位置到文件末尾
                self.last_position = file.tell()
                
                # 处理最近的日志行
                processed_count = 0
                for line in recent_lines:
                    parsed_log = self.parse_log_line(line)
                    if parsed_log:
                        self._emit_log_to_frontend(parsed_log)
                        processed_count += 1
                
                if processed_count > 0:
                    logger.info(f"已加载最近 {processed_count} 条日志记录")
                else:
                    logger.warning("未找到有效的日志记录")
                    self._send_config_suggestion()
                
        except Exception as e:
            logger.error(f"读取现有日志失败: {str(e)}")
    
    def get_log_statistics(self):
        """
        获取日志统计信息
        
        Returns:
            dict: 日志统计数据
        """
        try:
            stats = {
                'total_logs': self.log_queue.qsize(),
                'log_file_path': self.log_file_path,
                'is_monitoring': self.is_monitoring,
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'file_exists': os.path.exists(self.log_file_path),
                'file_size': os.path.getsize(self.log_file_path) if os.path.exists(self.log_file_path) else 0
            }
            return stats
        except Exception as e:
            logger.error(f"获取日志统计信息失败: {str(e)}")
            return {}
    
    def inject_demo_logs(self):
        """
        注入演示日志（用于演示和测试）
        """
        demo_logs = [
            {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'level': 'INFO',
                'module': 'demo',
                'line_num': '1',
                'message': '🌟 咸鱼AI客服系统启动完成',
                'raw_line': '',
                'category': 'system'
            },
            {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'level': 'INFO',
                'module': 'demo',
                'line_num': '2',
                'message': '🔗 WebSocket连接注册完成',
                'raw_line': '',
                'category': 'heartbeat'
            },
            {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'level': 'INFO',
                'module': 'demo',
                'line_num': '3',
                'message': '用户: 小明 (ID: 12345), 商品: 苹果手机, 会话: 67890, 消息: 这个手机还能便宜点吗？',
                'raw_line': '',
                'category': 'user_message'
            },
            {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'level': 'INFO',
                'module': 'demo',
                'line_num': '4',
                'message': '机器人回复: 您好！这个价格已经很优惠了，我们的产品质量有保证。如果您真心想要，我可以再给您优惠20元，您觉得怎么样？',
                'raw_line': '',
                'category': 'bot_reply'
            },
            {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'level': 'WARNING',
                'module': 'demo',
                'line_num': '5',
                'message': '🔴 已接管会话 67890 (商品: 苹果手机)',
                'raw_line': '',
                'category': 'manual_mode'
            }
        ]
        
        for log_data in demo_logs:
            self._emit_log_to_frontend(log_data)
            time.sleep(0.1)  # 小延迟使演示更真实
        
        logger.info("已注入演示日志数据") 