#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Email-cli 命令行自动化接口
让 AI Agent 和外部脚本极其方便地调用，支持列出账号、读写/收发邮件等自动化流程。
"""

import sys
import os
import argparse
import json
from datetime import datetime

# 强制 stdout 使用 utf-8 编码输出，防止 Windows cmd/powershell 默认 GBK 导致 ensure_ascii=False 报错
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# 注入 Python 搜索路径以支持直接导入 backend 模块
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, 'backend')
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

try:
    from database.db import Database
    from utils.email import EmailBatchProcessor, MailSender
except ImportError as e:
    print(f"【错误】导入模块失败，请确保在 Email-cli 项目根目录下运行：{str(e)}", file=sys.stderr)
    sys.exit(1)

def serialize_datetime(obj):
    """序列化时间对象为字符串以支持 JSON"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def format_ascii_table(headers, rows):
    """生成漂亮的 ASCII 表格，适合人类阅读"""
    if not rows:
        return "没有找到符合条件的记录。"
        
    # 计算每列的最大宽度
    widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            val_str = str(val)
            # 处理汉字字符宽度（汉字一般占两个字符宽度，这里做简化对齐处理）
            widths[idx] = max(widths[idx], len(val_str))
            
    # 构建边框和行
    border = "+" + "+".join(["-" * (w + 2) for w in widths]) + "+"
    header_line = "| " + " | ".join([f"{h:<{widths[i]}}" for i, h in enumerate(headers)]) + " |"
    
    result = [border, header_line, border]
    for row in rows:
        row_line = "| " + " | ".join([f"{str(val):<{widths[i]}}" for i, val in enumerate(row)]) + " |"
        result.append(row_line)
    result.append(border)
    return "\n".join(result)

def cmd_list(args, db):
    """列出所有配置的邮箱账户"""
    emails = db.get_all_emails()
    emails_list = [dict(email) for email in emails]
    
    # 过滤可能需要的敏感字段
    for email in emails_list:
        email.pop('password', None)
        email.pop('refresh_token', None)
        email.pop('access_token', None)
        
    if args.json:
        print(json.dumps(emails_list, default=serialize_datetime, ensure_ascii=False, indent=2))
        return
        
    headers = ["ID", "用户ID", "邮箱地址", "类型", "接收服务器", "SSL", "最后检查时间", "实时检查"]
    rows = []
    for e in emails_list:
        rows.append([
            e.get('id'),
            e.get('user_id'),
            e.get('email'),
            e.get('mail_type'),
            f"{e.get('server')}:{e.get('port')}" if e.get('server') else "OAuth2/API",
            "是" if e.get('use_ssl') else "否",
            e.get('last_check_time') or "从未检查",
            "开启" if e.get('enable_realtime_check') else "关闭"
        ])
        
    print("\n=== 配置邮箱账户列表 ===")
    print(format_ascii_table(headers, rows))

def is_recent_mail(received_time, minutes=10):
    """自适应判断这封邮件是否在最近的 X 分钟内"""
    if not received_time:
        return False
    
    dt = None
    if isinstance(received_time, datetime):
        dt = received_time
    else:
        time_str = str(received_time).strip()
        # 尝试标准 SQLite/ISO 日期时间格式解析
        for fmt in (
            '%Y-%m-%d %H:%M:%S.%f', 
            '%Y-%m-%d %H:%M:%S', 
            '%Y-%m-%dT%H:%M:%S.%f', 
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S%z',
            '%Y-%m-%dT%H:%M:%S%z'
        ):
            try:
                dt = datetime.strptime(time_str, fmt)
                break
            except ValueError:
                continue
        
        if not dt:
            # 试试 email 库的 RFC 解析
            import email.utils
            try:
                dt = email.utils.parsedate_to_datetime(time_str)
            except Exception:
                pass
                
        if not dt:
            # 保底尝试前 19 位
            try:
                dt = datetime.strptime(time_str[:19], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return False
                
    # 时区敏感比对
    if dt.tzinfo is not None:
        now = datetime.now().astimezone()
        diff = now - dt
    else:
        now = datetime.now()
        diff = now - dt
        
    seconds = diff.total_seconds()
    # 秒数在 -180秒（微小的系统时间超前）到 10 分钟内，均认为属于最近刚拉到的邮件
    return -180 <= seconds <= (minutes * 60)

def cmd_fetch(args, db):
    """检查并同步拉取指定邮箱的最新邮件"""
    # 查找符合邮箱地址的账户
    emails = db.get_all_emails()
    target_email = None
    for e in emails:
        if e['email'].lower() == args.email.lower():
            target_email = dict(e)
            break
            
    if not target_email:
        print(f"【错误】未找到邮箱地址为 {args.email} 的账户。", file=sys.stderr)
        sys.exit(1)
        
    print(f"开始拉取邮箱 {args.email} 的最新邮件...", file=sys.stderr)
    
    # 构造进度通知
    def progress_callback(progress, message):
        if not args.json:
            print(f"[{progress}%] {message}", file=sys.stderr)
            
    processor = EmailBatchProcessor(db)
    # 同步运行拉取任务
    result = processor._check_email_task(target_email, progress_callback)
    
    # 查询最近 10 分钟收割到的新邮件（包括普通邮件和垃圾邮件）
    recent_emails = []
    if result.get('success'):
        records = db.get_mail_records(target_email['id'])
        for r in records:
            r_dict = dict(r)
            if is_recent_mail(r_dict.get('received_time'), minutes=10):
                # 过滤/清洗正文，防止爆 Agent 长度
                if r_dict.get('content') and len(r_dict['content']) > 1500:
                    r_dict['content'] = r_dict['content'][:1500] + "..."
                recent_emails.append(r_dict)
                
    if args.json:
        # 在返回的 JSON 中就地追加 recent_emails
        result['recent_emails'] = recent_emails
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("\n=== 拉取结果 ===")
        if result.get('success'):
            print(f"【成功】{result.get('message')}")
            if recent_emails:
                print(f"\n=== 检测到最近 10 分钟收到的新邮件 (共 {len(recent_emails)} 封) ===")
                headers = ["邮件ID", "发件人", "主题", "接收时间", "所在文件夹"]
                rows = []
                for e in recent_emails:
                    subject = e.get('subject', '(无主题)')
                    if len(subject) > 25:
                        subject = subject[:22] + "..."
                    sender = e.get('sender', '(未知发件人)')
                    if len(sender) > 25:
                        sender = sender[:22] + "..."
                    rows.append([
                        e.get('id'),
                        sender,
                        subject,
                        e.get('received_time'),
                        e.get('folder') or "INBOX"
                    ])
                print(format_ascii_table(headers, rows))
                print("您可以使用 `cli.py detail --id <邮件ID>` 查看完整邮件详情。")
            else:
                print("未检测到 10 分钟内的最新邮件。")
        else:
            print(f"【失败】{result.get('message')}")

def cmd_read(args, db):
    """读取指定账户在数据库中已存的邮件"""
    # 先定位邮箱账户 ID
    emails = db.get_all_emails()
    email_id = None
    for e in emails:
        if e['email'].lower() == args.email.lower():
            email_id = e['id']
            break
            
    if not email_id:
        print(f"【错误】未找到邮箱地址为 {args.email} 的账户。", file=sys.stderr)
        sys.exit(1)
        
    records = db.get_mail_records(email_id)
    records_list = [dict(r) for r in records]
    
    # 限制返回数量
    if args.limit and args.limit > 0:
        records_list = records_list[:args.limit]
        
    if args.json:
        # 对正文做截断，防止 JSON 输出过大
        for r in records_list:
            if r.get('content') and len(r['content']) > 100:
                r['content'] = r['content'][:100] + "..."
        print(json.dumps(records_list, default=serialize_datetime, ensure_ascii=False, indent=2))
        return
        
    headers = ["邮件ID", "发件人", "主题", "接收时间", "所在文件夹"]
    rows = []
    for r in records_list:
        # 汉字主题或发件人太长做截断显示，保持表格整齐
        subject = r.get('subject', '(无主题)')
        if len(subject) > 25:
            subject = subject[:22] + "..."
            
        sender = r.get('sender', '(未知发件人)')
        if len(sender) > 25:
            sender = sender[:22] + "..."
            
        rows.append([
            r.get('id'),
            sender,
            subject,
            r.get('received_time'),
            r.get('folder') or "INBOX"
        ])
        
    print(f"\n=== 邮箱 {args.email} 的历史邮件记录 (最多展示前 {args.limit} 封) ===")
    print(format_ascii_table(headers, rows))

def cmd_detail(args, db):
    """查看某封邮件的详细信息和完整内容"""
    # 数据库没有直接的单个查询，但可以用搜索或者直接通过 SQLite 查询
    # 这里通过执行底层 SQL 查询该记录
    cursor = db.conn.execute("SELECT mr.*, e.email as recipient FROM mail_records mr JOIN emails e ON mr.email_id = e.id WHERE mr.id = ?", (args.id,))
    row = cursor.fetchone()
    
    if not row:
        print(f"【错误】未找到邮件ID为 {args.id} 的记录。", file=sys.stderr)
        sys.exit(1)
        
    mail = dict(row)
    
    if args.json:
        print(json.dumps(mail, default=serialize_datetime, ensure_ascii=False, indent=2))
        return
        
    print("\n================== 邮件详情 ==================")
    print(f" 邮件ID   : {mail.get('id')}")
    print(f" 收件人邮箱: {mail.get('recipient')}")
    print(f" 发件人   : {mail.get('sender')}")
    print(f" 邮件主题 : {mail.get('subject')}")
    print(f" 接收时间 : {mail.get('received_time')}")
    print(f" 所在文件夹: {mail.get('folder') or 'INBOX'}")
    print("----------------------------------------------")
    print(mail.get('content', '(邮件内容为空)'))
    print("==============================================")

def cmd_send(args, db):
    """使用配置好的账户发送新邮件"""
    # 查找发信人账户详情
    emails = db.get_all_emails()
    sender_account = None
    for e in emails:
        if e['email'].lower() == args.sender.lower():
            sender_account = dict(e)
            break
            
    if not sender_account:
        print(f"【错误】未找到发信账户：{args.sender}，请先在系统中配置此邮箱。", file=sys.stderr)
        sys.exit(1)
        
    print(f"正在通过 {args.sender} 向 {args.to} 发送邮件...", file=sys.stderr)
    
    success, msg = MailSender.send_email(
        email_info=sender_account,
        recipient=args.to,
        subject=args.subject,
        body=args.body,
        db=db
    )
    
    if args.json:
        print(json.dumps({"success": success, "message": msg}, ensure_ascii=False, indent=2))
    else:
        print("\n=== 发送状态 ===")
        if success:
            print(f"【成功】{msg}")
        else:
            print(f"【失败】{msg}")

def main():
    parser = argparse.ArgumentParser(
        description="Email-cli - AI Agent 邮箱自动化调用套件",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('--json', action='store_true', help='要求以结构化 JSON 格式输出结果（适合 Agent 直接抓取）')
    
    subparsers = parser.add_subparsers(dest='command', help='可用子命令')
    
    # 1. list
    subparsers.add_parser('list', help='列出所有已配置的邮箱账号')
    
    # 2. fetch
    p_fetch = subparsers.add_parser('fetch', help='实时同步并拉取指定账号的最新邮件')
    p_fetch.add_argument('--email', required=True, help='需要检查的邮箱账户地址')
    
    # 3. read
    p_read = subparsers.add_parser('read', help='从数据库读取指定账户的历史邮件记录')
    p_read.add_argument('--email', required=True, help='关联的邮箱账户地址')
    p_read.add_argument('--limit', type=int, default=20, help='读取记录数量限制 (默认: 20)')
    
    # 4. detail
    p_detail = subparsers.add_parser('detail', help='查看某封已存邮件的完整详细正文内容')
    p_detail.add_argument('--id', type=int, required=True, help='邮件记录 ID')
    
    # 5. send
    p_send = subparsers.add_parser('send', help='通过指定邮箱账户发送一封新邮件')
    p_send.add_argument('--from', dest='sender', required=True, help='已配置的发信人邮箱账户')
    p_send.add_argument('--to', required=True, help='收信人邮箱地址')
    p_send.add_argument('--subject', required=True, help='邮件主题')
    p_send.add_argument('--body', required=True, help='邮件纯文本正文内容')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
        
    # 初始化数据库
    db = Database()
    
    # 分发执行子命令
    try:
        if args.command == 'list':
            cmd_list(args, db)
        elif args.command == 'fetch':
            cmd_fetch(args, db)
        elif args.command == 'read':
            cmd_read(args, db)
        elif args.command == 'detail':
            cmd_detail(args, db)
        elif args.command == 'send':
            cmd_send(args, db)
    except Exception as e:
        error_info = {"success": False, "error": str(e)}
        if args.json:
            print(json.dumps(error_info, ensure_ascii=False, indent=2))
        else:
            print(f"【系统异常】执行命令时发生致命错误: {str(e)}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()

if __name__ == '__main__':
    main()
