#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import shutil

base_dir = os.path.dirname(os.path.abspath(__file__))

def run_command(command, cwd=None):
    """安全执行终端命令并实时打印输出"""
    print(f"正在执行: {command} in {cwd or 'root'}")
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=cwd,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )
    
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            stripped = output.strip()
            try:
                print(stripped)
            except UnicodeEncodeError:
                # 兼容 Windows 终端非 UTF-8 编码时的打印报错，过滤掉非法多字节字符
                try:
                    print(stripped.encode(sys.stdout.encoding, errors='ignore').decode(sys.stdout.encoding))
                except Exception:
                    pass
            
    rc = process.poll()
    return rc == 0

def create_default_icon_if_not_exists():
    """使用 Pillow 自动在本地高画质生成一个极具 Cupertino 艺术感的 ICO 图标，若无 Pillow 则自动安装"""
    icon_path = os.path.join(base_dir, 'icon.ico')
    if os.path.exists(icon_path):
        print("[提示] 检测到 icon.ico 已存在，将直接使用。")
        return
        
    print("[提示] 本地缺少 icon.ico 图标，正在尝试动态生成...")
    
    # 尝试导入 Pillow，若失败则静默安装
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("未检测到 Pillow 库，正在为您自动安装以用于图标生成...")
        import subprocess
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "Pillow"], check=True)
            from PIL import Image, ImageDraw
        except Exception as pi_err:
            print(f"[警告] 自动安装 Pillow 库失败: {pi_err}，跳过图标生成。")
            return
        
    try:
        # 1. 创建一张 256x256 的高分辨率 RGBA 画布
        size = 256
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # 2. 画出苹果标志性的高对比圆角矩形背景（经典 iOS 蓝色背景）
        r = 60
        blue_color = (0, 113, 227, 255) # Apple Blue
        draw.rounded_rectangle([15, 15, size - 15, size - 15], radius=r, fill=blue_color)
        
        # 3. 绘制一个高质感、极简白色的信封线框
        x1, y1 = 60, 85
        x2, y2 = size - 60, size - 85
        
        # 画外框，线宽 8 像素
        envelope_color = (255, 255, 255, 255)
        draw.rectangle([x1, y1, x2, y2], outline=envelope_color, width=8)
        
        # 画信封折角线
        mid_x = size // 2
        mid_y = y1 + 45
        draw.line([x1, y1, mid_x, mid_y], fill=envelope_color, width=8)
        draw.line([x2, y1, mid_x, mid_y], fill=envelope_color, width=8)
        
        # 4. 保存为高标准 ICO 文件，嵌入多种尺寸
        image.save(icon_path, format="ICO", sizes=[(16,16), (32,32), (48,48), (256,256)])
        print(f"[成功] 圆满生成极简苹果风应用图标: {icon_path}")
    except Exception as e:
        print(f"[警告] 自动生成图标失败: {e}，将采用默认系统图标。")

def main():
    # 0. 检查并生成默认的应用图标
    create_default_icon_if_not_exists()
    
    print("==================================================")
    print("  Email-cli 原生 Windows GUI 桌面客户端打包程序")
    print("==================================================")
    
    # 1. 编译前端静态资源 SPA
    frontend_dir = os.path.join(base_dir, 'frontend')
    print("\n[步骤 1/3] 正在启动前端 Vue 3 (Vite) 生产环境编译...")
    
    # 验证 frontend 下是否有 node_modules
    if not os.path.exists(os.path.join(frontend_dir, 'node_modules')):
        print("提示: 未在 frontend 下检测到 node_modules，尝试安装依赖...")
        if not run_command("npm install", cwd=frontend_dir):
            print("错误: 安装前端 npm 依赖失败，请确保本地已安装 Node.js 与 npm！")
            sys.exit(1)
            
    # 执行打包
    if not run_command("npm run build", cwd=frontend_dir):
        print("错误: 前端 Vue 构建打包失败，请核对前端代码！")
        sys.exit(1)
        
    print("[成功] 前端编译打包成功，已生成静态资源库 'frontend/dist'。")
    
    # 2. 检查并清理历史打包痕迹
    print("\n[步骤 2/3] 清理历史缓存及临时目录...")
    
    # 苹果风高韧性自愈：在清理打包输出前，先安全备份已有的用户数据库数据，以防打包清空历史数据造成不便
    db_file_path = os.path.join(base_dir, 'dist_gui', 'Email-cli', 'backend', 'data', 'email-cli.db')
    backup_db_path = os.path.join(base_dir, 'build_tmp_db_backup.db')
    has_backup = False
    
    if os.path.exists(db_file_path):
        try:
            shutil.copy2(db_file_path, backup_db_path)
            has_backup = True
            print(f"[成功] 已将您已有的本地数据备份到临时区域: {backup_db_path}")
        except Exception as e:
            print(f"[警告] 备份您的数据库失败: {e}，将直接进行全新编译")
            
    for folder in ['build_tmp', 'dist_gui']:
        p = os.path.join(base_dir, folder)
        if os.path.exists(p):
            try:
                shutil.rmtree(p)
                print(f"已清理目录: {folder}")
            except Exception as e:
                print(f"清理 {folder} 失败: {e}")
                
    # 3. 运行 PyInstaller 进行一键高压缩打包
    print("\n[步骤 3/3] 正在启动 PyInstaller 进行 EXE 高压缩封装...")
    
    # 使用 python -m PyInstaller 彻底解决用户本地 Scripts 目录未加入 Path 环境变量的问题
    pyinstaller_cmd = (
        'python -m PyInstaller '
        '--clean '
        '--name="Email-cli" '
        '--add-data "backend;backend" '
        '--add-data "frontend/dist;frontend/dist" '
        '--hidden-import=jinja2.ext '
        '--hidden-import=sqlite3 '
        '--hidden-import=bs4 '
        '--hidden-import=jwt '
        '--hidden-import=websockets '
        '--hidden-import=flask_cors '
        '--hidden-import=imaplib '
        '--hidden-import=smtplib '
        '--hidden-import=requests '
        '--hidden-import=chardet '
        '--hidden-import=email.mime.text '
        '--hidden-import=email.mime.multipart '
        '--hidden-import=email.header '
        '--hidden-import=email.utils '
        '--hidden-import=email.message '
        '--icon="icon.ico" '
        '--workpath="build_tmp" '
        '--distpath="dist_gui" '
        'gui.py'
    )
    
    if run_command(pyinstaller_cmd, cwd=base_dir):
        # 苹果风高韧性自愈：在 PyInstaller 打包成功后，自动将之前备份的用户物理数据库数据完美迁移回原来的目录，无缝保留历史数据
        target_data_dir = os.path.join(base_dir, 'dist_gui', 'Email-cli', 'backend', 'data')
        os.makedirs(target_data_dir, exist_ok=True)
        target_db_path = os.path.join(target_data_dir, 'email-cli.db')
        
        restored = False
        if has_backup and os.path.exists(backup_db_path):
            try:
                shutil.copy2(backup_db_path, target_db_path)
                os.remove(backup_db_path)
                print(f"\n==================================================")
                print(f" [成功] 已将您之前客户端测试录入的历史数据完美迁移回新版本！")
                print(f" [文件] 本地数据库路径: {target_db_path}")
                print(f"==================================================")
                restored = True
            except Exception as e:
                print(f"\n[错误] 恢复备份的客户端数据失败: {e}")
                
        # 兜底自愈：如果客户端之前没有数据，但本地开发数据库 backend/data/email-cli.db 存在且有数据，则无缝同步过去
        if not restored:
            dev_db_path = os.path.join(base_dir, 'backend', 'data', 'email-cli.db')
            if os.path.exists(dev_db_path):
                try:
                    shutil.copy2(dev_db_path, target_db_path)
                    print(f"\n==================================================")
                    print(f" [同步] 检测到您在开发环境下有可用数据，已自动为您同步导入！")
                    print(f" [文件] 数据库物理路径: {target_db_path}")
                    print(f"==================================================")
                except Exception as e:
                    print(f"\n[警告] 自动导入开发环境数据失败: {e}")
                
        print("\n==================================================")
        print(" [完成] Email-cli 桌面客户端打包圆满成功！")
        print(f" [文件] 绿色版可执行文件存放于: {os.path.join(base_dir, 'dist_gui', 'Email-cli', 'Email-cli.exe')}")
        print("==================================================")
    else:
        print("\n[错误] PyInstaller 打包封装失败，请查看上方详细输出并排查依赖！")
        sys.exit(1)

if __name__ == '__main__':
    main()
