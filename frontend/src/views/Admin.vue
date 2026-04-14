<template>
  <div class="admin-container">
    <el-header class="header">
      <div class="logo">
        <el-icon><Setting /></el-icon>
        管理后台
      </div>
      <div class="header-right">
        <span class="username">{{ username }}</span>
        <el-button type="text" @click="logout">退出登录</el-button>
      </div>
    </el-header>
    <el-container class="main">
      <el-aside width="220px" class="aside">
        <el-menu :default-active="currentMenu" @select="handleMenuSelect" class="menu">
          <el-menu-item index="dashboard">
            <el-icon><Odometer /></el-icon>
            <span>数据概览</span>
          </el-menu-item>
          <el-menu-item index="jobs">
            <el-icon><Briefcase /></el-icon>
            <span>职位管理</span>
          </el-menu-item>
          <el-menu-item index="users">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          <el-menu-item index="interviews">
            <el-icon><Microphone /></el-icon>
            <span>面试记录</span>
          </el-menu-item>
          <el-menu-item index="back">
            <el-icon><ArrowLeft /></el-icon>
            <span>返回首页</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main class="content">
        <!-- 数据概览 -->
        <div v-if="currentMenu === 'dashboard'" class="dashboard">
          <h2>系统数据概览</h2>
          <el-row :gutter="20" class="stats-row">
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-icon users"><el-icon><User /></el-icon></div>
                <div class="stat-info">
                  <div class="stat-value">{{ stats.totalUsers }}</div>
                  <div class="stat-label">总用户数</div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-icon jobs"><el-icon><Briefcase /></el-icon></div>
                <div class="stat-info">
                  <div class="stat-value">{{ stats.totalJobs }}</div>
                  <div class="stat-label">职位数量</div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-icon interviews"><el-icon><Microphone /></el-icon></div>
                <div class="stat-info">
                  <div class="stat-value">{{ stats.totalInterviews }}</div>
                  <div class="stat-label">面试次数</div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-icon resumes"><el-icon><Document /></el-icon></div>
                <div class="stat-info">
                  <div class="stat-value">{{ stats.totalResumes }}</div>
                  <div class="stat-label">简历数量</div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <!-- 职位管理 -->
        <div v-if="currentMenu === 'jobs'" class="jobs-management">
          <div class="page-header">
            <h2>职位管理</h2>
            <el-button type="primary" @click="openAddJobDialog">
              <el-icon><Plus /></el-icon>
              添加职位
            </el-button>
          </div>
          <el-table :data="jobs" stripe class="data-table">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="title" label="职位名称" min-width="120" />
            <el-table-column prop="job_type" label="职位类型" width="120">
              <template #default="{ row }">
                <el-tag>{{ row.job_type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="department" label="部门" width="100" />
            <el-table-column prop="salary_range" label="薪资范围" width="120" />
            <el-table-column prop="location" label="工作地点" width="120" />
            <el-table-column prop="headcount" label="人数" width="60" />
            <el-table-column prop="is_active" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'" @click="toggleJobStatus(row)" style="cursor:pointer;">
                  {{ row.is_active ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="160">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="editJob(row)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteJob(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 用户管理 -->
        <div v-if="currentMenu === 'users'" class="users-management">
          <div class="page-header">
            <h2>用户管理</h2>
            <el-button type="primary" @click="showUserDialog = true">
              <el-icon><Plus /></el-icon>
              添加管理员
            </el-button>
          </div>
          <el-table :data="users" stripe class="data-table">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="username" label="用户名" width="120" />
            <el-table-column prop="email" label="邮箱" min-width="180" />
            <el-table-column prop="full_name" label="姓名" width="100" />
            <el-table-column prop="is_admin" label="角色" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_admin ? 'warning' : 'success'">
                  {{ row.is_admin ? '管理员' : '用户' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="注册时间" width="160">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button
                  size="small"
                  :type="row.is_admin ? 'info' : 'warning'"
                  @click="toggleAdmin(row)"
                >
                  {{ row.is_admin ? '取消管理员' : '设为管理员' }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 面试记录 -->
        <div v-if="currentMenu === 'interviews'" class="interviews-management">
          <div class="page-header">
            <h2>面试记录</h2>
          </div>
          <el-table :data="interviews" stripe class="data-table">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="username" label="用户名" width="100" />
            <el-table-column prop="resume_name" label="简历" min-width="120" show-overflow-tooltip />
            <el-table-column prop="job_title" label="应聘职位" width="120">
              <template #default="{ row }">
                <el-tag type="primary">{{ row.job_type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status_code)">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="total_score" label="得分" width="80">
              <template #default="{ row }">
                <span v-if="row.total_score > 0">{{ row.total_score }}分</span>
                <span v-else-if="row.status_code === 0 || row.status === '进行中'" class="text-warning">面试中</span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="question_num" label="题目数" width="80">
              <template #default="{ row }">
                {{ row.answered_num || 0 }}/{{ row.question_num }}
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="开始时间" width="160">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="viewInterviewDetail(row)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-main>
    </el-container>

    <!-- 添加/编辑职位对话框 -->
    <el-dialog v-model="showJobDialog" :title="editingJob ? '编辑职位' : '添加职位'" width="600px">
      <el-form :model="jobForm" label-width="100px">
        <el-form-item label="职位名称" required>
          <el-input v-model="jobForm.title" placeholder="请输入职位名称" />
        </el-form-item>
        <el-form-item label="职位类型" required>
          <el-select v-model="jobForm.job_type" placeholder="请选择职位类型">
            <el-option label="软件工程师" value="软件工程师" />
            <el-option label="产品经理" value="产品经理" />
            <el-option label="数据科学家" value="数据科学家" />
            <el-option label="UI设计师" value="UI设计师" />
            <el-option label="运营专员" value="运营专员" />
            <el-option label="市场专员" value="市场专员" />
            <el-option label="人力资源" value="人力资源" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="部门">
          <el-input v-model="jobForm.department" placeholder="请输入部门" />
        </el-form-item>
        <el-form-item label="薪资范围">
          <el-input v-model="jobForm.salary_range" placeholder="如: 15k-25k" />
        </el-form-item>
        <el-form-item label="工作地点">
          <el-input v-model="jobForm.location" placeholder="请输入工作地点" />
        </el-form-item>
        <el-form-item label="招聘人数">
          <el-input-number v-model="jobForm.headcount" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="jobForm.is_active" />
        </el-form-item>
        <el-form-item label="职位描述">
          <el-input v-model="jobForm.description" type="textarea" :rows="4" placeholder="请输入职位描述" />
        </el-form-item>
        <el-form-item label="任职要求">
          <el-input v-model="jobForm.requirements" type="textarea" :rows="4" placeholder="请输入任职要求" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showJobDialog = false">取消</el-button>
        <el-button type="primary" @click="saveJob" :loading="loading">保存</el-button>
      </template>
    </el-dialog>

    <!-- 添加管理员对话框 -->
    <el-dialog v-model="showUserDialog" title="添加管理员" width="400px">
      <el-form :model="adminForm" label-width="80px">
        <el-form-item label="用户名" required>
          <el-input v-model="adminForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" required>
          <el-input v-model="adminForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="密码" required>
          <el-input v-model="adminForm.password" type="password" placeholder="请输入密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUserDialog = false">取消</el-button>
        <el-button type="primary" @click="createAdmin" :loading="loading">创建</el-button>
      </template>
    </el-dialog>

    <!-- 面试详情对话框 -->
    <el-dialog v-model="showInterviewDialog" title="面试详情" width="700px">
      <div v-if="interviewDetail" class="interview-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="面试ID">{{ interviewDetail.id }}</el-descriptions-item>
          <el-descriptions-item label="应聘者">{{ interviewDetail.username }}</el-descriptions-item>
          <el-descriptions-item label="简历">{{ interviewDetail.resume_name }}</el-descriptions-item>
          <el-descriptions-item label="应聘职位">
            <el-tag type="primary">{{ interviewDetail.job_type }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(interviewDetail.status_code)">
              {{ interviewDetail.status }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="总分">{{ interviewDetail.total_score > 0 ? interviewDetail.total_score + '分' : interviewDetail.total_score === 0 ? '0分' : '-' }}</el-descriptions-item>
          <el-descriptions-item label="完成进度">{{ interviewDetail.answered_num || 0 }}/{{ interviewDetail.question_num }}题</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatDate(interviewDetail.created_at) }}</el-descriptions-item>
        </el-descriptions>
        <div v-if="interviewDetail.resume_content" class="resume-preview">
          <h4>简历内容预览</h4>
          <el-card>
            <p class="resume-text">{{ interviewDetail.resume_content }}</p>
          </el-card>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Setting,
  Odometer,
  Briefcase,
  User,
  Microphone,
  ArrowLeft,
  Plus,
  Document
} from '@element-plus/icons-vue'
import api from '../api'

const router = useRouter()

const currentMenu = ref('dashboard')
const loading = ref(false)
const username = ref('')

// 统计数据
const stats = ref({
  totalUsers: 0,
  totalJobs: 0,
  totalInterviews: 0,
  totalResumes: 0
})

// 职位管理
const jobs = ref([])
const showJobDialog = ref(false)
const editingJob = ref(null)
const jobForm = ref({
  title: '',
  job_type: '',
  department: '',
  salary_range: '',
  location: '',
  headcount: 1,
  is_active: true,
  description: '',
  requirements: ''
})

// 用户管理
const users = ref([])
const showUserDialog = ref(false)
const adminForm = ref({
  username: '',
  email: '',
  password: ''
})

// 面试记录
const interviews = ref([])
const showInterviewDialog = ref(false)
const interviewDetail = ref(null)

onMounted(() => {
  checkAdmin()
  loadStats()
})

const checkAdmin = async () => {
  try {
    const res = await api.get('/auth/me')
    const userData = res.data || res
    if (!userData.is_admin) {
      ElMessage.error('需要管理员权限')
      router.push('/')
      return
    }
    username.value = userData.username
  } catch (error) {
    router.push('/login')
  }
}

const loadStats = async () => {
  try {
    // 加载职位列表获取职位数
    const jobsRes = await api.get('/jobs')
    const jobsList = jobsRes.data?.data || jobsRes.data || []
    stats.value.totalJobs = jobsList.length || 0

    // 获取用户数量
    try {
      const usersRes = await api.get('/admin/users')
      const usersList = usersRes.data?.data || usersRes.data || []
      stats.value.totalUsers = usersList.length || 0
    } catch (e) {
      stats.value.totalUsers = 0
    }

    // 获取面试数量
    try {
      const interviewsRes = await api.get('/admin/interviews')
      const interviewsList = interviewsRes.data?.data || interviewsRes.data || []
      stats.value.totalInterviews = interviewsList.length || 0
    } catch (e) {
      stats.value.totalInterviews = 0
    }

    // 获取简历数量
    try {
      const resumeRes = await api.get('/admin/resumes')
      const resumeList = resumeRes.data?.data || resumeRes.data || []
      stats.value.totalResumes = resumeList.length || 0
    } catch (e) {
      stats.value.totalResumes = 0
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const handleMenuSelect = (index) => {
  if (index === 'back') {
    router.push('/')
    return
  }
  currentMenu.value = index
  if (index === 'jobs') loadJobs()
  if (index === 'users') loadUsers()
  if (index === 'interviews') loadInterviews()
}

const loadJobs = async () => {
  try {
    // 管理员查看所有职位，包括禁用的
    const res = await api.get('/jobs', { params: { show_all: 'true' } })
    jobs.value = res.data?.data || res.data || []
  } catch (error) {
    console.error('加载职位失败:', error)
  }
}

const loadUsers = async () => {
  try {
    const res = await api.get('/admin/users')
    users.value = res.data?.data || res.data || []
  } catch (error) {
    console.error('加载用户列表失败:', error)
    ElMessage.error('加载用户列表失败')
  }
}

const loadInterviews = async () => {
  try {
    const res = await api.get('/admin/interviews')
    interviews.value = res.data?.data || res.data || []
  } catch (error) {
    console.error('加载面试记录失败:', error)
    ElMessage.error('加载面试记录失败')
  }
}

const editJob = (job) => {
  editingJob.value = job
  jobForm.value = { ...job }
  showJobDialog.value = true
}

const openAddJobDialog = () => {
  editingJob.value = null
  jobForm.value = {
    title: '',
    job_type: '',
    department: '',
    salary_range: '',
    location: '',
    headcount: 1,
    is_active: true,
    description: '',
    requirements: ''
  }
  showJobDialog.value = true
}

const saveJob = async () => {
  if (!jobForm.value.title || !jobForm.value.job_type) {
    ElMessage.warning('请填写必填项')
    return
  }

  loading.value = true
  try {
    if (editingJob.value) {
      await api.put(`/jobs/${editingJob.value.id}`, jobForm.value)
      ElMessage.success('职位更新成功')
    } else {
      await api.post('/jobs', jobForm.value)
      ElMessage.success('职位创建成功')
    }
    showJobDialog.value = false
    loadJobs()
    loadStats()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    loading.value = false
  }
}

const deleteJob = async (job) => {
  try {
    await ElMessageBox.confirm(`确定要删除职位 "${job.title}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await api.delete(`/jobs/${job.id}`)
    ElMessage.success('删除成功')
    loadJobs()
    loadStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

const toggleJobStatus = async (job) => {
  try {
    await ElMessageBox.confirm(
      `确定要${job.is_active ? '禁用' : '启用'}职位 "${job.title}" 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await api.put(`/jobs/${job.id}`, { is_active: !job.is_active })
    ElMessage.success(`职位已${job.is_active ? '禁用' : '启用'}`)
    loadJobs()
    loadStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    }
  }
}

const createAdmin = async () => {
  if (!adminForm.value.username || !adminForm.value.email || !adminForm.value.password) {
    ElMessage.warning('请填写所有字段')
    return
  }

  loading.value = true
  try {
    await api.post('/auth/register', adminForm.value)
    ElMessage.success('管理员创建成功')
    showUserDialog.value = false
    adminForm.value = { username: '', email: '', password: '' }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '创建失败')
  } finally {
    loading.value = false
  }
}

const toggleAdmin = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要${user.is_admin ? '取消' : '设置'}用户 "${user.username}" 的管理员权限吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    const res = await api.put(`/admin/users/${user.id}/toggle-admin`)
    ElMessage.success(res.data?.message || '操作成功')
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    }
  }
}

const viewInterviewDetail = async (interview) => {
  showInterviewDialog.value = true
  interviewDetail.value = interview
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const getStatusType = (status) => {
  // status 可能是数字 0/1 或字符串
  if (status === 1 || status === '已完成' || status === 'completed') return 'success'
  if (status === 0 || status === '进行中' || status === 'in_progress') return 'warning'
  return 'info'
}

const getStatusText = (status) => {
  const texts = {
    completed: '已完成',
    in_progress: '进行中',
    pending: '待开始'
  }
  return texts[status] || status
}

const logout = () => {
  localStorage.clear()
  router.push('/login')
}
</script>

<style scoped>
.admin-container {
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.logo {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.username {
  color: #666;
}

.main {
  height: calc(100vh - 60px);
}

.aside {
  background: rgba(255, 255, 255, 0.95);
}

.menu {
  border-right: none;
}

.content {
  background: rgba(245, 247, 250, 0.8);
  overflow-y: auto;
}

.dashboard h2,
.page-header h2 {
  color: #333;
  margin-bottom: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.stats-row {
  margin-top: 20px;
}

.stat-card {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
}

.stat-icon.users { background: linear-gradient(135deg, #667eea, #764ba2); }
.stat-icon.jobs { background: linear-gradient(135deg, #f093fb, #f5576c); }
.stat-icon.interviews { background: linear-gradient(135deg, #4facfe, #00f2fe); }
.stat-icon.resumes { background: linear-gradient(135deg, #43e97b, #38f9d7); }

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.data-table {
  background: white;
  border-radius: 8px;
}

.interview-detail {
  padding: 10px 0;
}

.evaluation-section {
  margin-top: 20px;
}

.evaluation-section h4 {
  margin-bottom: 10px;
  color: #333;
}

.resume-preview {
  margin-top: 20px;
}

.resume-preview h4 {
  margin-bottom: 10px;
  color: #333;
}

.resume-text {
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
  font-size: 13px;
  line-height: 1.6;
  color: #666;
}

.text-warning {
  color: #E6A23C;
  font-size: 12px;
}
</style>
