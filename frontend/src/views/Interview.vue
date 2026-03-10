<template>
  <div class="interview-container">
    <el-header class="header">
      <div class="logo">智能面试系统</div>
      <el-button type="text" @click="logout">退出登录</el-button>
    </el-header>
    <el-container class="main">
      <el-aside width="200px" class="aside">
        <el-menu :default-active="'3'" class="menu">
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
          <div class="progress">
            <el-progress :percentage="Math.round((currentQuestion / questions.length) * 100)"></el-progress>
            <span>问题 {{ currentQuestion }} / {{ questions.length }}</span>
          </div>

          <div v-if="!interviewStarted" class="start-page">
            <h2>准备好开始面试了吗？</h2>
            <p>系统会根据你的简历，生成5个个性化的面试问题，你可以打字或者语音回答</p>
            <el-button type="primary" size="large" @click="startInterview">开始面试</el-button>
          </div>

          <div v-else class="question-page">
            <el-alert :title="questions[currentQuestion-1]" type="info" description="请在下方输入你的回答">
            </el-alert>

            <el-input
              v-model="answer"
              type="textarea"
              :rows="6"
              placeholder="请输入你的回答..."
              style="margin-top: 20px;"
            ></el-input>

            <div style="margin-top: 20px; text-align: right;">
              <el-button type="primary" @click="nextQuestion" :loading="loading">
                {{ currentQuestion === questions.length ? '完成面试' : '下一题' }}
              </el-button>
            </div>
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { House, Document, Microphone, TrendCharts } from '@element-plus/icons-vue'
import api from '../api'

const router = useRouter()
const interviewStarted = ref(false)
const loading = ref(false)
const currentQuestion = ref(0)
const questions = ref([])
const answer = ref('')
const interviewId = ref(null)

const logout = () => {
  localStorage.clear()
  router.push('/login')
}

const goPage = (page) => {
  router.push('/' + page)
}

const startInterview = async () => {
  loading.value = true
  try {
    const resumeId = localStorage.getItem('resume_id')
    const res = await api.post('/interview/start', { resume_id: parseInt(resumeId) })
    interviewId.value = res.interview_id
    questions.value = res.questions
    currentQuestion.value = 1
    interviewStarted.value = true
    ElMessage.success('面试开始！')
  } catch (e) {
    ElMessage.error('创建面试失败')
  } finally {
    loading.value = false
  }
}

const nextQuestion = async () => {
  if (!answer.value) {
    ElMessage.warning('请输入你的回答！')
    return
  }

  loading.value = true
  try {
    await api.post('/interview/answer', {
      interview_id: interviewId.value,
      question_index: currentQuestion.value - 1,
      answer: answer.value
    })

    if (currentQuestion.value === questions.value.length) {
      // 面试结束
      await api.post('/interview/finish', { interview_id: interviewId.value })
      ElMessage.success('面试完成！')
      router.push('/result')
    } else {
      currentQuestion.value += 1
      answer.value = ''
    }
  } catch (e) {
    ElMessage.error('提交失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.interview-container {
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
.progress {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}
.start-page {
  text-align: center;
  padding: 60px 0;
}
.start-page h2 {
  margin-bottom: 15px;
}
</style>