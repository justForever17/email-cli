---
name: email-cli
description: AI Agent 通过 Email-cli 命令行接口收发和自动化管理电子邮件的技能指南。
---

# Email-cli - 智能体自动化邮件操控技能

本技能教程旨在教导并指引 AI Agent 核心通过系统自带的 `cli.py` 命令行应用，在无人值守的状况下执行获取邮箱列表、同步/拉取邮件、阅读邮件内容以及安全发送邮件等高频自动化流程。

---

## 📌 命令执行环境

* **主入口文件**：项目根目录下的 `cli.py`
* **基础运行命令**：`python cli.py <subcommand> [options]`
* **全局通用选项**：`--json`（强烈建议 Agent 始终携带此选项，以保证输出易于直接解析的结构化 JSON 格式）

---

## 🛠️ 子命令与调用指南

### 1. 获取已配置的邮箱列表 (`list`)

列出数据库中所有已添加和校验过的邮箱账号，返回它们的特征及 ID。

* **调用示例**：
  ```bash
  python cli.py list --json
  ```
* **JSON 输出格式说明**：
  ```json
  [
    {
      "id": 1,
      "user_id": 1,
      "email": "your_email@outlook.com",
      "mail_type": "outlook",
      "server": null,
      "port": null,
      "use_ssl": true,
      "client_id": "9e5f94bc-e8a4-4e73-b8be-63364c29d753",
      "last_check_time": "2026-05-26T21:15:02",
      "enable_realtime_check": 1,
      "created_at": "2026-05-26T13:15:05",
      "updated_at": "2026-05-26T21:15:02"
    }
  ]
  ```

---

### 2. 同步并拉取最新邮件 (`fetch`)

触发底层的 IMAP/API 同步流程，实时探测收件箱（INBOX）以及自动锁定垃圾邮件夹（如 Junk Email/Spam），抓取最新的未处理邮件入库。

* **参数**：
  * `--email <address>`：指定的邮箱账户地址（必需）
* **调用示例**：
  ```bash
  python cli.py fetch --email your_email@outlook.com --json
  ```
* **JSON 输出格式说明**：
  ```json
  {
    "success": true,
    "message": "完成，共处理5封邮件，新增1封",
    "total": 5,
    "saved": 1
  }
  ```

---

### 3. 读取本地已存邮件列表 (`read`)

从 SQLite 数据库直接检索并分页展现指定邮箱中的已保存邮件，避免频繁访问远程邮件服务器造成封号或高延迟。

* **参数**：
  * `--email <address>`：指定的邮箱账户地址（必需）
  * `--limit <int>`：读取的最大条数限制，默认 20（可选）
* **调用示例**：
  ```bash
  python cli.py read --email your_email@outlook.com --limit 5 --json
  ```
* **JSON 输出格式说明**（出于防溢出考虑，本列表中对 `content` 正文进行了 100 字符内安全截断）：
  ```json
  [
    {
      "id": 42,
      "email_id": 1,
      "subject": "[GitHub] Please verify your device",
      "sender": "noreply@github.com",
      "received_time": "2026-05-26T21:14:15",
      "content": "Hey there! Your verification code is 987654. This code is valid for 10 minutes...",
      "folder": "Junk Email",
      "created_at": "2026-05-26T21:15:02"
    }
  ]
  ```

---

### 4. 获取特定邮件的完整细节 (`detail`)

根据邮件数据库的主键 ID，提取无截断的整封邮件正文（包含长 HTML 去标签后的格式化正文），非常适合用于读取整篇验证码以及解析文本指令。

* **参数**：
  * `--id <mail_record_id>`：邮件记录主键 ID（必需）
* **调用示例**：
  ```bash
  python cli.py detail --id 42 --json
  ```
* **JSON 输出格式说明**：
  ```json
  {
    "id": 42,
    "email_id": 1,
    "subject": "[GitHub] Please verify your device",
    "sender": "noreply@github.com",
    "received_time": "2026-05-26T21:14:15",
    "content": "Hey there! Your verification code is 987654. This code is valid for 10 minutes. Please enter it to authorize your device.",
    "folder": "Junk Email",
    "created_at": "2026-05-26T21:15:02",
    "recipient": "your_email@outlook.com"
  }
  ```

---

### 5. 发送电子邮件 (`send`)

利用底层的 SMTP 通道向目标收信人发送新的纯文本邮件。

* **参数**：
  * `--from <sender_address>`：已配置好的发信账号（必需）
  * `--to <recipient_address>`：收信人邮箱（必需）
  * `--subject "<title>"`：邮件标题（必需）
  * `--body "<body>"`：邮件纯文本内容（必需）
* **调用示例**：
  ```bash
  python cli.py send --from your_email@outlook.com --to test_user@qq.com --subject "Agent Auto Notification" --body "Dear User, this is an automated message sent by Email-cli." --json
  ```
* **JSON 输出格式说明**：
  ```json
  {
    "success": true,
    "message": "邮件发送成功"
  }
  ```

---

## 🤖 AI Agent 自动化流程典型组合（Recipe）

当 AI Agent 被分配任务：“获取指定邮箱上一次拉取的验证码，并回复确认收到时”：

1. **第 1 步：查库并拉取新邮件**
   ```bash
   python cli.py fetch --email user@outlook.com --json
   ```
2. **第 2 步：读取历史列表，寻找验证码的邮件 ID**
   ```bash
   python cli.py read --email user@outlook.com --limit 3 --json
   ```
   *（Agent 自行在 JSON 节点中，定位主题或发件人如 `noreply@github.com` 的首行，获取 `id` 属性，例如 `42`）*
3. **第 3 步：根据 ID 抓取完整验证码正文**
   ```bash
   python cli.py detail --id 42 --json
   ```
   *（Agent 从中正则提炼出类似 `987654` 的内容并回传给受控任务系统）*
4. **第 4 步：撰写并发送一封回复确认信**
   ```bash
   python cli.py send --from user@outlook.com --to admin@company.com --subject "Task completed successfully" --body "Verified successfully using code 987654." --json
   ```
