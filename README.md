# 📧 Email-cli - 智能体与原生桌面邮件管理套件

🌟 一款专为 AI Agent（智能体）与自动化流程量身定制的轻量级多邮箱批量收发工具，提供高效的命令行交互、数据持久化及邮件外发解决方案，同时附带极具 Cupertino 苹果美学的高质感原生 GUI 桌面客户端。

---

## 🖼️ 项目特性与功能

* 💻 **强大独立的命令行接口 (CLI)**：无需启动 Web 服务器即可独立运作。提供 `list`、`fetch`、`read`、`detail` 和 `send` 等命令。
* 🤖 **AI Agent 极简集成**：支持 `--json` 参数输出纯 UTF-8 编码的结构化 JSON 数据。在同步收信 `fetch` 成功后，系统会全自动提取 10 分钟内的新邮件，并就地内嵌邮件正文，Agent 无需进行二次 read 交互即可获取数据，极大节省 Token 消耗与处理延迟。
* 📤 **内置 SMTP 邮件发送引擎**：
  * 支持通用 SMTP SSL/TLS（自动根据 IMAP 地址解析推导发送端，如 `imap.xxx.com` 映射为 `smtp.xxx.com`）。
  * 原生支持 Outlook/Hotmail 借助 OAuth2 **`XOAUTH2`** 协议进行安全刷新和免密发信。
* 📥 **垃圾邮件夹自动同步**：拉取邮件时自动探索匹配 `junk` / `spam` / `垃圾` 文件夹，确保任何被系统误判的验证码邮件都不会被漏掉。
* 🔐 **安全管理**：密码采用 PBKDF2 和 SHA-256 算法高强度加密，敏感信息仅存储在本地轻量级 SQLite 数据库中。
* 🍎 **Cupertino 苹果风 GUI 壳子**：
  * **38px 置顶精致顶栏**：无边框窗口模式，支持顶栏空白手势拖拽、 macOS 经典三色窗口小药丸控制。
  * **无背景文字按钮**：右上角“登录”与“注册”采用极简去背景设计，Hover 呈现圆角呼吸背景。
  * **呼吸脉冲状态灯**：右上角仅以脉冲呼吸绿点指示 WebSocket 连接状态，灵动轻盈。
  * **物理滑轨主题开关**：亮/暗模式切换重塑为 macOS 胶囊滑动开关，白色滑球在左右滑移的同时日月图标发生微平移渐变，阻尼感拉满。
  * **文本允许自由复制**：邮件地址、详情表格行、密码字段及邮件正文区域强力启用 `user-select: text` 样式，保证随时可鼠标选中并复制。

---

## 🏗️ 开发环境快速启动

Email-cli 采用前后端分离的架构。您可以独立启动后端 Flask API 服务器和前端 Vue 3 渲染服务：

### 1. 准备工作

确保您的系统已安装 **Python 3.10+** 和 **Node.js 16+**。

### 2. 后端开发环境启动

1. **安装 Python 依赖库**：
   在项目根目录下执行：
   ```bash
   pip install -r requirements.txt
   ```
2. **运行 Flask 服务**：
   ```bash
   python backend/app.py
   ```
   * 后端主程序默认会在随机空闲端口上拉起 API 服务，并在控制台打印当前的 `HOST`, `FLASK_PORT` 和 `WS_PORT`（WebSocket 服务端端口）。
   * 数据库及配置文件将自动在 `backend/data/` 目录下生成并加载。

> 💡 **提示**：如果您不需要图形界面和 API 服务，仅需要使用命令行工具，可在安装依赖后**直接在终端运行 `python cli.py` 及其子命令**，它会自动直连 SQLite 数据库，无任何服务依赖。
> - 例如：`python cli.py list` 列出账户；
> - 例如：`python cli.py --json fetch --email test@outlook.com` 同步并就地获取最新邮件。

### 3. 前端开发环境启动

1. **进入前端目录**：
   ```bash
   cd frontend
   ```
2. **安装 npm 依赖项**：
   ```bash
   npm install
   ```
3. **开启 Vite 本地开发服务器**：
   ```bash
   npm run dev
   ```
   * 启动成功后，在浏览器访问 `http://localhost:5173` 即可进行开发调试。

---

## 📦 桌面原生 GUI 客户端一键打包编译

项目根目录下内置了一键构建与 PyInstaller EXE 打包封装脚本 `build_gui.py`：

### 1. 编译与打包步骤

在项目根目录下直接运行：
```bash
python build_gui.py
```

### 2. 打包脚本自动化流程

该脚本会以无损、高容灾的标准执行以下步骤：
1. **自动生成应用图标**：检测本地根目录下的 `icon.ico`。若缺失，将调用 Pillow 库自动渲染绘制出一个圆角苹果蓝（`#0071E3`）极简信封图形高画质 ICO 图标。
2. **前端 Vite 编译**：执行前端 Vue 代码的生产环境静态化构建，将产物输出至 `frontend/dist`。
3. **本地数据库暂存容灾**：为防止 PyInstaller 覆盖物理文件夹造成数据丢失，脚本会自动将旧版 `dist_gui` 里的 SQLite 数据库文件安全备份到临时区域。
4. **编译与高压缩封装**：调用 PyInstaller 对 `gui.py` 进行静态依赖分析与 EXE 绿包构建。
5. **数据恢复与多端互通同步**：
   * 打包成功后，将暂存备份的原版客户端数据库还原归位。
   * **兜底克隆机制**：若之前无客户端数据，但本地开发环境数据库 `backend/data/email-cli.db` 存在，则**全自动将开发环境数据库拷贝至打包客户端目录中**！确保用户在开发调试时注册的 `123123` 账号能瞬间免注册互通使用。
6. **交付成品**：最终生成的桌面客户端位于 `dist_gui/Email-cli/Email-cli.exe`。

---

## 📚 智能体 Skill 说明

* **命令行 Agent 技能手册**：[skills/email-cli/SKILL.md](skills/email-cli/SKILL.md)

---

## 📄 开源协议

本项目采用 [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) 许可证进行开源。