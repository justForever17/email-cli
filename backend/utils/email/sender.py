"""
邮件发送模块
支持标准 SMTP SSL/TLS 以及 Outlook OAuth2 (XOAUTH2) 发信
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
import logging

from .logger import logger
from .outlook import OutlookMailHandler

class MailSender:
    """邮件发送器类"""
    
    @staticmethod
    def send_email(email_info, recipient, subject, body, db=None):
        """
        发送邮件
        
        Args:
            email_info: dict, 包含邮箱详情的字典（如 emails 表记录）
            recipient: str, 收件人邮箱地址
            subject: str, 邮件主题
            body: str, 邮件正文
            db: Database, 可选的数据库实例，用于刷新访问令牌并更新数据库
            
        Returns:
            tuple: (success_bool, message_str)
        """
        email_address = email_info['email']
        mail_type = email_info['mail_type']
        
        # 1. 确定 SMTP 服务器、端口及安全协议
        smtp_server = None
        smtp_port = 587  # 默认使用 TLS 587
        use_ssl = False  # True 表示使用 465 SSL，False 表示使用 TLS / STARTTLS
        
        if mail_type == 'gmail':
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
        elif mail_type == 'qq':
            smtp_server = 'smtp.qq.com'
            smtp_port = 465
            use_ssl = True
        elif mail_type == 'outlook':
            smtp_server = 'smtp.office365.com'
            smtp_port = 587
        elif mail_type == 'imap':
            # 通用 IMAP，尝试根据 IMAP 服务器地址智能推断 SMTP 服务器
            imap_server = email_info.get('server')
            if imap_server:
                # 转换例如 imap.xxx.com -> smtp.xxx.com
                smtp_server = imap_server.replace('imap.', 'smtp.').replace('mail.', 'smtp.')
                if smtp_server == imap_server:
                    if 'imap' in imap_server:
                        smtp_server = imap_server.replace('imap', 'smtp')
                    else:
                        smtp_server = 'smtp.' + imap_server.split('.')[-2] + '.' + imap_server.split('.')[-1]
            else:
                smtp_server = 'smtp.' + email_address.split('@')[1]
                
            smtp_port = email_info.get('port', 587)
            # 如果 IMAP 端口为 465，则默认 SMTP 使用 SSL，否则使用 587/TLS
            if smtp_port == 465:
                use_ssl = True
                
        # 最后的兜底
        if not smtp_server:
            smtp_server = 'smtp.' + email_address.split('@')[1]
            
        logger.info(f"准备通过 SMTP 服务器 {smtp_server}:{smtp_port} (SSL: {use_ssl}) 向 {recipient} 发送邮件...")
        
        # 2. 构建 MIME 邮件体
        msg = MIMEMultipart()
        msg['From'] = email_address
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = None
        try:
            # 3. 建立连接
            if use_ssl:
                server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=15)
            else:
                server = smtplib.SMTP(smtp_server, smtp_port, timeout=15)
                server.ehlo()
                server.starttls()  # 升级为 TLS 安全连接
                server.ehlo()
                
            # 4. 身份验证
            if mail_type == 'outlook':
                refresh_token = email_info.get('refresh_token')
                client_id = email_info.get('client_id')
                
                # 如果是 OAuth2 Outlook 邮箱
                if refresh_token and client_id:
                    logger.info("尝试使用 OAuth2 (XOAUTH2) 认证方式登录 Outlook...")
                    access_token, new_refresh_token = OutlookMailHandler.get_new_access_token(refresh_token, client_id)
                    if access_token:
                        if db and email_info.get('id'):
                            # 刷新并持久化保存新的访问令牌及可选的刷新令牌到数据库
                            db.update_email_token(email_info['id'], access_token, new_refresh_token)
                        
                        # 生成 XOAUTH2 授权字符串并进行 Base64 编码
                        auth_string = OutlookMailHandler.generate_auth_string(email_address, access_token)
                        auth_bytes = auth_string.encode('utf-8')
                        auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')
                        
                        # 发送 XOAUTH2 验证指令
                        code, resp = server.docmd('AUTH', 'XOAUTH2 ' + auth_b64)
                        if code != 235:
                            logger.warning(f"Outlook XOAUTH2 授权登录失败 (状态码: {code}, 响应: {resp})，尝试密码兜底认证...")
                            server.login(email_address, email_info['password'])
                        else:
                            logger.info("Outlook XOAUTH2 授权登录成功！")
                    else:
                        logger.warning("获取新的 OAuth2 令牌失败，转为密码直接认证...")
                        server.login(email_address, email_info['password'])
                else:
                    logger.info("未使用 OAuth2，采用标准密码认证方式登录 Outlook...")
                    server.login(email_address, email_info['password'])
            else:
                # 通用 SMTP 密码认证 (Gmail / QQ 邮箱等采用应用密码)
                logger.info(f"采用普通账户/应用密码方式进行 SMTP 登录...")
                server.login(email_address, email_info['password'])
                
            # 5. 执行邮件传输发送
            server.sendmail(email_address, [recipient], msg.as_string())
            logger.info("邮件传输成功！")
            return True, "邮件发送成功"
            
        except Exception as e:
            error_message = f"邮件发送失败: {str(e)}"
            logger.error(error_message)
            return False, error_message
            
        finally:
            # 6. 关闭连接释放资源
            if server:
                try:
                    server.quit()
                except:
                    pass
