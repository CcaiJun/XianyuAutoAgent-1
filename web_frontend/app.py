import os
import sys
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from loguru import logger
import threading
import time

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from services.log_service import LogService


class XianyuWebApp:
    """
    咸鱼AI客服系统 Web管理界面
    
    提供实时日志查看功能，通过WebSocket实时推送main.py的日志输出
    """
    
    def __init__(self):
        """
        初始化Web应用
        """
        # 创建Flask应用
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'xianyu_web_secret_key_2024'
        
        # 配置模板和静态文件路径
        self.app.template_folder = 'templates'
        self.app.static_folder = 'static'
        
        # 初始化SocketIO
        self.socketio = SocketIO(
            self.app, 
            cors_allowed_origins="*",
            async_mode='eventlet',
            logger=False,
            engineio_logger=False
        )
        
        # 初始化日志服务
        self.log_service = LogService(self.socketio)
        
        # 应用状态
        self.is_running = False
        self.connected_clients = set()
        
        # 注册路由和事件处理器
        self._register_routes()
        self._register_socketio_events()
        
        logger.info("咸鱼Web管理界面初始化完成")
    
    def _register_routes(self):
        """
        注册Flask路由
        """
        
        @self.app.route('/')
        def index():
            """
            主页 - 实时日志查看界面
            
            Returns:
                str: 渲染后的HTML页面
            """
            logger.info("用户访问主页")
            return render_template('index.html')
        
        @self.app.route('/api/status')
        def get_status():
            """
            获取系统状态API
            
            Returns:
                json: 系统状态信息
            """
            try:
                stats = self.log_service.get_log_statistics()
                status = {
                    'app_status': 'running' if self.is_running else 'stopped',
                    'connected_clients': len(self.connected_clients),
                    'log_monitoring': stats.get('is_monitoring', False),
                    'log_file_path': stats.get('log_file_path', ''),
                    'total_logs': stats.get('total_logs', 0),
                    'last_update': stats.get('last_update', ''),
                    'timestamp': stats.get('last_update', '')
                }
                return jsonify(status)
            except Exception as e:
                logger.error(f"获取系统状态失败: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/logs/clear')
        def clear_logs():
            """
            清空前端日志显示（不影响日志文件）
            
            Returns:
                json: 操作结果
            """
            try:
                # 向所有客户端发送清空日志命令
                self.socketio.emit('clear_logs', namespace='/logs')
                logger.info("发送清空日志命令到所有客户端")
                return jsonify({'success': True, 'message': '日志已清空'})
            except Exception as e:
                logger.error(f"清空日志失败: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/logs/demo')
        def inject_demo_logs():
            """
            注入演示日志数据（用于演示和测试）
            
            Returns:
                json: 操作结果
            """
            try:
                # 注入演示日志
                self.log_service.inject_demo_logs()
                logger.info("演示日志注入完成")
                return jsonify({'success': True, 'message': '演示日志已注入'})
            except Exception as e:
                logger.error(f"注入演示日志失败: {str(e)}")
                return jsonify({'error': str(e)}), 500
    
    def _register_socketio_events(self):
        """
        注册SocketIO事件处理器
        """
        
        @self.socketio.on('connect', namespace='/logs')
        def handle_connect(auth):
            """
            客户端连接事件处理
            """
            client_id = request.sid  # 使用session ID作为客户端ID
            self.connected_clients.add(client_id)
            logger.info(f"客户端连接: {client_id}, 当前连接数: {len(self.connected_clients)}")
            
            # 发送连接成功消息
            emit('connection_status', {
                'status': 'connected',
                'message': '已连接到咸鱼AI客服日志监控',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        @self.socketio.on('disconnect', namespace='/logs')
        def handle_disconnect():
            """
            客户端断开连接事件处理
            """
            client_id = request.sid  # 使用session ID作为客户端ID
            self.connected_clients.discard(client_id)
            logger.info(f"客户端断开连接: {client_id}, 当前连接数: {len(self.connected_clients)}")
        
        @self.socketio.on('request_log_history', namespace='/logs')
        def handle_request_log_history(data):
            """
            客户端请求历史日志
            
            Args:
                data (dict): 请求参数，包含lines_count等
            """
            try:
                lines_count = data.get('lines_count', 100)
                logger.info(f"客户端请求历史日志，行数: {lines_count}")
                
                # 重新读取最近的日志
                self.log_service._read_existing_logs(lines_count)
                
                emit('log_history_loaded', {
                    'status': 'success',
                    'lines_count': lines_count,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                })
                
            except Exception as e:
                logger.error(f"处理历史日志请求失败: {str(e)}")
                emit('log_history_loaded', {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                })
        
        @self.socketio.on('ping', namespace='/logs')
        def handle_ping():
            """
            处理客户端心跳检测
            """
            emit('pong', {'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')})
    
    def start_background_tasks(self):
        """
        启动后台任务
        """
        def monitor_task():
            """
            日志监控后台任务
            """
            logger.info("启动日志监控后台任务")
            self.log_service.start_monitoring()
        
        def heartbeat_task():
            """
            服务器心跳任务，定期向客户端发送状态更新
            """
            while self.is_running:
                try:
                    # 每30秒发送一次状态更新
                    time.sleep(30)
                    
                    if self.connected_clients:
                        stats = self.log_service.get_log_statistics()
                        status_update = {
                            'type': 'server_heartbeat',
                            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'connected_clients': len(self.connected_clients),
                            'log_monitoring': stats.get('is_monitoring', False),
                            'total_logs': stats.get('total_logs', 0)
                        }
                        self.socketio.emit('status_update', status_update, namespace='/logs')
                
                except Exception as e:
                    logger.error(f"服务器心跳任务错误: {str(e)}")
        
        # 启动后台监控任务
        monitor_thread = threading.Thread(target=monitor_task, daemon=True)
        monitor_thread.start()
        
        # 启动心跳任务
        heartbeat_thread = threading.Thread(target=heartbeat_task, daemon=True)
        heartbeat_thread.start()
        
        logger.info("所有后台任务已启动")
    
    def run(self, host='0.0.0.0', port=8080, debug=False):
        """
        启动Web应用
        
        Args:
            host (str): 监听地址，默认0.0.0.0
            port (int): 监听端口，默认8080
            debug (bool): 是否开启调试模式，默认False
        """
        try:
            self.is_running = True
            
            # 启动后台任务
            self.start_background_tasks()
            
            logger.info(f"启动咸鱼Web管理界面: http://{host}:{port}")
            logger.info("功能: 实时日志监控、系统状态查看")
            
            # 启动Flask-SocketIO应用
            self.socketio.run(
                self.app,
                host=host,
                port=port,
                debug=debug,
                use_reloader=False  # 禁用重载器，避免多进程问题
            )
            
        except Exception as e:
            logger.error(f"启动Web应用失败: {str(e)}")
            self.is_running = False
        finally:
            self.cleanup()
    
    def cleanup(self):
        """
        清理资源
        """
        try:
            self.is_running = False
            
            # 停止日志监控
            if self.log_service:
                self.log_service.stop_monitoring()
            
            logger.info("Web应用资源清理完成")
            
        except Exception as e:
            logger.error(f"清理资源时发生错误: {str(e)}")


def main():
    """
    主函数 - 启动Web应用
    """
    # 配置日志
    logger.remove()  # 移除默认处理器
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # 检查命令行参数
    host = os.getenv('WEB_HOST', '0.0.0.0')
    port = int(os.getenv('WEB_PORT', '8080'))
    debug = os.getenv('WEB_DEBUG', 'False').lower() == 'true'
    
    logger.info("=" * 60)
    logger.info("咸鱼AI客服系统 - Web管理界面")
    logger.info("=" * 60)
    logger.info(f"监听地址: {host}:{port}")
    logger.info(f"调试模式: {debug}")
    logger.info("功能: 实时日志监控")
    logger.info("=" * 60)
    
    try:
        # 创建并启动Web应用
        web_app = XianyuWebApp()
        web_app.run(host=host, port=port, debug=debug)
        
    except KeyboardInterrupt:
        logger.info("接收到中断信号，正在关闭应用...")
    except Exception as e:
        logger.error(f"应用运行失败: {str(e)}")
    finally:
        logger.info("Web应用已退出")


if __name__ == '__main__':
    main() 