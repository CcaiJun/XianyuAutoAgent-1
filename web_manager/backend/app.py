"""
Web管理界面后端API服务

负责为XianyuAutoAgent项目提供Web管理功能，包括：
1. main.py进程管理和监控
2. 实时日志推送
3. 环境变量配置管理
4. 提示词文件管理

技术栈：FastAPI + WebSocket + SQLite
设计模式：RESTful API + 实时通信

Author: AI Assistant
Created: 2024-01-XX
Version: 1.0.0
"""

import os
import sys
import json
import asyncio
import subprocess
import signal
import threading
import queue
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from loguru import logger
import uvicorn

# 添加项目根目录到路径，以便导入项目模块
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from web_manager.backend.services.process_manager import ProcessManager
from web_manager.backend.services.config_manager import ConfigManager
from web_manager.backend.services.prompt_manager import PromptManager
from web_manager.backend.services.log_monitor import LogMonitor
from web_manager.backend.models.api_models import (
    ProcessStatusResponse, ConfigItem, ConfigUpdateRequest,
    PromptFile, PromptUpdateRequest, LogEntry
)

# 初始化FastAPI应用
app = FastAPI(
    title="XianyuAutoAgent Web管理器",
    description="为XianyuAutoAgent项目提供Web可视化管理界面",
    version="1.0.0"
)

# 配置CORS中间件，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # 允许的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务管理器
process_manager = ProcessManager(project_root)
config_manager = ConfigManager(project_root)
prompt_manager = PromptManager(project_root)
log_monitor = LogMonitor(project_root)

# WebSocket连接管理
class ConnectionManager:
    """WebSocket连接管理器，用于实时日志推送"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        """建立WebSocket连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket连接已建立，当前连接数: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket连接已断开，当前连接数: {len(self.active_connections)}")
            
    async def broadcast_log(self, log_entry: Dict[str, Any]):
        """向所有连接的客户端广播日志信息"""
        if self.active_connections:
            disconnected = []
            for connection in self.active_connections:
                try:
                    await connection.send_json(log_entry)
                except Exception as e:
                    logger.warning(f"向客户端发送日志失败: {e}")
                    disconnected.append(connection)
            
            # 清理断开的连接
            for connection in disconnected:
                self.disconnect(connection)

# 全局连接管理器实例
connection_manager = ConnectionManager()

# ======================= API路由定义 =======================

@app.get("/", summary="API根路径")
async def root():
    """API根路径，返回基本信息"""
    return {
        "message": "XianyuAutoAgent Web管理器API",
        "version": "1.0.0",
        "status": "运行中",
        "timestamp": datetime.now().isoformat()
    }

# ======================= 进程管理API =======================

@app.get("/api/process/status", response_model=ProcessStatusResponse, summary="获取进程状态")
async def get_process_status():
    """
    获取main.py进程的运行状态
    
    Returns:
        ProcessStatusResponse: 包含进程状态信息的响应
    """
    try:
        status = await process_manager.get_status()
        return ProcessStatusResponse(**status)
    except Exception as e:
        logger.error(f"获取进程状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取进程状态失败: {str(e)}")

@app.post("/api/process/start", summary="启动main.py进程")
async def start_process(background_tasks: BackgroundTasks):
    """
    启动main.py进程
    
    Args:
        background_tasks: FastAPI后台任务管理器
        
    Returns:
        dict: 操作结果
    """
    try:
        result = await process_manager.start_process()
        
        # 在后台任务中启动日志监控
        if result['success']:
            background_tasks.add_task(start_log_monitoring)
            
        return result
    except Exception as e:
        logger.error(f"启动进程失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动进程失败: {str(e)}")

@app.post("/api/process/stop", summary="停止main.py进程")
async def stop_process():
    """
    停止main.py进程
    
    Returns:
        dict: 操作结果
    """
    try:
        result = await process_manager.stop_process()
        
        # 停止日志监控
        if result['success']:
            await log_monitor.stop_monitoring()
            
        return result
    except Exception as e:
        logger.error(f"停止进程失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"停止进程失败: {str(e)}")

@app.post("/api/process/restart", summary="重启main.py进程")
async def restart_process(background_tasks: BackgroundTasks):
    """
    重启main.py进程
    
    Args:
        background_tasks: FastAPI后台任务管理器
        
    Returns:
        dict: 操作结果
    """
    try:
        # 先停止进程
        stop_result = await process_manager.stop_process()
        if not stop_result['success']:
            return stop_result
            
        # 等待进程完全停止
        await asyncio.sleep(2)
        
        # 启动进程
        start_result = await process_manager.start_process()
        
        # 在后台任务中启动日志监控
        if start_result['success']:
            background_tasks.add_task(start_log_monitoring)
            
        return start_result
    except Exception as e:
        logger.error(f"重启进程失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"重启进程失败: {str(e)}")

# ======================= 配置管理API =======================

@app.get("/api/config", response_model=List[ConfigItem], summary="获取环境配置")
async def get_config():
    """
    获取.env文件中的所有配置项
    
    Returns:
        List[ConfigItem]: 配置项列表
    """
    try:
        config_data = await config_manager.get_config()
        return [ConfigItem(**item) for item in config_data]
    except Exception as e:
        logger.error(f"获取配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")

@app.put("/api/config", summary="更新环境配置")
async def update_config(request: ConfigUpdateRequest):
    """
    更新.env文件中的配置项
    
    Args:
        request: 配置更新请求，包含要更新的配置项
        
    Returns:
        dict: 操作结果
    """
    try:
        result = await config_manager.update_config(request.configs)
        return result
    except Exception as e:
        logger.error(f"更新配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")

# ======================= 提示词管理API =======================

@app.get("/api/prompts", response_model=List[PromptFile], summary="获取提示词文件列表")
async def get_prompts():
    """
    获取prompts目录中的所有提示词文件（排除示例文件）
    
    Returns:
        List[PromptFile]: 提示词文件列表
    """
    try:
        prompt_files = await prompt_manager.get_prompt_files()
        return [PromptFile(**file) for file in prompt_files]
    except Exception as e:
        logger.error(f"获取提示词文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取提示词文件失败: {str(e)}")

@app.get("/api/prompts/{filename}", summary="获取特定提示词文件内容")
async def get_prompt_content(filename: str):
    """
    获取特定提示词文件的内容
    
    Args:
        filename: 文件名
        
    Returns:
        dict: 包含文件内容的响应
    """
    try:
        content = await prompt_manager.get_prompt_content(filename)
        return {"filename": filename, "content": content}
    except Exception as e:
        logger.error(f"获取提示词内容失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取提示词内容失败: {str(e)}")

@app.put("/api/prompts/{filename}", summary="更新提示词文件内容")
async def update_prompt(filename: str, request: PromptUpdateRequest):
    """
    更新特定提示词文件的内容
    
    Args:
        filename: 文件名
        request: 提示词更新请求，包含新的文件内容
        
    Returns:
        dict: 操作结果
    """
    try:
        result = await prompt_manager.update_prompt_content(filename, request.content)
        return result
    except Exception as e:
        logger.error(f"更新提示词失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新提示词失败: {str(e)}")

# ======================= 实时日志WebSocket =======================

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """
    WebSocket端点，用于实时推送main.py的日志信息
    
    Args:
        websocket: WebSocket连接对象
    """
    await connection_manager.connect(websocket)
    try:
        # 发送欢迎消息
        await websocket.send_json({
            "type": "system",
            "message": "日志监控已连接",
            "timestamp": datetime.now().isoformat(),
            "level": "INFO"
        })
        
        # 保持连接活跃
        while True:
            try:
                # 等待客户端消息（心跳检测）
                data = await websocket.receive_text()
                
                # 如果收到心跳消息，回复确认
                if data == "ping":
                    await websocket.send_text("pong")
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.warning(f"WebSocket通信异常: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info("WebSocket客户端断开连接")
    except Exception as e:
        logger.error(f"WebSocket连接异常: {e}")
    finally:
        connection_manager.disconnect(websocket)

# ======================= 后台任务函数 =======================

async def start_log_monitoring():
    """启动日志监控后台任务"""
    try:
        logger.info("启动日志监控...")
        await log_monitor.start_monitoring(connection_manager.broadcast_log)
    except Exception as e:
        logger.error(f"日志监控启动失败: {e}")

# ======================= 应用生命周期事件 =======================

@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化操作"""
    logger.info("XianyuAutoAgent Web管理器启动中...")
    
    # 检查项目根目录是否存在
    if not project_root.exists():
        logger.error(f"项目根目录不存在: {project_root}")
        return
    
    # 初始化各个管理器
    await process_manager.initialize()
    await config_manager.initialize()
    await prompt_manager.initialize()
    await log_monitor.initialize()
    
    logger.info("Web管理器初始化完成")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理操作"""
    logger.info("Web管理器正在关闭...")
    
    # 停止日志监控
    await log_monitor.stop_monitoring()
    
    # 清理WebSocket连接
    for connection in connection_manager.active_connections[:]:
        try:
            await connection.close()
        except Exception:
            pass
    
    logger.info("Web管理器已关闭")

# ======================= 主程序入口 =======================

if __name__ == "__main__":
    # 配置日志格式
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # 启动uvicorn服务器
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 