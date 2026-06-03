<template>
  <div class="home-container">
    <!-- Premium Aurora Fluid Hero Section -->
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">Email-cli</h1>
        <p class="hero-subtitle">专为 AI Agent 设计的邮件自动化与管理工具</p>
        <div class="hero-buttons">
          <button @click="navigateToEmails" class="apple-btn-primary hover-scale">开始使用</button>
          <button @click="scrollToFeatures" class="apple-btn-secondary hover-scale">了解更多</button>
        </div>
      </div>
      <!-- Subtle Floating Aurora Light Orbs -->
      <div class="aurora-orbs">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        <div class="orb orb-3"></div>
      </div>
    </div>
    
    <!-- Cupertino Features Grid -->
    <div class="features-section" ref="featuresSection">
      <h2 class="section-title">功能特点</h2>
      <div class="features-grid">
        <div class="feature-card hover-scale" v-for="(feature, index) in features" :key="index">
          <div class="feature-icon-wrapper" :class="`bg-${feature.color}`">
            <el-icon><component :is="feature.icon" /></el-icon>
          </div>
          <h3>{{ feature.title }}</h3>
          <p>{{ feature.description }}</p>
        </div>
      </div>
    </div>
    
    <!-- Breathing Stats Segment -->
    <div class="stats-section">
      <div class="stats-grid">
        <div class="stat-card" v-for="(stat, index) in stats" :key="index">
          <div class="stat-number">{{ stat.value }}</div>
          <div class="stat-desc">{{ stat.description }}</div>
        </div>
      </div>
    </div>
    
    <!-- macOS/iOS Settings-style Quick Start Steps -->
    <div class="quick-start-section">
      <h2 class="section-title">快速开始</h2>
      <div class="settings-list-container">
        <div class="settings-row hover-scale" v-for="(step, index) in steps" :key="index">
          <div class="settings-icon-col" :class="`icon-bg-${index + 1}`">
            <span class="step-badge">{{ index + 1 }}</span>
          </div>
          <div class="settings-text-col">
            <h3>{{ step.title }}</h3>
            <p>{{ step.description }}</p>
          </div>
          <div class="settings-arrow-col">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </div>
    </div>
    
    <!-- CTA Bottom Banner -->
    <div class="cta-section">
      <div class="cta-content">
        <h2>开始使用 Email-cli</h2>
        <p>简单几步，高效管理您的所有邮箱</p>
        <button @click="navigateToEmails" class="apple-btn-white hover-scale">立即开始</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Briefcase, Management, Connection, Cpu, Search, Document, ArrowRight } from '@element-plus/icons-vue'

const router = useRouter()
const featuresSection = ref(null)

const features = [
  {
    icon: Briefcase,
    title: '邮箱集中管理',
    description: '集中维护与管理多个邮箱账户，支持配置各类 Microsoft IMAP 和标准邮箱。',
    color: 'primary'
  },
  {
    icon: Connection,
    title: '批量自动化',
    description: '支持批量选择、批量拉取收信和批量删除，极大释放人工重复劳作。',
    color: 'success'
  },
  {
    icon: Search,
    title: '垃圾邮件同步',
    description: '特有垃圾邮件夹自动检测技术，确保漏收的验证码和验证邮件及时同步。',
    color: 'warning'
  },
  {
    icon: Cpu,
    title: 'SMTP 外发保障',
    description: '集成标准 SSL/TLS 外发邮件，原生支持 Outlook 刷新令牌 XOAUTH2 安全发信。',
    color: 'danger'
  },
  {
    icon: Document,
    title: 'AI Agent 交互友好',
    description: '提供无死角的命令行 CLI 工具和纯净 JSON 格式输出，方便 Agent 直接调用。',
    color: 'info'
  },
  {
    icon: Cpu,
    title: '实时连接侦听',
    description: '基于高性能 WebSocket，实时向上广播每一封邮件同步和推送的处理进度。',
    color: 'primary'
  }
]

const stats = [
  { value: '100+', description: '邮箱并行处理' },
  { value: '10x', description: '收件效率提升' },
  { value: '24/7', description: '智能体全天候监控' }
]

const steps = [
  {
    title: '配置导入邮箱',
    description: '在"邮箱管理"页面轻松填入您的邮箱凭据，或者直接批量粘贴进行快速导入'
  },
  {
    title: '极速同步收信',
    description: '选择您需要收信的账号，点击"收信"，后端高并发线程将自动同步 INBOX 与垃圾邮件'
  },
  {
    title: '查看与管理邮件',
    description: '双击查看已同步的所有邮件详情、文本与接收状态，支持横向轻松检索过滤'
  },
  {
    title: '自动化外发',
    description: '不仅支持从 Web 端回复或撰写新邮件，还可以通过 CLI 由您的 AI 助手一键代发'
  }
]

const navigateToEmails = () => {
  router.push('/emails')
}

const scrollToFeatures = () => {
  featuresSection.value.scrollIntoView({ behavior: 'smooth' })
}
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 24px;
}

/* ==========================================================================
   Cupertino Aurora Fluid Hero Section
   ========================================================================== */
.hero-section {
  position: relative;
  background: radial-gradient(circle at 80% 0%, rgba(0, 113, 227, 0.09) 0%, rgba(168, 85, 247, 0.06) 40%, transparent 80%), var(--background-color-light);
  border: 1px solid var(--border-color-base);
  border-radius: var(--border-radius-xl);
  padding: 100px 40px;
  margin-bottom: 60px;
  text-align: center;
  box-shadow: var(--box-shadow);
  overflow: hidden;
  transition: background-color 0.3s;
}

.hero-content {
  position: relative;
  z-index: 2;
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: 64px;
  font-weight: 800;
  color: var(--primary-text-color);
  letter-spacing: -2px;
  margin-bottom: 16px;
  text-shadow: 0 10px 40px rgba(0, 0, 0, 0.02);
}

.hero-subtitle {
  font-size: 20px;
  font-weight: 500;
  color: var(--secondary-text-color);
  margin-bottom: 40px;
  letter-spacing: -0.3px;
}

.hero-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
}

/* Apple Premium Pill Buttons */
.apple-btn-primary {
  background: var(--primary-color);
  border: none;
  color: #FFFFFF;
  font-weight: 600;
  font-size: 16px;
  padding: 14px 32px;
  border-radius: var(--border-radius-full);
  cursor: pointer;
  box-shadow: var(--box-shadow-sm);
  transition: all var(--transition-fast);
}

.apple-btn-primary:hover {
  background: var(--primary-color-hover);
  box-shadow: var(--box-shadow-md);
  transform: translateY(-1px);
}

.apple-btn-primary:active {
  transform: scale(0.96);
}

.apple-btn-secondary {
  background: var(--background-color-base);
  border: 1px solid var(--border-color-base);
  color: var(--primary-text-color);
  font-weight: 600;
  font-size: 16px;
  padding: 14px 32px;
  border-radius: var(--border-radius-full);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.apple-btn-secondary:hover {
  background: var(--border-color-light);
  transform: translateY(-1px);
}

.apple-btn-secondary:active {
  transform: scale(0.96);
}

/* Floating Aurora Orbs */
.aurora-orbs {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 1;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.45;
}

.orb-1 {
  width: 250px;
  height: 250px;
  background: rgba(0, 113, 227, 0.15);
  top: -50px;
  right: -50px;
  animation: orbFloat 18s infinite ease-in-out;
}

.orb-2 {
  width: 200px;
  height: 200px;
  background: rgba(168, 85, 247, 0.12);
  bottom: -40px;
  left: -20px;
  animation: orbFloat 22s infinite ease-in-out reverse;
}

.orb-3 {
  width: 150px;
  height: 150px;
  background: rgba(52, 199, 89, 0.08);
  top: 40%;
  left: 30%;
  animation: orbPulse 12s infinite ease-in-out;
}

@keyframes orbFloat {
  0% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-20px) scale(1.1); }
  100% { transform: translateY(0) scale(1); }
}

@keyframes orbPulse {
  0% { transform: scale(1); opacity: 0.3; }
  50% { transform: scale(1.25); opacity: 0.6; }
  100% { transform: scale(1); opacity: 0.3; }
}

/* ==========================================================================
   Features Section
   ========================================================================== */
.features-section {
  margin-bottom: 80px;
  scroll-margin-top: 100px;
}

.section-title {
  text-align: center;
  font-size: 32px;
  font-weight: 700;
  color: var(--primary-text-color);
  letter-spacing: -1px;
  margin-bottom: 48px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 30px;
}

.feature-card {
  background-color: var(--background-color-light);
  border: 1px solid var(--border-color-base);
  padding: 32px;
  border-radius: var(--border-radius-lg);
  text-align: left;
  box-shadow: var(--box-shadow-sm);
  transition: all var(--transition-normal);
}

.feature-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--box-shadow-md);
  border-color: var(--primary-color);
}

.feature-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  font-size: 24px;
  color: #FFFFFF;
}

.bg-primary { background: linear-gradient(135deg, #0071E3 0%, #1485ff 100%); }
.bg-success { background: linear-gradient(135deg, #34C759 0%, #30b852 100%); }
.bg-warning { background: linear-gradient(135deg, #FF9500 0%, #e08300 100%); }
.bg-danger { background: linear-gradient(135deg, #FF3B30 0%, #e0322a 100%); }
.bg-info { background: linear-gradient(135deg, #64748B 0%, #475569 100%); }

.feature-card h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--primary-text-color);
  margin-bottom: 12px;
  letter-spacing: -0.3px;
}

.feature-card p {
  font-size: 14px;
  color: var(--regular-text-color);
  line-height: 1.6;
}

/* ==========================================================================
   Stats Section
   ========================================================================== */
.stats-section {
  margin-bottom: 80px;
  background-color: var(--border-color-light);
  border: 1px solid var(--border-color-base);
  padding: 40px 30px;
  border-radius: var(--border-radius-xl);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 30px;
}

.stat-card {
  text-align: center;
}

.stat-number {
  font-size: 48px;
  font-weight: 800;
  color: var(--primary-color);
  letter-spacing: -1.5px;
  margin-bottom: 4px;
}

.stat-desc {
  font-size: 14px;
  color: var(--secondary-text-color);
  font-weight: 600;
}

/* ==========================================================================
   macOS/iOS Settings-style Steps
   ========================================================================== */
.quick-start-section {
  margin-bottom: 80px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.settings-list-container {
  background-color: var(--background-color-light);
  border: 1px solid var(--border-color-base);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  box-shadow: var(--box-shadow-sm);
}

.settings-row {
  display: flex;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color-base);
  transition: all var(--transition-fast);
  cursor: pointer;
}

.settings-row:last-child {
  border-bottom: none;
}

.settings-row:hover {
  background-color: var(--border-color-light);
  transform: translateX(4px);
}

.settings-icon-col {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-shrink: 0;
  margin-right: 20px;
}

.icon-bg-1 { background-color: var(--primary-color); }
.icon-bg-2 { background-color: var(--success-color); }
.icon-bg-3 { background-color: var(--warning-color); }
.icon-bg-4 { background-color: #a855f7; }

.step-badge {
  color: #FFFFFF;
  font-weight: 700;
  font-size: 15px;
}

.settings-text-col {
  flex-grow: 1;
}

.settings-text-col h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--primary-text-color);
  margin-bottom: 4px;
  letter-spacing: -0.3px;
}

.settings-text-col p {
  font-size: 13px;
  color: var(--secondary-text-color);
  margin: 0;
}

.settings-arrow-col {
  color: var(--placeholder-text-color);
  font-size: 16px;
}

/* ==========================================================================
   Bottom CTA Section
   ========================================================================== */
.cta-section {
  background: linear-gradient(135deg, #0071E3 0%, #005bb5 100%);
  color: #FFFFFF;
  border-radius: var(--border-radius-xl);
  padding: 80px 30px;
  text-align: center;
  box-shadow: var(--box-shadow-md);
  position: relative;
  overflow: hidden;
}

.cta-section::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 20% 100%, rgba(52, 199, 89, 0.15) 0%, transparent 60%);
  pointer-events: none;
}

.cta-content {
  position: relative;
  z-index: 2;
}

.cta-content h2 {
  font-size: 36px;
  font-weight: 700;
  letter-spacing: -1px;
  margin-bottom: 12px;
}

.cta-content p {
  font-size: 16px;
  margin-bottom: 36px;
  opacity: 0.9;
  font-weight: 500;
}

.apple-btn-white {
  background: #FFFFFF;
  border: none;
  color: var(--primary-color);
  font-weight: 600;
  font-size: 16px;
  padding: 14px 36px;
  border-radius: var(--border-radius-full);
  cursor: pointer;
  box-shadow: var(--box-shadow-sm);
  transition: all var(--transition-fast);
}

.apple-btn-white:hover {
  background: #f5f5f7;
  box-shadow: var(--box-shadow-md);
  transform: translateY(-1px);
}

.apple-btn-white:active {
  transform: scale(0.96);
}

@media (max-width: 768px) {
  .hero-section {
    padding: 60px 20px;
  }
  
  .hero-title {
    font-size: 40px;
  }
  
  .hero-subtitle {
    font-size: 16px;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .settings-row {
    padding: 16px;
  }
  
  .settings-icon-col {
    margin-right: 12px;
  }
}
</style>