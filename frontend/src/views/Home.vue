<template>
  <div class="home-container">
    <el-header class="header">
      <div class="logo">智能面试系统</div>
      <el-button type="text" @click="logout">退出登录</el-button>
    </el-header>
    <el-container class="main">
      <el-aside width="200px" class="aside">
        <el-menu :default-active="activeMenu" class="menu">
          <el-menu-item index="1" @click="goPage('home')">
            <el-icon><House /></el-icon>首页
          </el-menu-item>
          <el-menu-item index="2" @click="goPage('resume')">
            <el-icon><Document /></el-icon>简历管理
          </el-menu-item>
          <el-menu-item index="3" @click="goPage('interview')">
            <el-icon><Microphone /></el-icon>开始面试
          </el-menu-item>
          <el-menu-item index="4" @click="goPage('result')">
            <el-icon><TrendCharts /></el-icon>面试结果
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main class="content">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card>
              <div class="stat-item">
                <div class="stat-icon" style="background: #e6f7ff;">
                  <el-icon><User /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ stats.resume_count }}</div>
                  <div class="stat-label">已上传简历</div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card>
              <div class="stat-item">
                <div class="stat-icon" style="background: #f6ffed;">
                  <el-icon><VideoCamera /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ stats.interview_count }}</div>
                  <div class="stat-label">已完成面试</div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card>
              <div class="stat-item">
                <div class="stat-icon" style="background: #fff7e6;">
                  <el-icon><Star /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ stats.avg_score }}</div>
                  <div class="stat-label">平均评分</div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <el-card class="chart-card" style="margin-top: 20px;">
          <div ref="chartRef" style="width: 100%; height: 300px;"></div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { House, Document, Microphone, TrendCharts, User, VideoCamera, Star } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import api from '../api'

const router = useRouter()
const activeMenu = ref('1')
const stats = ref({ resume_count: 0, interview_count: 0, avg_score: 0 })
const chartRef = ref(null)

const logout = () => {
  localStorage.clear()
  router.push('/login')
}

const goPage = (page) => {
  router.push('/' + page)
}

const loadData = async () => {
  try {
    const res = await api.get('/admin/stats')
    stats.value = res.data
  } catch (e) {
    // 模拟数据
    stats.value = { resume_count: 1, interview_count: 1, avg_score: 85 }
  }
}

const initChart = () => {
  const chart = echarts.init(chartRef.value)
  chart.setOption({
    title: { text: '面试评分趋势' },
    xAxis: { type: 'category', data: ['第1次', '第2次', '第3次'] },
    yAxis: { type: 'value', min: 0, max: 100 },
    series: [{
      data: [82, 85, 88],
      type: 'line',
      smooth: true,
      itemStyle: { color: '#667eea' }
    }]
  })
}

onMounted(() => {
  loadData()
  initChart()
})
</script>

<style scoped>
.home-container {
  height: 100vh;
}
.header {
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}
.logo {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}
.main {
  height: calc(100vh - 60px);
}
.aside {
  background: #fff;
}
.menu {
  border-right: none;
}
.content {
  background: #f5f7fa;
}
.stat-item {
  display: flex;
  align-items: center;
}
.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-right: 15px;
}
.stat-info .stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}
.stat-info .stat-label {
  font-size: 14px;
  color: #666;
}
</style>