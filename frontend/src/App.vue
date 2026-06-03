<template>
  <el-config-provider :locale="zhCn">
    <div class="app-container">
      <el-container>
        <!-- Apple Glassmorphic Header -->
        <el-header class="app-header pywebview-drag-region" :class="{ 'scrolled': isScrolled }">
          <div class="header-left flex items-center">
            <!-- macOS 苹果风红黄绿窗口控制药丸 -->
            <div class="window-controls">
              <span class="control-dot close" @click="closeWindow" title="关闭"></span>
              <span class="control-dot minimize" @click="minimizeWindow" title="最小化"></span>
              <span class="control-dot maximize" @click="maximizeWindow" title="最大化/还原"></span>
            </div>
            <router-link to="/" class="logo-link ml-4" style="margin-left: 10px;">
              <h1>Email-cli</h1>
            </router-link>
          </div>
          
          <div class="header-right flex items-center">
            <!-- Cupertino Style Theme Slider Switch -->
            <div class="theme-slider-switch" @click="toggleTheme" :class="{ 'dark-active': isDark }" aria-label="Toggle Theme">
              <span class="theme-slider-thumb">
                <!-- Sun SVG -->
                <svg v-if="!isDark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="sun-icon-mini">
                  <circle cx="12" cy="12" r="4"></circle>
                  <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"></path>
                </svg>
                <!-- Moon SVG -->
                <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="moon-icon-mini">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                </svg>
              </span>
            </div>

            <!-- User Auth State -->
            <template v-if="!isAuthenticated">
              <router-link to="/login" class="nav-text-btn">登录</router-link>
              <router-link to="/register" class="nav-text-btn font-medium">注册</router-link>
            </template>
            
            <template v-else>
              <el-dropdown @command="handleUserCommand" trigger="click">
                <span class="user-dropdown-link flex items-center">
                  <span class="username-badge">{{ currentUser ? currentUser.username.substring(0, 2).toUpperCase() : 'U' }}</span>
                  <span class="username-text sm-hidden">{{ currentUser ? currentUser.username : '用户' }}</span>
                  <el-icon class="dropdown-arrow"><arrow-down /></el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu class="apple-dropdown-menu">
                    <el-dropdown-item command="account">账户设置</el-dropdown-item>
                    <el-dropdown-item v-if="isAdmin" command="admin">用户管理</el-dropdown-item>
                    <el-dropdown-item divided command="logout" class="text-danger">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
            
            <div class="connection-status-pure" :title="websocketConnected ? '服务已连接' : '服务未连接'">
              <span class="status-dot-pure" :class="{ 'connected': websocketConnected }"></span>
            </div>
          </div>
        </el-header>
        
        <!-- Apple Pill Nav Menu -->
        <div class="nav-menu-wrapper" v-if="isAuthenticated">
          <el-menu 
            mode="horizontal" 
            :router="true" 
            :default-active="$route.path"
            class="app-nav"
          >
            <el-menu-item index="/">
              <el-icon><HomeFilled /></el-icon>首页
            </el-menu-item>
            <el-menu-item index="/emails">
              <el-icon><Message /></el-icon>邮箱管理
            </el-menu-item>
            <el-menu-item index="/search">
              <el-icon><Search /></el-icon>邮件搜索
            </el-menu-item>
            <el-menu-item index="/admin/users" v-if="isAdmin">
              <el-icon><UserFilled /></el-icon>用户管理
            </el-menu-item>
            <el-menu-item index="/about">
              <el-icon><InfoFilled /></el-icon>关于
            </el-menu-item>
          </el-menu>
        </div>
        
        <!-- Main Area with premium breathing margin -->
        <el-main class="app-main">
          <router-view v-slot="{ Component }" v-if="!initializing">
            <transition name="apple-fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
          <div v-else class="loading-container flex-center">
            <el-skeleton :rows="6" animated />
          </div>
        </el-main>
        
        <el-footer class="app-footer">
          <div class="footer-content">
            Email-cli &copy; 2026 • Premium Cupertino Experience
          </div>
        </el-footer>
      </el-container>
      
      <!-- Notifications -->
      <Notifications />
    </div>
  </el-config-provider>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useStore } from 'vuex'
import { ElConfigProvider, ElMessage } from 'element-plus'
import { ArrowDown, Search, Message, HomeFilled, InfoFilled, UserFilled } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import websocket from '@/services/websocket'
import Notifications from './components/Notifications.vue'

// 初始化状态
const initializing = ref(true)
const isConnected = ref(false)
const isScrolled = ref(false)
const isDark = ref(false)

// 窗口无边框控制交互
const closeWindow = () => {
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.close_window()
  } else {
    console.log('系统API暂不可用 (可能处于浏览器开发环境)')
  }
}
const minimizeWindow = () => {
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.minimize_window()
  } else {
    console.log('系统API暂不可用')
  }
}
const maximizeWindow = () => {
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.maximize_window()
  } else {
    console.log('系统API暂不可用')
  }
}

// 使用Vuex管理状态
const store = useStore()
const router = useRouter()

// 计算属性
const websocketConnected = computed(() => store.state.websocketConnected)
const isAuthenticated = computed(() => store.getters['auth/isAuthenticated'])
const currentUser = computed(() => store.getters['auth/currentUser'])
const isAdmin = computed(() => store.getters['auth/isAdmin'])

// 滚动监听
const handleScroll = () => {
  isScrolled.value = window.scrollY > 15
}

// 主题切换逻辑
const toggleTheme = () => {
  isDark.value = !isDark.value
  applyTheme()
}

const applyTheme = () => {
  const root = document.documentElement
  if (isDark.value) {
    root.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    root.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

// 初始化认证状态
const initializeAuth = async () => {
  initializing.value = true
  if (isAuthenticated.value) {
    try {
      await store.dispatch('auth/getCurrentUser')
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }
  initializing.value = false
}

// 用户命令处理
const handleUserCommand = (command) => {
  switch (command) {
    case 'account':
      router.push('/account')
      break
    case 'admin':
      router.push('/admin/users')
      break
    case 'logout':
      handleLogout()
      break
  }
}

// 退出登录
const handleLogout = async () => {
  try {
    await store.dispatch('auth/logout')
    router.push('/login')
    ElMessage({
      type: 'success',
      message: '已成功退出登录'
    })
  } catch (error) {
    console.error('登出失败:', error)
    ElMessage.error('退出登录失败')
  }
}

const handleConnect = () => {
  store.commit('SET_WEBSOCKET_CONNECTED', true)
}

const handleDisconnect = () => {
  store.commit('SET_WEBSOCKET_CONNECTED', false)
}

watch(isAuthenticated, (newValue) => {
  if (newValue) {
    if (!websocket.isConnected) {
      websocket.connect()
    }
  } else {
    websocket.disconnect()
  }
})

// 挂载周期
onMounted(async () => {
  // 初始化系统双色模式
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    isDark.value = true
  } else {
    isDark.value = false
  }
  applyTheme()

  // 初始化验证
  await initializeAuth()
  
  // 连接逻辑
  websocket.onConnect(() => {
    isConnected.value = true
  })
  
  websocket.onDisconnect(() => {
    isConnected.value = false
  })
  
  websocket.onConnect(handleConnect)
  websocket.onDisconnect(handleDisconnect)
  
  if (isAuthenticated.value && !websocket.isConnected) {
    websocket.connect()
  }
  
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  websocket.offConnect(handleConnect)
  websocket.offDisconnect(handleDisconnect)
  websocket.disconnect()
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style>
/* App Layout Custom Overrides */
body, html, #app, .app-container, .app-main, .nav-menu-wrapper, .app-footer, .el-overlay {
  -webkit-app-region: no-drag !important;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--color-background);
}

.app-main {
  flex: 1;
  padding: 0 !important;
  background-color: var(--color-background);
}

/* Glassmorphic Header Styles */
.app-header {
  background: var(--glass-background) !important;
  backdrop-filter: blur(20px) saturate(180%) !important;
  -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
  border-bottom: 1px solid var(--glass-border) !important;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px 0 16px !important;
  height: 38px !important;
  position: sticky;
  top: 0;
  z-index: 100;
  transition: box-shadow var(--transition-normal), border-color var(--transition-normal) !important;
  
  /* 支持苹果风无边框窗口手势拖拽 */
  -webkit-app-region: drag !important;
}

/* 屏蔽拖拽，让交互子组件正常捕获点击事件 */
.logo-link,
.theme-toggle-btn,
.theme-slider-switch,
.nav-text-btn,
.user-dropdown-link,
.connection-status,
.connection-status-pure,
.window-controls,
.nav-menu-wrapper,
.app-main,
.el-dialog__wrapper,
.el-overlay {
  -webkit-app-region: no-drag !important;
}

/* macOS 经典三色控制 dot 小药丸 */
.window-controls {
  display: flex;
  gap: 6px;
  align-items: center;
  margin-right: 14px;
  height: 100%;
}

.control-dot {
  width: 11px;
  height: 11px;
  border-radius: 50%;
  cursor: pointer;
  position: relative;
  transition: filter var(--transition-fast) ease, transform 0.1s ease;
}

.control-dot:hover {
  filter: brightness(0.85);
  transform: scale(1.05);
}

.control-dot:active {
  transform: scale(0.95);
}

.control-dot.close {
  background-color: #FF5F56;
  border: 0.5px solid #E0443E;
}

.control-dot.minimize {
  background-color: #FFBD2E;
  border: 0.5px solid #DEA123;
}

.control-dot.maximize {
  background-color: #27C93F;
  border: 0.5px solid #1AAB29;
}

.app-header.scrolled {
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.03);
  border-bottom-color: var(--border-color-base) !important;
}

.logo-link {
  text-decoration: none;
}

.logo-link h1 {
  font-size: 15px;
  font-weight: 700;
  color: var(--primary-text-color);
  letter-spacing: -0.8px;
  margin: 0;
}

.header-right {
  gap: 12px;
}

/* macOS 经典胶囊物理滑动轨主题开关 */
.theme-slider-switch {
  background-color: var(--border-color-base);
  border: 1px solid var(--border-color-base);
  width: 36px;
  height: 20px;
  border-radius: 10px;
  position: relative;
  cursor: pointer;
  transition: background-color 0.3s cubic-bezier(0.25, 0.8, 0.25, 1), border-color 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  display: flex;
  align-items: center;
  padding: 0 2px;
}

.theme-slider-switch:hover {
  filter: brightness(0.95);
}

.theme-slider-switch.dark-active {
  background-color: #3A3A3C;
  border-color: #48484A;
}

.theme-slider-thumb {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background-color: #FFFFFF;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.25);
  display: flex;
  justify-content: center;
  align-items: center;
  transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1), background-color 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  transform: translateX(0);
}

.theme-slider-switch.dark-active .theme-slider-thumb {
  transform: translateX(16px);
  background-color: #1C1C1E;
}

.sun-icon-mini, .moon-icon-mini {
  width: 9px;
  height: 9px;
}

.sun-icon-mini {
  color: #FF9500;
}

.moon-icon-mini {
  color: #BF5AF2;
}

/* 极简去背景文字 Auth 链接按钮 */
.nav-text-btn {
  font-size: 12px;
  font-weight: 500;
  color: var(--secondary-text-color);
  text-decoration: none;
  padding: 3px 8px;
  border-radius: 6px;
  transition: all var(--transition-fast);
}

.nav-text-btn:hover {
  color: var(--primary-text-color);
  background-color: var(--border-color-light);
}

.nav-text-btn:active {
  transform: scale(0.96);
}

/* Premium User Dropdown Capsule */
.user-dropdown-link {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 2px 8px 2px 2px;
  border-radius: var(--border-radius-full);
  border: 1px solid var(--border-color-base);
  background-color: var(--background-color-base);
  transition: all var(--transition-fast);
}

.user-dropdown-link:hover {
  background-color: var(--border-color-light);
}

.username-badge {
  width: 22px;
  height: 22px;
  background-color: var(--primary-color);
  color: white;
  font-weight: 700;
  font-size: 9px;
  border-radius: var(--border-radius-full);
  display: flex;
  justify-content: center;
  align-items: center;
}

.username-text {
  font-size: 12px;
  font-weight: 500;
  color: var(--primary-text-color);
}

.dropdown-arrow {
  font-size: 12px;
  color: var(--secondary-text-color);
  transition: transform var(--transition-fast);
}

.user-dropdown-link:hover .dropdown-arrow {
  transform: translateY(1px);
}

/* Apple Dropdown styling override */
.apple-dropdown-menu {
  border-radius: var(--border-radius-md) !important;
  border: 1px solid var(--border-color-base) !important;
  box-shadow: var(--box-shadow-md) !important;
  background: var(--glass-background) !important;
  backdrop-filter: blur(20px) !important;
  -webkit-backdrop-filter: blur(20px) !important;
}

.el-dropdown-menu__item {
  font-weight: 500 !important;
  padding: 8px 16px !important;
  font-size: 14px !important;
  color: var(--primary-text-color) !important;
}

.el-dropdown-menu__item:hover {
  background-color: rgba(0, 113, 227, 0.08) !important;
  color: var(--primary-color) !important;
}

.el-dropdown-menu__item.text-danger {
  color: var(--danger-color) !important;
}

.el-dropdown-menu__item.text-danger:hover {
  background-color: rgba(255, 59, 48, 0.08) !important;
  color: var(--danger-color) !important;
}

/* 纯状态极简小呼吸灯 */
.connection-status-pure {
  display: flex;
  align-items: center;
  justify-content: center;
  padding-left: 2px;
}

.status-dot-pure {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: var(--danger-color);
  display: inline-block;
  position: relative;
  transition: all var(--transition-normal) ease;
  cursor: pointer;
  box-shadow: 0 0 3px rgba(255, 59, 48, 0.4);
}

.status-dot-pure.connected {
  background-color: var(--success-color);
  box-shadow: 0 0 8px var(--success-color);
  /* 注入高级脉冲呼吸微动效 */
  animation: pure-pulse 2.2s infinite ease-in-out;
}

@keyframes pure-pulse {
  0% {
    transform: scale(1);
    opacity: 0.85;
    box-shadow: 0 0 6px var(--success-color);
  }
  50% {
    transform: scale(1.2);
    opacity: 1;
    box-shadow: 0 0 12px var(--success-color);
  }
  100% {
    transform: scale(1);
    opacity: 0.85;
    box-shadow: 0 0 6px var(--success-color);
  }
}

/* Cupertino Pill-shaped Nav Menu */
.nav-menu-wrapper {
  display: flex;
  justify-content: center;
  margin: 24px auto 0;
  max-width: 1200px;
  width: calc(100% - 48px);
  animation: slideUpFade 0.4s var(--transition-normal);
}

.app-nav {
  display: flex;
  background-color: var(--background-color-light) !important;
  border: 1px solid var(--border-color-base) !important;
  border-radius: var(--border-radius-full) !important;
  padding: 6px !important;
  box-shadow: var(--box-shadow-sm) !important;
  width: auto !important;
  height: auto !important;
}

.app-nav .el-menu-item {
  border-radius: var(--border-radius-full) !important;
  height: 38px !important;
  line-height: 38px !important;
  font-weight: 500 !important;
  padding: 0 20px !important;
  font-size: 14px !important;
  color: var(--secondary-text-color) !important;
  border-bottom: none !important;
  transition: all var(--transition-fast) !important;
}

.app-nav .el-menu-item:hover, .app-nav .el-menu-item.is-active:hover {
  background-color: var(--border-color-light) !important;
  color: var(--primary-text-color) !important;
}

.app-nav .el-menu-item.is-active {
  background-color: var(--primary-color) !important;
  color: #FFFFFF !important;
  font-weight: 600 !important;
  box-shadow: var(--box-shadow-sm) !important;
}

.app-nav .el-icon {
  margin-right: 6px !important;
}

/* Footer Design */
.app-footer {
  padding: 30px 0 !important;
  background-color: transparent !important;
  border-top: 1px solid var(--border-color-base) !important;
  margin-top: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.footer-content {
  font-size: 13px;
  color: var(--secondary-text-color);
  font-weight: 500;
}

/* Apple Smooth Fade Transitions */
.apple-fade-enter-active,
.apple-fade-leave-active {
  transition: opacity 0.25s var(--transition-normal), transform 0.25s var(--transition-normal);
}

.apple-fade-enter-from {
  opacity: 0;
  transform: scale(0.995) translateY(4px);
}

.apple-fade-leave-to {
  opacity: 0;
  transform: scale(0.995) translateY(-4px);
}

@media (max-width: 768px) {
  .app-header {
    padding: 0 20px !important;
  }
  
  .nav-menu-wrapper {
    margin-top: 16px;
  }
  
  .app-nav .el-menu-item {
    padding: 0 12px !important;
    font-size: 13px !important;
  }
}
</style>