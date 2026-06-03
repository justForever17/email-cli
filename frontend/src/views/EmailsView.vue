<template>
  <div class="page-container">
    <div class="emails-container">
      <!-- Apple Glass Card wrapper -->
      <el-card class="email-list-card">
        <template #header>
          <div class="card-header flex-between">
            <h2 class="page-title">邮箱列表</h2>
            <div class="actions flex gap-md">
              <el-button type="primary" @click="refreshEmails" :icon="Refresh">
                刷新列表
              </el-button>
              <el-button type="success" @click="showAddEmailDialog" :icon="Plus">
                添加邮箱
              </el-button>
            </div>
          </div>
        </template>
        
        <!-- Bulk operation bar -->
        <div class="toolbar flex gap-md mb-6">
          <el-button 
            type="danger" 
            :disabled="!hasSelectedEmails" 
            @click="handleBatchDelete"
            :icon="Delete"
          >
            批量删除
          </el-button>
          <el-button 
            type="primary" 
            :disabled="!hasSelectedEmails" 
            @click="handleBatchCheck"
            :icon="Download"
          >
            批量收信
          </el-button>
        </div>
        
        <!-- Apple Premium Borderless modern Table -->
        <el-table
          v-loading="loading"
          :data="emails"
          @selection-change="handleSelectionChange"
          style="width: 100%"
          highlight-current-row
          class="email-table"
        >
          <el-table-column 
            type="selection" 
            width="50"
            :selectable="row => row" 
          />
          <el-table-column prop="email" label="邮箱地址" min-width="200" show-overflow-tooltip />
          
          <el-table-column prop="mail_type" label="类型" width="110">
            <template #default="scope">
              <el-tag 
                :type="getMailTypeColor(scope.row.mail_type || 'outlook')" 
                effect="plain"
                class="mail-type-tag"
              >
                {{ getMailTypeName(scope.row.mail_type || 'outlook') }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="password" label="密匙/密码" width="140">
            <template #default="scope">
              <div class="password-field flex-between">
                <span class="password-text">{{ scope.row.showPassword ? scope.row.password : '••••••' }}</span>
                <el-button 
                  type="primary" 
                  link
                  :icon="scope.row.showPassword ? Hide : View" 
                  @click="togglePasswordVisibility(scope.row)"
                  :loading="scope.row.passwordLoading"
                  class="password-toggle-btn"
                />
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="配置服务器" min-width="180" show-overflow-tooltip>
            <template #default="scope">
              <template v-if="scope.row.mail_type === 'imap'">
                <div class="server-badge">
                  <span>{{ scope.row.server || 'N/A' }}</span>
                  <span class="port-label">:{{ scope.row.port || 'N/A' }}</span>
                </div>
              </template>
              <template v-else-if="scope.row.mail_type === 'gmail'">
                <div class="server-badge">imap.gmail.com:993</div>
              </template>
              <template v-else-if="scope.row.mail_type === 'qq'">
                <div class="server-badge">imap.qq.com:993</div>
              </template>
              <template v-else>
                <span class="default-config-label">系统自动托管 XOAUTH2</span>
              </template>
            </template>
          </el-table-column>
          
          <el-table-column prop="last_check_time" label="最后同步时间" width="170">
            <template #default="scope">
              <span class="time-field">{{ formatDate(scope.row.last_check_time) }}</span>
            </template>
          </el-table-column>
          
          <el-table-column label="控制面板" fixed="right" width="380">
            <template #default="scope">
              <div class="action-buttons flex gap-sm">
                <el-button 
                  type="primary" 
                  size="small" 
                  :disabled="isEmailProcessing(scope.row)"
                  @click="handleCheck(scope.row)"
                >
                  {{ getEmailActionText(scope.row) }}
                </el-button>
                <el-button 
                  type="success" 
                  size="small" 
                  @click="handleViewMails(scope.row)"
                >
                  查看邮件
                </el-button>
                <el-button 
                  type="info" 
                  size="small" 
                  @click="showSendEmailDialog(scope.row)"
                >
                  写邮件
                </el-button>
                <el-button 
                  type="warning" 
                  size="small" 
                  @click="handleEdit(scope.row)"
                >
                  编辑
                </el-button>
                <el-button 
                  type="danger" 
                  size="small" 
                  @click="handleDelete(scope.row)"
                >
                  删除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
      
      <!-- Add Email Dialog (Glassmorphism) -->
      <el-dialog
        v-model="addEmailDialogVisible"
        title="添加邮箱"
        width="560px"
        :close-on-click-modal="false"
        class="add-email-dialog"
        destroy-on-close
      >
        <el-tabs v-model="addEmailActiveTab" class="apple-tabs">
          <el-tab-pane label="单个添加" name="single">
            <el-form
              ref="addEmailFormRef"
              :model="addEmailForm"
              :rules="addEmailRules"
              label-width="100px"
              class="add-email-form"
            >
              <el-form-item label="邮箱类型" prop="mail_type">
                <el-select v-model="addEmailForm.mail_type" placeholder="请选择邮箱类型" class="w-full">
                  <el-option 
                    v-for="(config, type) in mailTypes" 
                    :key="type"
                    :label="config.name" 
                    :value="type" 
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="邮箱地址" prop="email">
                <el-input v-model="addEmailForm.email" placeholder="example@outlook.com" />
              </el-form-item>

              <el-form-item label="密码" prop="password">
                <el-input
                  v-model="addEmailForm.password"
                  type="password"
                  placeholder="请输入您的邮箱密码或应用授权码"
                  show-password
                />
              </el-form-item>

              <template v-if="addEmailForm.mail_type === 'outlook'">
                <el-form-item label="Client ID" prop="client_id">
                  <el-input v-model="addEmailForm.client_id" placeholder="Microsoft Azure Application Client ID" />
                </el-form-item>

                <el-form-item label="Refresh Token" prop="refresh_token">
                  <el-input v-model="addEmailForm.refresh_token" placeholder="Offline OAuth2 Refresh Token" />
                </el-form-item>
              </template>

              <template v-if="addEmailForm.mail_type === 'imap'">
                <el-form-item label="服务器" prop="server">
                  <el-input v-model="addEmailForm.server" placeholder="imap.domain.com" />
                </el-form-item>

                <el-form-item label="端口" prop="port">
                  <el-input-number v-model="addEmailForm.port" :min="1" :max="65535" controls-position="right" />
                </el-form-item>
                
                <el-form-item label="使用SSL" prop="use_ssl">
                  <el-switch v-model="addEmailForm.use_ssl" />
                </el-form-item>
              </template>
            </el-form>
          </el-tab-pane>
          
          <el-tab-pane label="批量导入" name="batch">
            <div class="import-help">
              <strong>格式规范：</strong> 每行录入一条数据，使用 <code>----</code> 进行分割：<br/>
              <code>邮箱地址----密码----客户端ID----刷新令牌</code>
            </div>
            <el-form :model="batchImport" label-width="100px" :rules="batchImportRules" ref="batchImportFormRef" class="add-email-form">
              <el-form-item label="邮箱类型">
                <el-select v-model="batchImport.mailType" placeholder="请选择邮箱类型" class="w-full">
                  <el-option label="Outlook/Hotmail" value="outlook" />
                </el-select>
              </el-form-item>
              <el-form-item label="批量数据" prop="data">
                <el-input
                  v-model="batchImport.data"
                  type="textarea"
                  :rows="8"
                  placeholder="例如: example@outlook.com----password----clientid----refreshtoken"
                />
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>
        
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="addEmailDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="handleAddOrImport" :loading="addingEmail || importing">
              确定添加
            </el-button>
          </span>
        </template>
      </el-dialog>
      
      <!-- Mail Records Dialog (Glassmorphism) -->
      <el-dialog
        v-model="mailListDialogVisible"
        title="邮件记录"
        width="85%"
        top="8vh"
        class="mail-list-dialog"
        destroy-on-close
      >
        <div v-if="currentEmail" class="mail-dialog-header flex-between mb-6">
          <h3 class="email-title">
            <span class="text-primary">{{ currentEmail.email }}</span> 的同步箱
          </h3>
          <el-button 
            type="primary"
            size="small"
            @click="handleCheck(currentEmail)"
            :disabled="isEmailProcessing(currentEmail)"
            :icon="Refresh"
          >
            刷新邮件
          </el-button>
        </div>
        
        <el-table
          v-loading="loadingMails"
          :data="mailRecords"
          style="width: 100%"
          max-height="55vh"
          class="mail-list-table"
        >
          <el-table-column prop="subject" label="邮件主题" min-width="260" show-overflow-tooltip />
          <el-table-column prop="sender" label="发件人" min-width="180" show-overflow-tooltip />
          <el-table-column prop="folder" label="邮件来源" width="160">
            <template #default="scope">
              <el-tag 
                :type="scope.row.folder && scope.row.folder.toLowerCase().includes('junk') ? 'warning' : 'primary'"
                effect="light"
              >
                {{ scope.row.folder && scope.row.folder.toLowerCase().includes('junk') ? '垃圾箱: Junk Email' : '收件箱: INBOX' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="received_time" label="收取时间" width="170">
            <template #default="scope">
              <span class="time-field">{{ formatDate(scope.row.received_time) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="scope">
              <el-button 
                type="primary" 
                size="small" 
                @click="viewMailContent(scope.row)"
                :icon="Document"
              >
                查看
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-dialog>
      
      <!-- Mail Content Detail (Glassmorphism) -->
      <el-dialog
        v-model="mailContentDialogVisible"
        title="邮件详情"
        width="75%"
        top="8vh"
        class="mail-content-dialog"
      >
        <div v-if="selectedMail" class="mail-detail">
          <div class="mail-info-card">
            <div class="info-item flex">
              <span class="info-label">主题</span>
              <span class="info-value text-bold">{{ selectedMail.subject }}</span>
            </div>
            <div class="info-item flex">
              <span class="info-label">发件人</span>
              <span class="info-value">{{ selectedMail.sender }}</span>
            </div>
            <div class="info-item flex">
              <span class="info-label">时间</span>
              <span class="info-value">{{ formatDate(selectedMail.received_time) }}</span>
            </div>
            <div class="info-item flex">
              <span class="info-label">分类来源</span>
              <span class="info-value">
                <el-tag 
                  :type="selectedMail.folder && selectedMail.folder.toLowerCase().includes('junk') ? 'warning' : 'primary'"
                  effect="light"
                  size="small"
                >
                  {{ selectedMail.folder && selectedMail.folder.toLowerCase().includes('junk') ? '垃圾邮件 (Junk Email)' : '收件箱 (INBOX)' }}
                </el-tag>
              </span>
            </div>
          </div>
          
          <div class="mail-content-wrapper">
            <pre class="mail-content-text">{{ truncateContent(selectedMail.content) }}</pre>
          </div>
        </div>
      </el-dialog>
      
      <!-- Edit Dialog (Glassmorphism) -->
      <el-dialog
        v-model="editDialogVisible"
        title="编辑邮箱配置"
        width="500px"
        @close="resetEditForm"
      >
        <el-form
          ref="editFormRef"
          :model="editForm"
          :rules="editRules"
          label-width="90px"
          class="add-email-form"
        >
          <el-form-item label="邮箱地址" prop="email">
            <el-input v-model="editForm.email" />
          </el-form-item>
          
          <el-form-item label="安全密码" prop="password">
            <el-input 
              v-model="editForm.password" 
              type="password" 
              show-password
              @input="checkPasswordStrength"
            />
            <div class="password-strength-indicator" v-if="editForm.password && editForm.password !== '******'">
              <span class="indicator-label">强度</span>
              <el-progress 
                :percentage="passwordStrength" 
                :color="passwordStrengthColor"
                :format="passwordStrengthText"
                class="strength-bar"
              />
            </div>
          </el-form-item>
          
          <el-form-item label="邮箱类型">
            <el-tag :type="getMailTypeColor(editForm.mail_type)">
              {{ getMailTypeName(editForm.mail_type) }}
            </el-tag>
          </el-form-item>
          
          <template v-if="editForm.mail_type === 'imap'">
            <el-form-item label="服务器" prop="server">
              <el-input v-model="editForm.server" />
            </el-form-item>
            <el-form-item label="端口" prop="port">
              <el-input-number v-model="editForm.port" :min="1" :max="65535" controls-position="right" />
            </el-form-item>
            <el-form-item label="使用SSL" prop="use_ssl">
              <el-switch v-model="editForm.use_ssl" />
            </el-form-item>
          </template>
          
          <template v-if="editForm.mail_type === 'outlook'">
            <el-form-item label="Client ID" prop="client_id">
              <el-input v-model="editForm.client_id" />
            </el-form-item>
            <el-form-item label="Refresh Token" prop="refresh_token">
              <el-input v-model="editForm.refresh_token" />
            </el-form-item>
          </template>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="editDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="submitEditForm">保存更改</el-button>
          </span>
        </template>
      </el-dialog>

      <!-- Send Email Dialog (Glassmorphism) -->
      <el-dialog
        v-model="sendEmailDialogVisible"
        title="写邮件"
        width="560px"
        :close-on-click-modal="false"
        class="send-email-dialog"
        destroy-on-close
      >
        <el-form
          ref="sendEmailFormRef"
          :model="sendEmailForm"
          :rules="sendEmailRules"
          label-width="90px"
          class="add-email-form"
        >
          <el-form-item label="发件邮箱">
            <el-input :value="sendEmailForm.from" disabled />
          </el-form-item>

          <el-form-item label="收件人" prop="to">
            <el-input v-model="sendEmailForm.to" placeholder="recipient@example.com" />
          </el-form-item>

          <el-form-item label="主题" prop="subject">
            <el-input v-model="sendEmailForm.subject" placeholder="请输入邮件主题" />
          </el-form-item>

          <el-form-item label="正文内容" prop="body">
            <el-input
              v-model="sendEmailForm.body"
              type="textarea"
              :rows="12"
              placeholder="请输入邮件正文..."
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="sendEmailDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="handleSendEmail" :loading="sendingEmail">
              发送邮件
            </el-button>
          </span>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useEmailsStore } from '@/store/emails'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { 
  Delete, 
  Refresh, 
  Plus, 
  Download, 
  Document, 
  View,
  Hide
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const emailsStore = useEmailsStore()

// 状态
const loadingMails = ref(false)
const addEmailDialogVisible = ref(false)
const addEmailActiveTab = ref('single')
const mailContentDialogVisible = ref(false)
const mailListDialogVisible = ref(false)
const addingEmail = ref(false)
const importing = ref(false)
const sendEmailDialogVisible = ref(false)
const sendingEmail = ref(false)

// 引用
const addEmailFormRef = ref(null)
const batchImportFormRef = ref(null)
const sendEmailFormRef = ref(null)

const sendEmailForm = ref({
  id: null,
  from: '',
  to: '',
  subject: '',
  body: ''
})

const sendEmailRules = {
  to: [
    { required: true, message: '收件人邮箱不能为空', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  subject: [
    { required: true, message: '邮件主题不能为空', trigger: 'blur' }
  ],
  body: [
    { required: true, message: '邮件正文不能为空', trigger: 'blur' }
  ]
}

// 邮箱配置映射
const mailTypes = {
  outlook: { name: 'Outlook/Hotmail', color: 'primary' },
  imap: { name: 'IMAP邮箱', color: 'info' },
  gmail: { name: 'Gmail', color: 'danger' },
  qq: { name: 'QQ邮箱', color: 'success' }
}

const getMailTypeName = (type) => mailTypes[type]?.name || type
const getMailTypeColor = (type) => mailTypes[type]?.color || 'default'

// 表单初始值
const addEmailForm = ref({
  mail_type: 'outlook',
  email: '',
  password: '',
  client_id: '',
  refresh_token: '',
  server: '',
  port: 993,
  use_ssl: true
})

const batchImport = reactive({
  data: '',
  mailType: 'outlook'
})

// 表单验证
const batchImportRules = {
  data: [
    { required: true, message: '导入数据不能为空', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (!value) {
          callback()
          return
        }
        const lines = value.trim().split('\n')
        let hasError = false
        for (let i = 0; i < lines.length; i++) {
          const line = lines[i].trim()
          if (!line) continue
          if (batchImport.mailType === 'outlook') {
            const parts = line.split('----')
            if (parts.length !== 4) {
              hasError = true
              callback(new Error(`第 ${i + 1} 行格式错误，请使用"----"分隔邮箱、密码、客户端ID和RefreshToken`))
              break
            }
            if (!parts[0] || !parts[1] || !parts[2] || !parts[3]) {
              hasError = true
              callback(new Error(`第 ${i + 1} 行有空白字段，所有字段都必须填写`))
              break
            }
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(parts[0])) {
              hasError = true
              callback(new Error(`第 ${i + 1} 行邮箱格式不正确`))
              break
            }
          }
        }
        if (!hasError) callback()
      },
      trigger: 'blur'
    }
  ]
}

const addEmailRules = {
  mail_type: [{ required: true, message: '请选择邮箱类型', trigger: 'change' }],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  client_id: [{ required: true, trigger: 'blur', validator: (rule, value, callback) => {
    if (addEmailForm.value.mail_type === 'outlook' && !value) {
      callback(new Error('请输入Client ID'))
    } else {
      callback()
    }
  }}],
  refresh_token: [{ required: true, trigger: 'blur', validator: (rule, value, callback) => {
    if (addEmailForm.value.mail_type === 'outlook' && !value) {
      callback(new Error('请输入Refresh Token'))
    } else {
      callback()
    }
  }}],
  server: [{ required: true, trigger: 'blur', validator: (rule, value, callback) => {
    if (addEmailForm.value.mail_type === 'imap' && !value) {
      callback(new Error('请输入服务器地址'))
    } else {
      callback()
    }
  }}],
  port: [{ required: true, message: '请输入端口号', trigger: 'blur' }]
}

const selectedMail = ref(null)

// 计算属性
const emails = computed(() => emailsStore.emails)
const loading = computed(() => emailsStore.loading)
const currentEmail = computed(() => emailsStore.getEmailById(emailsStore.currentEmailId))
const mailRecords = computed(() => emailsStore.currentMailRecords)
const hasSelectedEmails = computed(() => emailsStore.hasSelectedEmails)

// 方法
const refreshEmails = async () => {
  try {
    await emailsStore.fetchEmails()
    ElMessage.success('刷新成功')
  } catch (error) {
    console.error('获取邮箱列表失败:', error)
    ElMessage.error('获取邮箱列表失败')
  }
}

const handleSelectionChange = (selection) => {
  if (Array.isArray(selection)) {
    emailsStore.selectedEmails = selection.map(item => item.id)
  } else {
    emailsStore.selectedEmails = []
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除邮箱 ${row.email} 吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      customClass: 'apple-box-confirm'
    }
  ).then(async () => {
    try {
      await emailsStore.deleteEmail(row.id)
      ElMessage.success('删除成功')
    } catch (error) {
      console.error('删除邮箱失败:', error)
      ElMessage.error('删除邮箱失败: ' + (error.message || '未知错误'))
    }
  }).catch(() => {})
}

const handleBatchDelete = () => {
  if (!hasSelectedEmails.value) return
  const count = emailsStore.selectedEmailsCount
  const emailIds = Array.isArray(emailsStore.selectedEmails) ? [...emailsStore.selectedEmails] : []
  
  ElMessageBox.confirm(
    `确定要彻底删除选中的 ${count} 个邮箱吗？此操作不可逆！`,
    '批量删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      customClass: 'apple-box-confirm'
    }
  ).then(async () => {
    try {
      await emailsStore.deleteEmails(emailIds)
      ElMessage.success(`已成功删除 ${count} 个邮箱`)
    } catch (error) {
      console.error('批量删除邮箱失败:', error)
      ElMessage.error('批量删除失败')
    }
  }).catch(() => {})
}

const handleCheck = async (row) => {
  try {
    const result = await emailsStore.checkEmail(row.id)
    if (result && result.status === 'processing') {
      ElMessage.warning(result.message || '邮箱正在同步中，请稍候...')
    } else {
      ElMessage.info(`正在检查邮箱 ${row.email}，请稍候...`)
    }
  } catch (error) {
    console.error('检查邮箱失败:', error)
    ElMessage.error('同步失败')
  }
}

const handleBatchCheck = async () => {
  if (!hasSelectedEmails.value) return
  const count = emailsStore.selectedEmailsCount
  const emailIds = Array.isArray(emailsStore.selectedEmails) ? [...emailsStore.selectedEmails] : []
  
  try {
    await emailsStore.checkEmails(emailIds)
    ElMessage.info(`正在同步 ${count} 个邮箱的最新邮件，可在通知栏查看进度...`)
  } catch (error) {
    console.error('批量同步邮箱失败:', error)
    ElMessage.error('批量同步失败')
  }
}

const handleViewMails = async (row) => {
  loadingMails.value = true
  try {
    emailsStore.currentEmailId = row.id
    await emailsStore.fetchMailRecords(row.id)
    mailListDialogVisible.value = true
  } catch (error) {
    console.error('获取邮件记录失败:', error)
    ElMessage.error('获取邮件记录失败')
  } finally {
    loadingMails.value = false
  }
}

const viewMailContent = (mail) => {
  if (!mail) return
  selectedMail.value = {
    ...mail,
    subject: mail.subject || '(无主题)',
    sender: mail.sender || '(未知发件人)',
    received_time: mail.received_time || new Date().toISOString(),
    content: mail.content || '(无正文内容)'
  }
  mailContentDialogVisible.value = true
}

const showAddEmailDialog = () => {
  resetAddEmailForm()
  addEmailDialogVisible.value = true
  addEmailActiveTab.value = 'single'
}

const handleAddOrImport = async () => {
  if (addEmailActiveTab.value === 'single') {
    await handleAddEmail()
  } else {
    await handleImport()
  }
}

const handleAddEmail = async () => {
  if (!addEmailFormRef.value) return
  try {
    await addEmailFormRef.value.validate()
    addingEmail.value = true
    const loading = ElLoading.service({
      lock: true,
      text: '正在加密存储并连通邮箱...',
      background: 'rgba(0, 0, 0, 0.7)'
    })
    
    const formData = {
      email: addEmailForm.value.email,
      password: addEmailForm.value.password,
      mail_type: addEmailForm.value.mail_type
    }
    
    if (addEmailForm.value.mail_type === 'outlook') {
      formData.client_id = addEmailForm.value.client_id
      formData.refresh_token = addEmailForm.value.refresh_token
    } else if (addEmailForm.value.mail_type === 'imap') {
      formData.server = addEmailForm.value.server
      formData.port = addEmailForm.value.port
      formData.use_ssl = addEmailForm.value.use_ssl
    }
    
    await emailsStore.addEmail(formData)
    addEmailDialogVisible.value = false
    ElMessage.success('添加邮箱成功')
    await refreshEmails()
  } catch (error) {
    console.error('添加邮箱失败:', error)
    ElMessage.error('添加邮箱失败: ' + (error.message || '网络连接超时'))
  } finally {
    addingEmail.value = false
    ElLoading.service().close()
  }
}

const handleImport = async () => {
  if (!batchImportFormRef.value) return
  try {
    await batchImportFormRef.value.validate()
    importing.value = true
    const importData = {
      data: batchImport.data.trim(),
      mail_type: batchImport.mailType
    }
    await emailsStore.importEmails(importData)
    ElMessage.info('正在解析并批量同步邮箱，请稍候...')
    setTimeout(async () => {
      await refreshEmails()
      ElMessage.success('批量导入队列完成')
      addEmailDialogVisible.value = false
    }, 2000)
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error('导入失败')
  } finally {
    importing.value = false
  }
}

const resetAddEmailForm = () => {
  addEmailForm.value = {
    mail_type: 'outlook',
    email: '',
    password: '',
    client_id: '',
    refresh_token: '',
    server: '',
    port: 993,
    use_ssl: true
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '未同步';
  return dayjs(dateString).format('YYYY-MM-DD HH:mm:ss');
}

const isEmailProcessing = (email) => {
  const status = emailsStore.getProcessingStatus(email.id)
  return status && status.progress >= 0 && status.progress < 100
}

const getEmailActionText = (email) => {
  return isEmailProcessing(email) ? '同步中...' : '同步收信'
}

const togglePasswordVisibility = async (row) => {
  if (row.showPassword) {
    row.showPassword = false
    return
  }
  if (!row.password || row.password === '******') {
    row.passwordLoading = true
    try {
      const response = await emailsStore.getEmailPassword(row.id)
      if (response && response.password) {
        row.password = response.password
      }
    } catch (error) {
      console.error('获取密码失败:', error)
      ElMessage.error('获取密码失败')
    } finally {
      row.passwordLoading = false
    }
  }
  row.showPassword = true
}

const truncateContent = (content) => {
  if (!content) return '(无邮件正文)'
  const maxLength = 1200
  if (content.length > maxLength) {
    return content.slice(0, maxLength) + '\n\n[...已自动截取超长邮件正文...]'
  }
  return content
}

const handleEdit = (email) => {
  const emailData = { ...email }
  if (emailData.mail_type === 'imap') {
    emailData.use_ssl = Boolean(emailData.use_ssl)
  }
  editForm.value = emailData
  editDialogVisible.value = true
}

const editDialogVisible = ref(false)
const editFormRef = ref(null)
const editForm = ref({
  id: null,
  email: '',
  password: '',
  mail_type: 'outlook',
  server: '',
  port: 993,
  use_ssl: true,
  client_id: '',
  refresh_token: ''
})

const passwordStrength = ref(0)
const passwordStrengthColor = computed(() => {
  if (passwordStrength.value < 40) return '#FF3B30'
  if (passwordStrength.value < 80) return '#FF9500'
  return '#34C759'
})

const passwordStrengthText = (percentage) => {
  if (percentage < 40) return '弱'
  if (percentage < 80) return '中'
  return '强'
}

const checkPasswordStrength = (password) => {
  if (!password) {
    passwordStrength.value = 0
    return
  }
  let strength = 0
  if (password.length >= 8) strength += 20
  if (/\d/.test(password)) strength += 20
  if (/[a-z]/.test(password)) strength += 20
  if (/[A-Z]/.test(password)) strength += 20
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength += 20
  passwordStrength.value = strength
}

const editRules = {
  email: [
    { required: true, message: '邮箱地址不能为空', trigger: 'blur' },
    { type: 'email', message: '格式不正确', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '密码不能为空', trigger: 'blur' }
  ],
  server: [{ required: true, trigger: 'blur', validator: (rule, value, callback) => {
    if (editForm.value.mail_type === 'imap' && !value) {
      callback(new Error('IMAP服务器地址不能为空'))
    } else {
      callback()
    }
  }}],
  port: [{ required: true, trigger: 'blur', validator: (rule, value, callback) => {
    if (editForm.value.mail_type === 'imap' && (!value || isNaN(value))) {
      callback(new Error('端口号不合法'))
    } else {
      callback()
    }
  }}],
  client_id: [{ required: true, trigger: 'blur', validator: (rule, value, callback) => {
    if (editForm.value.mail_type === 'outlook' && !value) {
      callback(new Error('Client ID不能为空'))
    } else {
      callback()
    }
  }}],
  refresh_token: [{ required: true, trigger: 'blur', validator: (rule, value, callback) => {
    if (editForm.value.mail_type === 'outlook' && !value) {
      callback(new Error('Refresh Token不能为空'))
    } else {
      callback()
    }
  }}]
}

const resetEditForm = () => {
  editForm.value = {
    id: null,
    email: '',
    password: '******',
    mail_type: 'outlook',
    client_id: '',
    refresh_token: '',
    server: '',
    port: 993,
    use_ssl: true
  }
}

const submitEditForm = async () => {
  if (!editFormRef.value) return
  try {
    await editFormRef.value.validate()
    const formData = { ...editForm.value }
    if (formData.password === '******') {
      delete formData.password
    }
    const loading = ElLoading.service({
      lock: true,
      text: '正在保存邮箱更改...',
      background: 'rgba(0, 0, 0, 0.7)'
    })
    
    await emailsStore.updateEmail(formData.id, formData)
    editDialogVisible.value = false
    await refreshEmails()
    ElMessage.success('邮箱更新成功')
  } catch (error) {
    console.error('更新邮箱失败:', error)
    ElMessage.error('更新失败')
  } finally {
    ElLoading.service().close()
  }
}

const showSendEmailDialog = (emailRow) => {
  sendEmailForm.value = {
    id: emailRow.id,
    from: emailRow.email,
    to: '',
    subject: '',
    body: ''
  }
  sendEmailDialogVisible.value = true
}

const handleSendEmail = async () => {
  if (!sendEmailFormRef.value) return
  try {
    await sendEmailFormRef.value.validate()
    sendingEmail.value = true
    
    const emailId = sendEmailForm.value.id
    const postData = {
      to: sendEmailForm.value.to,
      subject: sendEmailForm.value.subject,
      body: sendEmailForm.value.body
    }
    
    await emailsStore.sendEmail(emailId, postData)
    
    ElMessage.success('邮件发送成功！')
    sendEmailDialogVisible.value = false
  } catch (error) {
    console.error('发送邮件失败:', error)
    ElMessage.error(error.message || '发送邮件失败，请检查配置或凭据')
  } finally {
    sendingEmail.value = false
  }
}

onMounted(() => {
  emailsStore.initWebSocketListeners()
  refreshEmails()
})
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: var(--color-background);
}

.emails-container {
  padding: 40px 24px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.email-list-card {
  margin-bottom: 30px;
}

/* Badge for server configs - look like native capsule */
.server-badge {
  background-color: var(--border-color-light);
  border: 1px solid var(--border-color-base);
  color: var(--regular-text-color);
  padding: 4px 10px;
  border-radius: var(--border-radius-sm);
  display: inline-flex;
  align-items: center;
  font-family: monospace;
  font-size: 12px;
  font-weight: 500;
}

.port-label {
  color: var(--secondary-text-color);
  font-weight: 700;
}

.default-config-label {
  font-size: 13px;
  color: var(--secondary-text-color);
  font-style: italic;
}

.password-text {
  font-family: monospace;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.password-toggle-btn {
  font-size: 14px;
}

.time-field {
  color: var(--secondary-text-color);
  font-size: 13px;
  font-weight: 500;
}

.action-buttons {
  gap: 8px;
}

/* Mail Record dialog custom styles */
.mail-dialog-header {
  border-bottom: 1px solid var(--border-color-base);
  padding-bottom: 16px;
}

.email-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--primary-text-color);
}

/* Mail detail card */
.mail-info-card {
  background-color: var(--border-color-light);
  border: 1px solid var(--border-color-base);
  border-radius: var(--border-radius);
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  font-size: 14px;
}

.info-label {
  width: 70px;
  color: var(--secondary-text-color);
  font-weight: 600;
}

.info-value {
  color: var(--primary-text-color);
}

.info-value.text-bold {
  font-weight: 700;
}

/* Mail content display with monospace */
.mail-content-wrapper {
  margin-top: 20px;
}

.mail-content-text {
  background-color: var(--background-color-base);
  border: 1px solid var(--border-color-base);
  border-radius: var(--border-radius);
  color: var(--primary-text-color);
  font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
  font-size: 13.5px;
  line-height: 1.6;
  padding: 20px;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 45vh;
  overflow-y: auto;
}

/* Password strength */
.password-strength-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  margin-top: 8px;
}

.indicator-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--secondary-text-color);
}

.strength-bar {
  flex-grow: 1;
}

.import-help {
  background-color: var(--border-color-light);
  border: 1px solid var(--border-color-base);
  border-radius: var(--border-radius);
  padding: 12px 16px;
  font-size: 13px;
  line-height: 1.5;
  color: var(--regular-text-color);
  margin-bottom: 20px;
}

.import-help code {
  background-color: var(--border-color-base);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-weight: 600;
  color: var(--primary-color);
}
</style>