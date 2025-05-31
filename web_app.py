#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
咸鱼AI客服系统 - Web管理界面
功能：进程管理、实时日志显示、状态监控
"""

import os
import sys
import time
import json
import signal
import psutil
import subprocess
from datetime import datetime
from threading import Thread, Lock
from queue import Queue, Empty
from pathlib import Path

from flask import Flask, render_template, jsonify, request, Response
from loguru import logger
import logging

# 禁用Flask的默认日志输出，避免与loguru冲突
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

class ProcessManager:
    """进程管理器 - 负责main.py的启动、停止和状态监控"""
    
    def __init__(self):
        self.process = None
        self.status = "stopped"  # stopped, running, starting, stopping
        self.start_time = None
        self.lock = Lock()
        self.log_queue = Queue()
        self.log_thread = None
        self.output_thread = None
        
        # 确保日志目录存在
        os.makedirs("logs", exist_ok=True)
        
        logger.info("进程管理器初始化完成")
    
    def start_main_process(self):
        """启动main.py进程"""
        with self.lock:
            if self.status == "running":
                logger.warning("主进程已在运行中")
                return False, "主进程已在运行中"
            
            try:
                self.status = "starting"
                logger.info("正在启动main.py进程...")
                
                # 启动主进程，捕获输出
                self.process = subprocess.Popen(
                    [sys.executable, "main.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    cwd=os.getcwd(),
                    env=os.environ.copy(),
                    text=True,
                    bufsize=1,  # 行缓冲
                    universal_newlines=True
                )
                
                self.start_time = datetime.now()
                self.status = "running"
                
                # 启动输出监控线程
                self._start_output_monitoring()
                
                logger.info(f"主进程启动成功，PID: {self.process.pid}")
                return True, f"主进程启动成功，PID: {self.process.pid}"
                
            except Exception as e:
                self.status = "stopped"
                logger.error(f"启动主进程失败: {str(e)}")
                return False, f"启动失败: {str(e)}"
    
    def stop_main_process(self):
        """停止main.py进程"""
        with self.lock:
            if self.status != "running":
                logger.warning("主进程未在运行")
                return False, "主进程未在运行"
            
            try:
                self.status = "stopping"
                logger.info("正在停止main.py进程...")
                
                if self.process:
                    # 优雅停止进程
                    try:
                        self.process.terminate()
                        # 等待进程结束，最多等待10秒
                        self.process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        # 如果优雅停止失败，强制杀死进程
                        logger.warning("优雅停止超时，强制终止进程")
                        self.process.kill()
                        self.process.wait()
                    
                    logger.info(f"主进程已停止，PID: {self.process.pid}")
                    self.process = None
                
                self.status = "stopped"
                self.start_time = None
                
                # 停止输出监控
                self._stop_output_monitoring()
                
                return True, "主进程已停止"
                
            except Exception as e:
                self.status = "stopped"
                logger.error(f"停止主进程失败: {str(e)}")
                return False, f"停止失败: {str(e)}"
    
    def get_status(self):
        """获取进程状态信息"""
        with self.lock:
            status_info = {
                "status": self.status,
                "pid": self.process.pid if self.process else None,
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "running_time": None,
                "cpu_percent": None,
                "memory_mb": None,
                "memory_percent": None
            }
            
            # 如果进程在运行，获取更详细的信息
            if self.status == "running" and self.process:
                try:
                    # 检查进程是否仍在运行
                    if self.process.poll() is not None:
                        # 进程已结束，更新状态
                        self.status = "stopped"
                        self.start_time = None
                        self.process = None
                        status_info["status"] = "stopped"
                        self._stop_output_monitoring()
                        logger.warning("检测到主进程意外结束")
                    else:
                        # 计算运行时间
                        if self.start_time:
                            running_time = datetime.now() - self.start_time
                            status_info["running_time"] = str(running_time).split('.')[0]
                        
                        # 获取进程资源使用情况
                        try:
                            process = psutil.Process(self.process.pid)
                            status_info["cpu_percent"] = round(process.cpu_percent(), 1)
                            memory_info = process.memory_info()
                            status_info["memory_mb"] = round(memory_info.rss / 1024 / 1024, 1)
                            status_info["memory_percent"] = round(process.memory_percent(), 1)
                        except psutil.NoSuchProcess:
                            # 进程不存在，更新状态
                            self.status = "stopped"
                            self.start_time = None
                            self.process = None
                            status_info["status"] = "stopped"
                            self._stop_output_monitoring()
                            logger.warning("进程PID不存在，更新状态为停止")
                            
                except Exception as e:
                    logger.error(f"获取进程状态失败: {str(e)}")
            
            return status_info
    
    def _start_output_monitoring(self):
        """启动输出监控线程"""
        if self.output_thread and self.output_thread.is_alive():
            return
        
        self.output_thread = Thread(target=self._monitor_process_output, daemon=True)
        self.output_thread.start()
        logger.info("输出监控线程已启动")
    
    def _stop_output_monitoring(self):
        """停止输出监控"""
        # 线程是daemon线程，会随主程序结束而结束
        pass
    
    def _monitor_process_output(self):
        """监控进程输出"""
        try:
            if not self.process or not self.process.stdout:
                return
                
            # 读取进程输出
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    # 将输出行添加到队列中
                    self.log_queue.put(line.rstrip('\n\r'))
                else:
                    # 如果没有输出且进程已结束，退出循环
                    if self.process.poll() is not None:
                        break
                        
        except Exception as e:
            logger.error(f"进程输出监控出错: {str(e)}")
        finally:
            # 确保进程输出流被关闭
            if self.process and self.process.stdout:
                try:
                    self.process.stdout.close()
                except:
                    pass
    
    def get_recent_logs(self, lines=100):
        """获取最近的日志（从队列中获取）"""
        try:
            logs = []
            temp_queue = Queue()
            
            # 从队列中取出所有日志，保存到临时列表
            while not self.log_queue.empty():
                try:
                    log_line = self.log_queue.get_nowait()
                    logs.append(log_line)
                    temp_queue.put(log_line)
                except Empty:
                    break
            
            # 将日志放回队列（保留最近的日志）
            while not temp_queue.empty():
                try:
                    log_line = temp_queue.get_nowait()
                    self.log_queue.put(log_line)
                except Empty:
                    break
            
            # 返回最近的日志
            return logs[-lines:] if len(logs) > lines else logs
                
        except Exception as e:
            logger.error(f"获取最近日志失败: {str(e)}")
            return []
    
    def get_log_stream(self):
        """获取实时日志流"""
        while True:
            try:
                # 尝试从队列中获取新日志
                log_line = self.log_queue.get(timeout=1.0)
                yield f"data: {json.dumps({'type': 'log', 'content': log_line, 'timestamp': datetime.now().isoformat()})}\n\n"
            except Empty:
                # 发送心跳包
                yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now().isoformat()})}\n\n"


# 创建Flask应用和进程管理器实例
app = Flask(__name__)
process_manager = ProcessManager()

# 配置日志
logger.remove()
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)


@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """获取系统状态API"""
    try:
        status = process_manager.get_status()
        return jsonify({
            "success": True,
            "data": status
        })
    except Exception as e:
        logger.error(f"获取状态失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@app.route('/api/start', methods=['POST'])
def start_process():
    """启动主进程API"""
    try:
        success, message = process_manager.start_main_process()
        return jsonify({
            "success": success,
            "message": message
        })
    except Exception as e:
        logger.error(f"启动进程API失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@app.route('/api/stop', methods=['POST'])
def stop_process():
    """停止主进程API"""
    try:
        success, message = process_manager.stop_main_process()
        return jsonify({
            "success": success,
            "message": message
        })
    except Exception as e:
        logger.error(f"停止进程API失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@app.route('/api/logs')
def get_logs():
    """获取最近日志API"""
    try:
        lines = request.args.get('lines', 100, type=int)
        logs = process_manager.get_recent_logs(lines)
        return jsonify({
            "success": True,
            "data": logs
        })
    except Exception as e:
        logger.error(f"获取日志失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@app.route('/api/logs/stream')
def log_stream():
    """实时日志流API (Server-Sent Events)"""
    def generate():
        try:
            yield "data: {\"type\": \"connected\", \"message\": \"日志流连接成功\"}\n\n"
            for log_data in process_manager.get_log_stream():
                yield log_data
        except Exception as e:
            logger.error(f"日志流出错: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )


def run_web_app(host='127.0.0.1', port=5000, debug=False):
    """运行Web应用"""
    logger.info(f"启动Web应用: http://{host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == '__main__':
    try:
        # 处理命令行参数
        import argparse
        parser = argparse.ArgumentParser(description='咸鱼AI客服系统 - Web管理界面')
        parser.add_argument('--host', default='127.0.0.1', help='服务器主机地址')
        parser.add_argument('--port', type=int, default=5000, help='服务器端口')
        parser.add_argument('--debug', action='store_true', help='启用调试模式')
        
        args = parser.parse_args()
        
        # 信号处理
        def signal_handler(signum, frame):
            logger.info("收到停止信号，正在关闭...")
            if process_manager.status == "running":
                process_manager.stop_main_process()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # 启动Web应用
        run_web_app(host=args.host, port=args.port, debug=args.debug)
        
    except KeyboardInterrupt:
        logger.info("用户中断，正在退出...")
        if process_manager.status == "running":
            process_manager.stop_main_process()
    except Exception as e:
        logger.error(f"Web应用启动失败: {str(e)}")
        sys.exit(1) 