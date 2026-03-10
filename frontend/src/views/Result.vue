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
        <el-card>
          <div class="result-header">
            <h2>面试结果</h2>
            <el-tag type="success" size="large">面试已完成</el-tag>
          </div>

          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="12">
              <el-card>
                <div class="score-card">
                  <div class="score-circle">
                    <span class="score-text">{{ result.total_score }}</span>
                    <span class="score-unit">/100</span>
                  </div>
                  <div class="score-desc">
                    <p>综合评分</p>
                    <p>表现优秀！</p>
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

          <el-card style="margin-top: 20px;">
            <h3>AI 评价</h3>
            <p class="feedback">{{ result.feedback }}</p>
          </el-card>

          <el-card style="margin-top: 20px;">
            <h3>问题详情</h3>
            <el-collapse>
              <el-collapse-item v-for="(item, index) in result.details" :title="`问题 ${index+1}: ${item.question}`">
                <p><strong>你的回答：</strong>{{ item.answer }}</p>
                <p><strong>评分：</strong>{{ item.score }} 分</p>
                <p><strong>点评：</strong>{{ item.comment }}</p>
              </el-collapse-item>
            </el-collapse>
          </el-card>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { House, Document, Microphone, TrendCharts } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import api from '../api'

const router = useRouter()
const result = ref({
  total_score: 85,
  feedback: '你的回答整体表现不错，逻辑清晰，表达流畅。在技术问题上回答准确，展现了扎实的专业基础。建议在项目经验部分可以更具体的描述你解决的问题和取得的成果，这样能更好的展示你的能力。',
  details: [
    { question: '请介绍一下你自己', answer: '我是一名软件工程专业的学生，擅长Python和前端开发...', score: 88, comment: '自我介绍清晰，重点突出' },
    { question: '你为什么想要申请这个职位？', answer: '我对这个领域很感兴趣，而且我的技能和这个职位很匹配...', score: 85, comment: '动机明确，对职位有一定了解' },
    { question: '你最大的优势是什么？', answer: '我的学习能力很强，能快速上手新技术...', score: 82, comment: '优势描述具体，有说服力' },
    { question: '你遇到过的最大的挑战是什么？', answer: '之前做项目的时候遇到过技术难题，最后通过查资料解决了...', score: 84, comment: '能体现解决问题的能力' },
    { question: '你的职业规划是什么？', answer: '我希望能在技术上不断成长，成为一名全栈工程师...', score: 86, comment: '规划清晰，有上进心' }
  ]
})
const scoreChart = ref(null)

const logout = () => {
  localStorage.clear()
  router.push('/login')
}

const goPage = (page) => {
  router.push('/' + page)
}

const initChart = () => {
  const chart = echarts.init(scoreChart.value)
  const scores = result.value.details.map(d => d.score)
  chart.setOption({
    radar: {
      indicator: [
        { name: '表达能力', max: 100 },
        { name: '专业能力', max: 100 },
        { name: '逻辑能力', max: 100 },
        { name: '应变能力', max: 100 },
        { name: '匹配度', max: 100 }
      ]
    },
    series: [{
      type: 'radar',
      data: [{
        value: scores,
        name: '能力评分'
      }],
      itemStyle: { color: '#667eea' }
    }]
  })
}

onMounted(() => {
  initChart()
})
</script>

<style scoped>
.result-container {
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
.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}
.score-text {
  font-size: 32px;
  font-weight: bold;
}
.score-unit {
  font-size: 14px;
  margin-left: 2px;
}
.feedback {
  line-height: 1.8;
  color: #666;
  margin-top: 10px;
}
</style>