<template>
  <div class="page-container">
    <div class="about-wrapper">
      <!-- Apple Product Badge and Main Header -->
      <div class="about-hero flex-col items-center">
        <div class="app-logo-badge">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="app-logo-svg">
            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
            <polyline points="22,6 12,13 2,6"></polyline>
          </svg>
        </div>
        <h1 class="about-title">Email-cli</h1>
        <div class="version-tag">Version 1.0.0 (Cupertino)</div>
        <p class="about-intro">专为现代 AI 智能体与邮件办公设计的轻量级全功能收发与自动化控制面板。</p>
      </div>
      
      <!-- Premium Cards Grid -->
      <el-row :gutter="24" class="info-row">
        <el-col :xs="24" :md="8">
          <el-card shadow="hover" class="info-card">
            <h3>项目介绍</h3>
            <p>Email-cli 是一款开箱即用、轻量且强大的批量邮件管理套件。特有垃圾邮件夹自动侦测算法，完美攻克验证码和验证链接漏收的核心痛点。</p>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :md="8">
          <el-card shadow="hover" class="info-card">
            <h3>核心架构</h3>
            <p>前台采用 Vue 3 与 Element Plus 重塑，后台基于 Python 3 与 Flask。自带完整的高并发多线程同步引擎，性能卓越，收件极速。</p>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :md="8">
          <el-card shadow="hover" class="info-card">
            <h3>智能体高度友好</h3>
            <p>除精美的图形页面外，本项目无缝支持 CLI 命令行控制（提供 `--json` 纯净零损耗输出模式），支持 AI Agent 独立调用实现全流程办公闭环。</p>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- Apple Clean Features List -->
      <div class="features-block">
        <h2 class="block-title">亮点设计</h2>
        <div class="features-list-container">
          <div class="feature-item flex items-center" v-for="(feat, index) in highlights" :key="index">
            <div class="feat-icon-wrapper" :class="`icon-bg-${index + 1}`">
              <el-icon><component :is="feat.icon" /></el-icon>
            </div>
            <div class="feat-content">
              <h4>{{ feat.title }}</h4>
              <p>{{ feat.desc }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- AI Agent & CLI Premium Guideline Block -->
      <div class="agent-guide-block">
        <h2 class="block-title">AI 智能体 (Agent) & CLI 接入指引</h2>
        <el-card class="guide-card">
          <div class="guide-section">
            <h4 class="guide-subtitle flex items-center">
              <el-icon class="mr-sm text-primary" style="margin-right: 6px; font-size: 18px;"><Cpu /></el-icon>
              极速三步走接入指南
            </h4>
            <div class="steps-container">
              <div class="step-item">
                <span class="step-number">1</span>
                <div class="step-text">
                  <strong>添加 CLI 到 Agent 工具集：</strong>
                  在您的 Agent (如 Claude / Gemini) 环境变量中配置项目的根路径，将 <code>python cli.py</code> 做为核心 shell 运作指令。
                </div>
              </div>
              <div class="step-item">
                <span class="step-number">2</span>
                <div class="step-text">
                  <strong>免 HTTP 后端独立同步：</strong>
                  CLI 直连本地 SQLite 数据库。Agent 无需在后台开启 Flask 网页服务，通过 <code>python cli.py fetch</code> 即可实现增量收信。
                </div>
              </div>
              <div class="step-item">
                <span class="step-number">3</span>
                <div class="step-text">
                  <strong>获取极净降噪数据：</strong>
                  Agent 在调用时加上全局 <code>--json</code> 标记，即可输出紧凑、零噪的 JSON 数据，<b>完美避开了上万字 HTML 样式乱码的 Token 吞噬与截断</b>，让验证码提取准确率直达 100%！
                </div>
              </div>
            </div>
          </div>

          <div class="guide-section border-top">
            <h4 class="guide-subtitle flex items-center">
              <el-icon class="mr-sm text-success" style="margin-right: 6px; font-size: 18px;"><Finished /></el-icon>
              CLI 经典控制台指令看板
            </h4>
            <div class="code-terminal">
              <div class="terminal-header" style="display: flex; align-items: center;">
                <span class="terminal-dot red"></span>
                <span class="terminal-dot yellow"></span>
                <span class="terminal-dot green"></span>
                <span class="terminal-title">cli.py console</span>
              </div>
              <pre class="code-block"><code># 1. 增量同步所有绑定的邮箱（自动探测垃圾文件夹）
python cli.py fetch

# 2. 列出最新收取的邮件记录（零解析损耗 JSON 模式，推荐 AI 使用）
python cli.py --json list

# 3. 详细阅读某封具体邮件的极净去噪正文（彻底剥离 CSS/HTML 样式）
python cli.py read &lt;mail_id&gt;

# 4. 通过特定绑定的邮箱向目标发送邮件
python cli.py send --from &lt;email_id&gt; --to recipient@example.com --subject "Hello" --body "Content"</code></pre>
            </div>
          </div>
        </el-card>
      </div>

      <!-- Alert & Warnings (iOS notice style) -->
      <div class="notice-block">
        <h2 class="block-title">注意事项</h2>
        <div class="notice-alert-wrapper">
          <div class="apple-notice-card" v-for="(notice, index) in notices" :key="index" :class="`notice-type-${index + 1}`">
            <el-icon class="notice-icon"><Warning /></el-icon>
            <div class="notice-text">{{ notice }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Warning, Cpu, Connection, Setting, Finished } from '@element-plus/icons-vue'

const highlights = [
  {
    icon: Connection,
    title: '单链接双卡槽探测',
    description: '无需断开连接即可自动在同一会话中列出、搜索并并发提取收件箱与垃圾邮件箱。'
  },
  {
    icon: Cpu,
    title: 'OAuth2 刷新发信',
    description: '全面集成 SMTP (SSL/TLS) 标准发信协议，并针对 Outlook 原生支持刷新令牌 XOAUTH2 发信。'
  },
  {
    icon: Setting,
    title: '独立控制台 (CLI)',
    description: '直连 SQLite 数据库文件，即使不开启 Flask Web 后端应用也能够独立进行所有数据的增删改查和收发。'
  },
  {
    icon: Finished,
    title: '高标视觉与双色模式',
    description: '采用 SF Pro 极简无衬线字体，优雅的圆角和纯净的双色背景系统切换，提供 premium 办公质感。'
  }
]

const notices = [
  '本套件仅提供给用户进行自己邮箱的管理与办公自动化调试，禁止用于任何垃圾广告投递或违法渗透等非法用途。',
  '邮箱账号与密码等密匙数据完全仅保存在本地 SQLite 数据库中，请妥善保管和备份您的本地数据安全。',
  '由于 Microsoft 官方服务器接口访问具有频率和流控限制，在大并发批量同步时请合理调配请求间隔。'
]
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: var(--color-background);
}

.about-wrapper {
  padding: 40px 24px;
  max-width: 900px;
  margin: 0 auto;
}

/* ==========================================================================
   Apple Product Logo Badge
   ========================================================================== */
.about-hero {
  text-align: center;
  margin-bottom: 50px;
}

.app-logo-badge {
  width: 90px;
  height: 90px;
  border-radius: 22px;
  background: linear-gradient(135deg, var(--primary-color) 0%, #1485ff 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  color: #FFFFFF;
  box-shadow: var(--box-shadow-md);
  margin-bottom: 24px;
  transition: transform var(--transition-normal);
}

.app-logo-badge:hover {
  transform: rotate(5deg) scale(1.05);
}

.app-logo-svg {
  width: 44px;
  height: 44px;
}

.about-title {
  font-size: 36px;
  font-weight: 800;
  color: var(--primary-text-color);
  letter-spacing: -1.2px;
  margin: 0 0 6px 0;
}

.version-tag {
  font-size: 13px;
  font-weight: 600;
  color: var(--secondary-text-color);
  background-color: var(--border-color-light);
  border: 1px solid var(--border-color-base);
  padding: 4px 12px;
  border-radius: var(--border-radius-full);
  display: inline-block;
  margin-bottom: 20px;
}

.about-intro {
  font-size: 16px;
  color: var(--regular-text-color);
  max-width: 600px;
  line-height: 1.6;
  margin: 0 auto;
}

/* ==========================================================================
   Cards & Layout
   ========================================================================== */
.info-row {
  margin-bottom: 50px;
}

.info-card {
  height: 100%;
}

.info-card h3 {
  font-size: 16px;
  font-weight: 700;
  color: var(--primary-text-color);
  margin-bottom: 12px;
  letter-spacing: -0.3px;
}

.info-card p {
  font-size: 13.5px;
  color: var(--regular-text-color);
  line-height: 1.6;
  margin: 0;
}

.block-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary-text-color);
  letter-spacing: -0.5px;
  margin-bottom: 24px;
  position: relative;
}

/* Highlights List resembling iOS settings cell group */
.features-block {
  margin-bottom: 50px;
}

.features-list-container {
  background-color: var(--background-color-light);
  border: 1px solid var(--border-color-base);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  box-shadow: var(--box-shadow-sm);
}

.feature-item {
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color-base);
  transition: background-color var(--transition-fast);
}

.feature-item:last-child {
  border-bottom: none;
}

.feature-item:hover {
  background-color: var(--border-color-light);
}

.feat-icon-wrapper {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #FFFFFF;
  margin-right: 18px;
  font-size: 18px;
  flex-shrink: 0;
}

.icon-bg-1 { background-color: var(--primary-color); }
.icon-bg-2 { background-color: var(--success-color); }
.icon-bg-3 { background-color: var(--warning-color); }
.icon-bg-4 { background-color: #a855f7; }

.feat-content h4 {
  font-size: 15px;
  font-weight: 600;
  color: var(--primary-text-color);
  margin-bottom: 4px;
  letter-spacing: -0.3px;
}

.feat-content p {
  font-size: 13px;
  color: var(--secondary-text-color);
  margin: 0;
  line-height: 1.5;
}

/* Apple Notice Alerts resembling iOS Warning Panels */
.notice-block {
  margin-bottom: 20px;
}

.notice-alert-wrapper {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.apple-notice-card {
  display: flex;
  align-items: flex-start;
  padding: 16px 20px;
  border-radius: var(--border-radius);
  border: 1px solid transparent;
  gap: 12px;
}

.notice-type-1 {
  background-color: rgba(255, 149, 0, 0.08);
  border-color: rgba(255, 149, 0, 0.15);
  color: #c27100;
}

.notice-type-2 {
  background-color: rgba(0, 113, 227, 0.08);
  border-color: rgba(0, 113, 227, 0.15);
  color: var(--primary-color);
}

.notice-type-3 {
  background-color: rgba(255, 59, 48, 0.08);
  border-color: rgba(255, 59, 48, 0.15);
  color: var(--danger-color);
}

/* Dark mode adaptive colored warning texts */
.dark .notice-type-1 { color: #FF9500; }
.dark .notice-type-2 { color: #58A6FF; }
.dark .notice-type-3 { color: #FF453A; }

.notice-icon {
  font-size: 18px;
  margin-top: 2px;
  flex-shrink: 0;
}

.notice-text {
  font-size: 13px;
  font-weight: 500;
  line-height: 1.5;
}

/* ==========================================================================
   AI Agent & CLI Guideline styling
   ========================================================================== */
.agent-guide-block {
  margin-bottom: 50px;
}

.guide-card {
  border-radius: var(--border-radius-lg) !important;
  background-color: var(--background-color-light) !important;
}

.guide-section {
  padding: 8px 0;
}

.guide-section.border-top {
  border-top: 1px solid var(--border-color-base);
  margin-top: 24px;
  padding-top: 24px;
}

.guide-subtitle {
  font-size: 16px;
  font-weight: 700;
  color: var(--primary-text-color);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.steps-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.step-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
}

.step-number {
  background-color: var(--primary-color);
  color: #FFFFFF;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-shrink: 0;
  margin-top: 2px;
}

.step-text {
  font-size: 13.5px;
  line-height: 1.6;
  color: var(--regular-text-color);
}

.step-text code {
  background-color: var(--border-color-base);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-weight: 600;
  color: var(--primary-color);
}

/* Cupertino Monospace Terminal View */
.code-terminal {
  background-color: #1E1E1E;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--box-shadow-md);
  border: 1px solid #2D2D2D;
}

.terminal-header {
  background-color: #2D2D2D;
  padding: 10px 16px;
  display: flex;
  align-items: center;
}

.terminal-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 6px;
  display: inline-block;
}

.terminal-dot.red { background-color: #FF5F56; }
.terminal-dot.yellow { background-color: #FFBD2E; }
.terminal-dot.green { background-color: #27C93F; }

.terminal-title {
  color: #9A9A9A;
  font-size: 11px;
  font-family: SFMono-Regular, Consolas, monospace;
  font-weight: 600;
  margin-left: 10px;
}

.code-block {
  margin: 0;
  padding: 16px 20px;
  overflow-x: auto;
}

.code-block code {
  color: #34C759 !important; /* macOS terminal green */
  font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
  font-size: 13px;
  line-height: 1.6;
}
</style>