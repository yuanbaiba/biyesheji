<template>
  <div class="home-container">
    <el-header class="header">
      <div class="logo">
        <el-icon><Cpu /></el-icon>
        智能面试系统
      </div>
      <div class="header-actions">
        <el-button type="text" @click="$router.push('/admin')" v-if="isAdmin">
          <el-icon><Setting /></el-icon>
          管理后台
        </el-button>
        <el-button type="text" @click="logout">
          <el-icon><SwitchButton /></el-icon>
          退出登录
        </el-button>
      </div>
    </el-header>

    <el-container class="main">
      <el-aside width="240px" class="aside">
        <el-menu :default-active="activeMenu" class="menu" router>
          <el-menu-item index="home">
            <el-icon><House /></el-icon>
            <template #title>首页概览</template>
          </el-menu-item>
          <el-menu-item index="resume">
            <el-icon><Document /></el-icon>
            <template #title>简历管理</template>
          </el-menu-item>
          <el-menu-item index="interview">
            <el-icon><Microphone /></el-icon>
            <template #title>智能面试</template>
          </el-menu-item>
          <el-menu-item index="result">
            <el-icon><TrendCharts /></el-icon>
            <template #title>面试结果</template>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-main class="content">
        <div class="welcome-section">
          <h1 class="welcome-title">
            欢迎使用智能面试系统
          </h1>
          <p class="welcome-subtitle">
            基于大语言模型的多智能体协作面试平台，为您提供专业、个性化的面试体验
          </p>
        </div>

        <el-row :gutter="20" class="stats-row">
          <el-col :xs="24" :sm="12" :md="6">
            <el-card class="stat-card" shadow="hover">
              <div class="stat-item">
                <div class="stat-icon resume-icon">
                  <el-icon><DocumentAdd /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ stats.resumeCount }}</div>
                  <div class="stat-label">简历数量</div>
                  <div class="stat-desc">已上传的简历</div>
                </div>
              </div>
            </el-card>
          </el-col>

          <el-col :xs="24" :sm="12" :md="6">
            <el-card class="stat-card" shadow="hover">
              <div class="stat-item">
                <div class="stat-icon interview-icon">
                  <el-icon><VideoCamera /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ stats.interviewCount }}</div>
                  <div class="stat-label">面试次数</div>
                  <div class="stat-desc">已完成的面试</div>
                </div>
              </div>
            </el-card>
          </el-col>

          <el-col :xs="24" :sm="12" :md="6">
            <el-card class="stat-card" shadow="hover">
              <div class="stat-item">
                <div class="stat-icon score-icon">
                  <el-icon><Star /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ stats.averageScore }}</div>
                  <div class="stat-label">平均评分</div>
                  <div class="stat-desc">综合表现评分</div>
                </div>
              </div>
            </el-card>
          </el-col>

          <el-col :xs="24" :sm="12" :md="6">
            <el-card class="stat-card" shadow="hover">
              <div class="stat-item">
                <div class="stat-icon ai-icon">
                  <el-icon><Cpu /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ stats.aiInteractions }}</div>
                  <div class="stat-label">AI交互</div>
                  <div class="stat-desc">智能体协作次数</div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="20" class="actions-row">
          <el-col :xs="24" :md="12">
            <el-card class="action-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <el-icon><DocumentAdd /></el-icon>
                  快速开始
                </div>
              </template>
              <div class="action-content">
                <p>上传简历，开启智能面试之旅</p>
                <el-button type="primary" size="large" @click="$router.push('/resume')">
                  <el-icon><Plus /></el-icon>
                  上传简历
                </el-button>
              </div>
            </el-card>
          </el-col>

          <el-col :xs="24" :md="12">
            <el-card class="action-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <el-icon><Microphone /></el-icon>
                  开始面试
                </div>
              </template>
              <div class="action-content">
                <p>体验AI多智能体协作面试</p>
                <el-button type="success" size="large" @click="$router.push('/interview')">
                  <el-icon><VideoPlay /></el-icon>
                  开始面试
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  House, Document, Microphone, TrendCharts, DocumentAdd,
  VideoCamera, Star, SwitchButton, Setting, Cpu
} from '@element-plus/icons-vue'
import { useUserStore, useResumeStore } from '../stores'

const router = useRouter()
const userStore = useUserStore()
const resumeStore = useResumeStore()

const activeMenu = ref('home')
const isAdmin = ref(false)

const stats = ref({
  resumeCount: 0,
  interviewCount: 0,
  averageScore: 0,
  aiInteractions: 0
})

const logout = () => {
  userStore.logout()
  router.push('/login')
}

const checkAdmin = async () => {
  try {
    const res = await fetch('/api/auth/me', {
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    })
    if (res.ok) {
      const data = await res.json()
      isAdmin.value = data.is_admin || false
    }
  } catch (error) {
    console.error('检查管理员状态失败:', error)
  }
}

const loadStats = async () => {
  try {
    const resumeRes = await fetch('/api/resume/list', {
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    })
    if (resumeRes.ok) {
      const resumeData = await resumeRes.json()
      // 处理API响应格式 {code: 200, data: [...]} 或直接返回数组
      const resumeList = resumeData.data || resumeData || []
      stats.value.resumeCount = Array.isArray(resumeList) ? resumeList.length : 0
    }

    const interviewRes = await fetch('/api/interview/list?user_id=' + userStore.userId, {
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    })
    if (interviewRes.ok) {
      const interviewData = await interviewRes.json()
      // 处理API响应格式 {code: 200, data: [...]} 或直接返回数组
      const interviewList = interviewData.data || interviewData || []
      if (Array.isArray(interviewList)) {
        // 只统计已完成的面试数量
        const completedList = interviewList.filter(i => i.status === '已完成')
        stats.value.interviewCount = completedList.length
        // 计算已完成面试的平均分（只统计有分数的面试）
        const scoredList = completedList.filter(i => i.total_score !== null && i.total_score !== undefined)
        if (scoredList.length > 0) {
          const totalScore = scoredList.reduce((sum, i) => sum + (i.total_score || 0), 0)
          stats.value.averageScore = Math.round(totalScore / scoredList.length)
        } else {
          stats.value.averageScore = 0
        }
        // AI交互次数 = 已回答的问题总数
        stats.value.aiInteractions = scoredList.reduce((sum, i) => sum + (i.answered_num || 0), 0)
      }
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(() => {
  checkAdmin()
  loadStats()
})
</script>

<style scoped>
.home-container {
  height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.logo {
  font-size: 20px;
  font-weight: 700;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo .el-icon {
  color: #667eea;
}

.main {
  height: calc(100vh - 64px);
}

.aside {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-right: 1px solid rgba(0, 0, 0, 0.1);
}

.menu {
  border-right: none;
  background: transparent;
}

.content {
  background: transparent;
  padding: 24px;
}

.welcome-section {
  margin-bottom: 32px;
  text-align: center;
}

.welcome-title {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.wave-icon {
  color: #67c23a;
  animation: wave 2s ease-in-out infinite;
}

@keyframes wave {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(20deg); }
  75% { transform: rotate(-10deg); }
}

.welcome-subtitle {
  font-size: 16px;
  color: #666;
  line-height: 1.6;
  max-width: 600px;
  margin: 0 auto;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  transition: all 0.3s ease;
  border: none;
  border-radius: 12px;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.resume-icon {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.interview-icon {
  background: linear-gradient(135deg, #f093fb, #f5576c);
}

.score-icon {
  background: linear-gradient(135deg, #4facfe, #00f2fe);
}

.ai-icon {
  background: linear-gradient(135deg, #43e97b, #38f9d7);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin: 4px 0;
}

.stat-desc {
  font-size: 12px;
  color: #999;
}

.actions-row {
  margin-bottom: 24px;
}

.action-card {
  height: 300px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 18px;
  color: #333;
}

.action-content {
  text-align: center;
  padding: 20px 0;
}

.action-content p {
  color: #666;
  margin-bottom: 20px;
  font-size: 14px;
}

.action-content .el-button {
  padding: 20px 40px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
}
</style>
