#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import socket
import threading
import logging
import time

# 显式引入邮件及网络核心标准库/三方库，引导 PyInstaller 静态依赖分析器正确进行高压缩打包
import imaplib
import smtplib
import email
import email.mime.text
import email.mime.multipart
import email.header
import email.utils
import email.message
import requests
import chardet
import bs4

# 顶级优化：支持打包解压路径与本地开发路径的兼容加载
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(base_dir, 'backend'))

# 配置全局日志
logger = logging.getLogger('Email-cli-GUI')

class WindowAPI:
    """供前台JS调用的原生窗口控制API"""
    def close_window(self):
        import webview
        logger.info("GUI前端请求：关闭原生窗口")
        active_win = webview.active_window()
        if active_win:
            active_win.destroy()
            
    def minimize_window(self):
        import webview
        logger.info("GUI前端请求：最小化原生窗口")
        active_win = webview.active_window()
        if active_win:
            active_win.minimize()
            
    def maximize_window(self):
        import webview
        logger.info("GUI前端请求：最大化/恢复原生窗口")
        active_win = webview.active_window()
        if active_win:
            active_win.toggle_fullscreen()

def find_free_port():
    """获取本地一个空闲的 TCP 端口"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port

def main():
    logger.info("正在启动 Email-cli 桌面原生客户端...")
    
    # 1. 动态寻找两个未占用的本地空闲端口
    flask_port = find_free_port()
    ws_port = find_free_port()
    
    logger.info(f"分配空闲端口: Flask 后端服务 = {flask_port}, WebSocket 消息总线 = {ws_port}")
    
    # 2. 计算打包后的物理路径与静态资源路径
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包环境
        assets_dir = sys._MEIPASS
    else:
        # 本地开发环境
        assets_dir = base_dir
        
    frontend_dist_dir = os.path.join(assets_dir, 'frontend', 'dist')
    
    # 3. 极速自适应注入：为前端生成动态环境配置，解决 WebSocket 在动态端口下的链接适配
    env_config_path = os.path.join(frontend_dist_dir, 'env-config.js')
    os.makedirs(os.path.dirname(env_config_path), exist_ok=True)
    
    try:
        with open(env_config_path, 'w', encoding='utf-8') as f:
            f.write(f"""// 桌面GUI自适应动态环境配置
window.API_URL = '/api';
window.WS_URL = 'ws://127.0.0.1:{ws_port}';
console.log('GUI自适应环境加载完成，API_URL:', window.API_URL, 'WS_URL:', window.WS_URL);
""")
        logger.info(f"成功写入动态环境配置文件: {env_config_path}")
    except Exception as e:
        logger.error(f"写入环境配置文件失败: {e}")

    # 4. 延迟加载后端核心库，防止系统变量初始化比端口指定更早发生
    # 注入端口到环境变量中，以防其它核心模块使用
    os.environ['HOST'] = '127.0.0.1'
    os.environ['FLASK_PORT'] = str(flask_port)
    os.environ['WS_PORT'] = str(ws_port)
    
    try:
        from backend.app import app, ws_handler, email_processor, db
    except ImportError as e:
        logger.error(f"导入后端服务核心模块失败: {e}")
        sys.exit(1)
        
    # 5. 配置并启动后台 WebSocket 服务 (守护线程方式运行)
    ws_handler.port = ws_port
    
    def run_websocket():
        try:
            ws_handler.run()
        except Exception as ex:
            logger.error(f"WebSocket 消息总线异常退出: {ex}")
            
    ws_thread = threading.Thread(target=run_websocket)
    ws_thread.daemon = True
    ws_thread.start()
    logger.info("WebSocket 后台守护服务拉起成功。")
    
    # 6. 配置并启动实时检查计划任务
    email_processor.start_real_time_check(check_interval=60)
    logger.info("后台多路高并发实时收信引擎启动成功。")
    
    # 7. 配置并启动 Flask 主服务 (非 reloader 守护线程方式运行)
    def run_flask():
        try:
            # 必须设置 use_reloader=False 且 debug=False，否则打包后二次拉起会引发崩溃和窗口重影
            app.run(host='127.0.0.1', port=flask_port, debug=False, use_reloader=False)
        except Exception as ex:
            logger.error(f"Flask 后端核心异常退出: {ex}")
            
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    logger.info("Flask HTTP 后台 API 服务拉起成功。")
    
    # 极微延迟确保本地 HTTP 和 WS 服务监听成功建立
    time.sleep(0.5)
    
    # 8. 启动原生 WebView2 窗口壳子
    import webview
    
    logger.info("弹出 Email-cli 苹果风图形客户端窗口...")
    
    # 创建精美大方的原生窗口（开启无边框苹果风，宽1280，高800，首选经典苹果铝灰背景，极力杜绝初始化时的白色刺眼闪烁）
    window = webview.create_window(
        title="Email-cli 邮件自动化助手",
        url=f"http://127.0.0.1:{flask_port}",
        width=1280,
        height=800,
        min_size=(1024, 700),
        background_color='#F5F5F7',
        frameless=True,  # 开启无边框苹果风
        easy_drag=False,  # 禁用全局随意拖拽，只允许带有 pywebview-drag-region 类名的区域拖拽
        js_api=WindowAPI()  # 注入JS窗口控制API
    )
    
    try:
        # 阻塞启动，代表前台图形界面运行中
        webview.start()
    finally:
        # 9. 优雅的生命周期退出清理：图形界面被用户点击关闭后自动安全关闭本地数据库，销毁全部守护线程
        logger.info("原生客户端主窗口已关闭，正在清理系统级资源...")
        try:
            if 'email_processor' in locals():
                logger.info("正在停止后台实时收信任务...")
                email_processor.stop_real_time_check()
                logger.info("正在关闭后台线程池...")
                email_processor.manual_thread_pool.shutdown(wait=False)
                email_processor.realtime_thread_pool.shutdown(wait=False)
                logger.info("后台邮件轮询服务已关闭")
        except Exception as e:
            logger.error(f"清理后台服务失败: {e}")
            
        if db:
            db.close()
        logger.info("本地数据库连接已断开。程序已安全退出。")
        # 强制退出整个进程，防止底层网络未决 socket 等非守护线程阻塞导致终端进程挂起
        os._exit(0)

if __name__ == '__main__':
    main()
