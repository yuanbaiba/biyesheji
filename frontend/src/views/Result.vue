<template>
  <div class="result-container">
    <el-header class="header">
      <div class="logo">智能面试系统</div>
      <el-button type="text" @click="logout">退出登录</el-button>
    </el-header>
    <el-container class="main">
      <el-aside width="200px" class="aside">
        <el-menu :default-active="'4'" class="menu">
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
        <el-card v-loading="loading">

          <!-- 历史面试列表 -->
          <div class="history-section">
            <h2>面试记录</h2>
            <el-select
              v-model="selectedInterviewId"
              placeholder="请选择面试记录"
              class="interview-selector"
              @change="onInterviewSelect"
            >
              <el-option
                v-for="item in interviewList"
                :key="item.id"
                :label="`${item.job_type} - ${formatDate(item.created_at)}${item.total_score !== null ? ' - ' + item.total_score + '分' : ''}`"
                :value="item.id"
              >
                <div class="interview-option">
                  <span class="job-type">{{ item.job_type }}</span>
                  <span class="interview-date">{{ formatDate(item.created_at) }}</span>
                  <span class="score-mini" v-if="item.total_score !== null">{{ item.total_score }}分</span>
                  <el-tag :type="item.status === '已完成' ? 'success' : 'warning'" size="small">
                    {{ item.status }}
                  </el-tag>
                </div>
              </el-option>
            </el-select>
          </div>

          <!-- 当前选中的面试结果 -->
          <div v-if="interviewData.id" class="result-section">
            <div class="result-header">
              <h2>面试结果详情</h2>
              <el-tag :type="interviewData.status === '已完成' ? 'success' : 'warning'" size="large">
                {{ interviewData.status }}
              </el-tag>
            </div>

            <!-- 评分卡片：仅在面试完成且有分数时显示 -->
            <el-row :gutter="20" style="margin-top: 20px;" v-if="interviewData.status === '已完成' && overallScore > 0">
              <el-col :span="12">
                <el-card>
                  <div class="score-card">
                    <div class="score-circle" :class="getScoreClass(overallScore)">
                      <span class="score-text">{{ overallScore }}</span>
                      <span class="score-unit">/100</span>
                    </div>
                    <div class="score-desc">
                      <p>综合评分</p>
                      <p>{{ getScoreDescription(overallScore) }}</p>
                    </div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card>
                  <div ref="scoreChart" style="width: 100%; height: 150px;"></div>
                </el-card>
              </el-col>
            </el-row>

            <!-- 进行中提示 -->
            <el-alert
              v-if="interviewData.status === '进行中'"
              title="面试进行中"
              type="warning"
              description="请完成所有面试问题后查看评分结果"
              :closable="false"
              style="margin-top: 20px;"
              show-icon>
              <template #default>
                <span>已回答 {{ interviewData.answers?.length || 0 }} / {{ interviewData.question_num }} 个问题</span>
              </template>
            </el-alert>

            <!-- 简历信息 -->
            <el-card style="margin-top: 20px;" v-if="interviewData.resume">
              <h3>简历信息</h3>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="简历名称">{{ interviewData.resume.file_name || '未知' }}</el-descriptions-item>
                <el-descriptions-item label="求职者">{{ interviewData.resume.name || '未知' }}</el-descriptions-item>
              </el-descriptions>
            </el-card>

            <!-- 问题详情 -->
            <el-card style="margin-top: 20px;" v-if="interviewData.answers && interviewData.answers.length > 0">
              <h3>问题详情</h3>
              <el-collapse>
                <el-collapse-item
                  v-for="(answer, index) in interviewData.answers"
                  :key="index"
                >
                  <template #title>
                    <div class="question-title">
                      <span>问题 {{ index+1 }}</span>
                      <el-tag :type="getScoreTagType(answer.evaluation?.overall_score)" size="small">
                        {{ answer.evaluation?.overall_score || 0 }}/100
                      </el-tag>
                    </div>
                  </template>
                  <div class="answer-detail">
                    <p><strong>问题：</strong>{{ answer.question }}</p>
                    <p><strong>你的回答：</strong>{{ answer.answer }}</p>
                    <p v-if="answer.is_voice"><el-tag type="info">语音回答</el-tag></p>
                    <div v-if="answer.evaluation" class="evaluation-section">
                      <p><strong>综合评分：</strong>{{ answer.evaluation.overall_score }}/100</p>
                      <el-descriptions :column="2" size="small" border>
                        <el-descriptions-item label="相关性">{{ answer.evaluation.scores?.relevance ?? 0 }}/20</el-descriptions-item>
                        <el-descriptions-item label="准确性">{{ answer.evaluation.scores?.accuracy ?? 0 }}/20</el-descriptions-item>
                        <el-descriptions-item label="深度">{{ answer.evaluation.scores?.depth ?? 0 }}/20</el-descriptions-item>
                        <el-descriptions-item label="完整性">{{ answer.evaluation.scores?.completeness ?? 0 }}/15</el-descriptions-item>
                        <el-descriptions-item label="表达">{{ answer.evaluation.scores?.expression ?? 0 }}/15</el-descriptions-item>
                        <el-descriptions-item label="证据">{{ answer.evaluation.scores?.evidence ?? 0 }}/10</el-descriptions-item>
                      </el-descriptions>
                      <p><strong>AI评价：</strong>{{ answer.evaluation.feedback }}</p>
                      <div v-if="answer.evaluation.strengths && answer.evaluation.strengths.length > 0" class="strengths-section">
                        <p><strong>优点：</strong></p>
                        <ul>
                          <li v-for="strength in answer.evaluation.strengths" :key="strength">{{ strength }}</li>
                        </ul>
                      </div>
                      <div v-if="answer.evaluation.suggestions && answer.evaluation.suggestions.length > 0" class="suggestions-section">
                        <p><strong>改进建议：</strong></p>
                        <ul>
                          <li v-for="suggestion in answer.evaluation.suggestions" :key="suggestion">{{ suggestion }}</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </el-card>
          </div>

          <div v-else class="no-data">
            <el-empty description="暂无面试数据">
              <el-button type="primary" @click="goPage('interview')">开始新面试</el-button>
            </el-empty>
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { House, Document, Microphone, TrendCharts } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import api from '../api'

const router = useRouter()
const loading = ref(false)
const interviewList = ref([])
const selectedInterviewId = ref(null)
const interviewData = ref({})
const scoreChart = ref(null)
let chartInstance = null

const overallScore = computed(() => {
  // 优先使用后端返回的 total_score（100分制）
  if (interviewData.value?.total_score !== null &&
      interviewData.value?.total_score !== undefined) {
    return interviewData.value.total_score
  }
  // 如果没有，则从前端计算各题平均分（兼容旧数据）
  if (!interviewData.value?.answers || interviewData.value.answers.length === 0) return 0
  const scores = interviewData.value.answers
    .map(ans => ans.evaluation?.overall_score || 0)
    .filter(score => score > 0)
  return scores.length > 0 ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0
})

const getScoreClass = (score) => {
  if (score >= 90) return 'score-excellent'
  if (score >= 75) return 'score-good'
  if (score >= 60) return 'score-average'
  return 'score-poor'
}

const getScoreTagType = (score) => {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'danger'
}

const getScoreDescription = (score) => {
  if (score === 0) return '暂无评分'
  if (score >= 90) return '表现优秀！'
  if (score >= 75) return '表现良好'
  if (score >= 60) return '表现一般'
  if (score >= 40) return '需要改进'
  return '需要大幅改进'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const logout = () => {
  localStorage.clear()
  router.push('/login')
}

const goPage = (page) => {
  router.push('/' + page)
}

const loadInterviewList = async () => {
  loading.value = true
  try {
    const userId = localStorage.getItem('user_id')
    const res = await api.get(`/interview/list?user_id=${userId}`)
    interviewList.value = res.data?.data || res.data || []
    // 按时间倒序排列，最新的在前
    interviewList.value.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))

    if (interviewList.value.length > 0) {
      selectedInterviewId.value = interviewList.value[0].id
      await loadInterviewDetail(selectedInterviewId.value)
    } else {
      interviewData.value = {}
    }
  } catch (e) {
    console.error('加载面试列表失败:', e)
    interviewList.value = []
  } finally {
    loading.value = false
  }
}

const loadInterviewDetail = async (interviewId) => {
  loading.value = true
  try {
    const userId = localStorage.getItem('user_id')
    const res = await api.get(`/interview/${interviewId}?user_id=${userId}`)
    interviewData.value = res.data?.data || res.data || {}

    await nextTick()
    initChart()
  } catch (e) {
    console.error('加载面试详情失败:', e)
    interviewData.value = {}
  } finally {
    loading.value = false
  }
}

const onInterviewSelect = (interviewId) => {
  if (interviewId) {
    loadInterviewDetail(interviewId)
  }
}

const initChart = () => {
  if (!scoreChart.value) return

  if (chartInstance) {
    chartInstance.dispose()
  }

  if (!interviewData.value.answers || interviewData.value.answers.length === 0) return

  chartInstance = echarts.init(scoreChart.value)
  const answers = interviewData.value.answers

  const avgScores = {
    relevance: answers.reduce((sum, ans) => sum + (ans.evaluation?.scores?.relevance || 0), 0) / answers.length,
    accuracy: answers.reduce((sum, ans) => sum + (ans.evaluation?.scores?.accuracy || 0), 0) / answers.length,
    depth: answers.reduce((sum, ans) => sum + (ans.evaluation?.scores?.depth || 0), 0) / answers.length,
    completeness: answers.reduce((sum, ans) => sum + (ans.evaluation?.scores?.completeness || 0), 0) / answers.length,
    expression: answers.reduce((sum, ans) => sum + (ans.evaluation?.scores?.expression || 0), 0) / answers.length,
    evidence: answers.reduce((sum, ans) => sum + (ans.evaluation?.scores?.evidence || 0), 0) / answers.length
  }

  chartInstance.setOption({
    radar: {
      indicator: [
        { name: '相关性', max: 20 },
        { name: '准确性', max: 20 },
        { name: '深度', max: 20 },
        { name: '完整性', max: 15 },
        { name: '表达', max: 15 },
        { name: '证据', max: 10 }
      ],
      axisName: {
        color: '#666'
      }
    },
    series: [{
      type: 'radar',
      data: [{
        value: [
          Math.round(avgScores.relevance),
          Math.round(avgScores.accuracy),
          Math.round(avgScores.depth),
          Math.round(avgScores.completeness),
          Math.round(avgScores.expression),
          Math.round(avgScores.evidence)
        ],
        name: '能力评分'
      }],
      itemStyle: { color: '#667eea' },
      areaStyle: { color: 'rgba(102, 126, 234, 0.3)' }
    }]
  })
}

onMounted(() => {
  loadInterviewList()
})
</script>

<style scoped>
.result-container {
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(230, 230, 230, 0.8);
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
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-right: 1px solid rgba(230, 230, 230, 0.8);
}
.menu {
  border-right: none;
}
.content {
  background: rgba(245, 247, 250, 0.8);
  padding: 20px;
  overflow-y: auto;
}
.history-section {
  margin-bottom: 20px;
}
.history-section h2 {
  margin-bottom: 15px;
  color: #333;
}
.interview-selector {
  width: 100%;
}
.interview-option {
  display: flex;
  align-items: center;
  gap: 10px;
}
.job-type {
  flex: 1;
}
.interview-date {
  color: #999;
  font-size: 12px;
}
.score-mini {
  color: #67C23A;
  font-weight: bold;
  font-size: 12px;
}
.result-section {
  margin-top: 20px;
}
.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.result-header h2 {
  color: #333;
}
.score-card {
  display: flex;
  align-items: center;
  gap: 20px;
}
.score-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}
.score-excellent {
  background: linear-gradient(135deg, #67C23A, #85CE61);
}
.score-good {
  background: linear-gradient(135deg, #409EFF, #66B1FF);
}
.score-average {
  background: linear-gradient(135deg, #E6A23C, #F3D19E);
}
.score-poor {
  background: linear-gradient(135deg, #F56C6C, #FAB6B6);
}
.score-text {
  font-size: 32px;
  font-weight: bold;
}
.score-unit {
  font-size: 14px;
  margin-left: 2px;
}
.score-desc p {
  margin: 5px 0;
  color: #666;
}
.question-title {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}
.answer-detail {
  padding: 10px 0;
}
.answer-detail p {
  margin: 10px 0;
  color: #666;
  line-height: 1.6;
}
.evaluation-section {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}
.strengths-section, .suggestions-section {
  margin-top: 10px;
}
.strengths-section ul, .suggestions-section ul {
  margin: 5px 0;
  padding-left: 20px;
  color: #666;
}
.strengths-section li {
  color: #67C23A;
}
.suggestions-section li {
  color: #E6A23C;
}
.no-data {
  text-align: center;
  padding: 40px 0;
}
</style>
