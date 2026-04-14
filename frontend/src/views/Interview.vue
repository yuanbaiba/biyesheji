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
        <el-card class="interview-card" shadow="hover">

          <!-- 步骤1: 选择职位和简历 -->
          <div v-if="!interviewStarted" class="start-page">
            <div class="welcome-section">
              <el-icon size="64" class="welcome-icon"><Microphone /></el-icon>
              <h2>准备好开始面试了吗？</h2>
              <p class="description">
                系统会根据你的简历和选择的职位，生成个性化的面试问题<br>
                你可以选择文字输入或语音回答
              </p>
            </div>

            <!-- 选择简历 -->
            <div class="selection-section">
              <h3>第一步：选择简历</h3>
              <el-select v-model="selectedResumeId" placeholder="请选择简历" class="resume-select">
                <el-option
                  v-for="resume in resumes"
                  :key="resume.id"
                  :label="resume.file_name || resume.name || '简历' + resume.id"
                  :value="resume.id"
                />
              </el-select>
            </div>

            <!-- 选择职位 -->
            <div class="selection-section">
              <h3>第二步：选择应聘职位</h3>
              <el-row :gutter="20" class="job-list">
                <el-col :xs="24" :sm="12" :md="8" v-for="job in jobs" :key="job.id">
                  <el-card
                    class="job-card"
                    :class="{ active: selectedJobId === job.id }"
                    @click="selectJob(job)"
                    shadow="hover"
                  >
                    <div class="job-header">
                      <el-tag>{{ job.job_type }}</el-tag>
                      <span class="job-status" v-if="job.is_active">招聘中</span>
                    </div>
                    <h4 class="job-title">{{ job.title }}</h4>
                    <div class="job-info">
                      <span v-if="job.department">{{ job.department }}</span>
                      <span v-if="job.salary_range">{{ job.salary_range }}</span>
                    </div>
                  </el-card>
                </el-col>
              </el-row>
            </div>

            <!-- 开始按钮 -->
            <div class="start-button-section">
              <el-button
                type="primary"
                size="large"
                @click="startInterview"
                :loading="loading"
                :disabled="!canStartInterview"
                class="start-button"
              >
                <el-icon><VideoPlay /></el-icon>
                开始面试
              </el-button>
              <p v-if="!canStartInterview" class="start-tip">
                请先选择简历和职位后再开始面试
              </p>
            </div>
          </div>

          <!-- 步骤2: 面试进行中 -->
          <div v-else class="question-page">
            <!-- 进度条 -->
            <div class="progress-section">
              <el-progress
                :percentage="Math.round((currentQuestion / questions.length) * 100)"
                :stroke-width="12"
                :text-inside="true"
                :stroke-color="getProgressColor()"
                class="custom-progress"
              />
              <div class="progress-info">
                <span class="question-counter">问题 {{ currentQuestion }} / {{ questions.length }}</span>
                <span class="job-info">应聘职位：{{ currentJobTitle }}</span>
              </div>
            </div>

            <!-- 当前问题 -->
            <div class="question-section">
              <el-alert
                :title="`问题 ${currentQuestion}`"
                :description="questions[currentQuestion - 1]"
                type="info"
                show-icon
                class="question-alert"
              />
            </div>

            <!-- 回答输入区域 -->
            <div class="answer-section">
              <el-tabs v-model="inputMode" @tab-click="handleTabClick" class="input-tabs">
                <el-tab-pane label="文字输入" name="text">
                  <div class="text-input-area">
                    <el-input
                      v-model="answer"
                      type="textarea"
                      :rows="6"
                      placeholder="请输入你的回答...（支持 Markdown 格式）"
                      :maxlength="2000"
                      show-word-limit
                      :autosize="{ minRows: 4, maxRows: 8 }"
                      class="answer-input"
                    />
                  </div>
                </el-tab-pane>

                <el-tab-pane label="语音输入" name="voice">
                  <div class="voice-input-area">
                    <div class="voice-controls">
                      <el-button
                        :type="recording ? 'danger' : 'primary'"
                        @click="toggleRecording"
                        size="large"
                        class="record-button"
                      >
                        {{ recording ? '停止录音' : '开始录音' }}
                      </el-button>
                      <div v-if="recording" class="recording-indicator">
                        <span>正在录音...</span>
                        <span>{{ recordingTime }}s</span>
                      </div>
                    </div>
                    <div v-if="audioUrl" class="audio-preview">
                      <audio :src="audioUrl" controls />
                      <el-button type="warning" size="small" @click="clearAudio">重新录音</el-button>
                    </div>
                  </div>
                </el-tab-pane>
              </el-tabs>
            </div>

            <!-- 操作按钮 -->
            <div class="action-buttons">
              <el-button @click="cancelInterview">取消面试</el-button>
              <el-button
                type="primary"
                @click="submitAnswer"
                :loading="loading"
                :disabled="!canSubmitAnswer"
              >
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
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { House, Document, Microphone, TrendCharts, VideoPlay } from '@element-plus/icons-vue'
import api from '../api'

const router = useRouter()

// 状态
const loading = ref(false)
const interviewStarted = ref(false)
const questions = ref([])
const currentQuestion = ref(0)
const answer = ref('')
const inputMode = ref('text')
const interviewId = ref(null)

// 简历和职位
const resumes = ref([])
const jobs = ref([])
const selectedResumeId = ref(null)
const selectedJobId = ref(null)
const currentJobTitle = ref('')

// 语音
const recording = ref(false)
const audioBlob = ref(null)
const audioUrl = ref('')
const recordingTime = ref(0)
const recordingTimer = ref(null)
const mediaRecorder = ref(null)

const canStartInterview = computed(() => {
  return selectedResumeId.value && selectedJobId.value
})

const canSubmitAnswer = computed(() => {
  return answer.value.trim().length > 0 || audioUrl.value
})

onMounted(() => {
  loadResumes()
  loadJobs()
})

onBeforeUnmount(() => {
  cleanupRecording()
})

const loadResumes = async () => {
  try {
    const res = await api.get('/resume/list')
    const data = res.data
    resumes.value = data.code === 200 ? data.data : (data || [])
    // 如果有已选择的简历，自动选中
    const savedResumeId = localStorage.getItem('resume_id')
    if (savedResumeId && resumes.value.length > 0) {
      const found = resumes.value.find(r => r.id === parseInt(savedResumeId))
      if (found) selectedResumeId.value = found.id
    }
  } catch (error) {
    console.error('获取简历失败:', error)
  }
}

const loadJobs = async () => {
  try {
    const res = await api.get('/jobs')
    const data = res.data
    jobs.value = Array.isArray(data) ? data : (data?.data || [])
  } catch (error) {
    console.error('获取职位失败:', error)
    // 默认职位
    jobs.value = [
      { id: 1, title: '软件工程师', job_type: '软件工程师', is_active: true },
      { id: 2, title: '产品经理', job_type: '产品经理', is_active: true }
    ]
  }
}

const selectJob = (job) => {
  selectedJobId.value = job.id
  currentJobTitle.value = job.title
}

const startInterview = async () => {
  if (!canStartInterview.value) {
    ElMessage.warning('请选择简历和职位')
    return
  }

  loading.value = true
  try {
    const selectedJob = jobs.value.find(j => j.id === selectedJobId.value)
    const res = await api.post('/interview/create', {
      user_id: parseInt(localStorage.getItem('user_id')),
      resume_id: selectedResumeId.value,
      job_id: selectedJobId.value,
      job_type: selectedJob?.job_type || '软件工程师',
      question_num: 5
    })

    const data = res.data?.data || res.data || res
    interviewId.value = data.interview_id
    questions.value = data.questions || []
    currentQuestion.value = 1
    interviewStarted.value = true

    // 保存选择
    localStorage.setItem('resume_id', selectedResumeId.value)
    localStorage.setItem('job_type', selectedJob?.job_type || '软件工程师')

    ElMessage.success('面试开始！')
  } catch (error) {
    console.error('创建面试失败:', error)
    ElMessage.error(error.response?.data?.detail || '创建面试失败')
  } finally {
    loading.value = false
  }
}

const submitAnswer = async () => {
  if (!canSubmitAnswer.value) {
    ElMessage.warning('请输入答案')
    return
  }

  loading.value = true
  try {
    const selectedJob = jobs.value.find(j => j.id === selectedJobId.value)
    await api.post('/interview/submit_answer', {
      interview_id: interviewId.value,
      question: questions.value[currentQuestion.value - 1],
      answer: answer.value.trim(),
      job_type: selectedJob?.job_type || '软件工程师'
    })

    if (currentQuestion.value === questions.value.length) {
      // 完成面试
      await finishInterview()
    } else {
      currentQuestion.value++
      answer.value = ''
      clearAudio()
    }
  } catch (error) {
    console.error('提交答案失败:', error)
    ElMessage.error(error.response?.data?.detail || '提交失败')
  } finally {
    loading.value = false
  }
}

const finishInterview = async () => {
  try {
    await api.post('/interview/finish', {
      interview_id: interviewId.value,
      user_id: parseInt(localStorage.getItem('user_id'))
    })
    ElMessage.success('面试完成！')
    setTimeout(() => router.push('/result'), 1500)
  } catch (error) {
    console.error('完成面试失败:', error)
    router.push('/result')
  }
}

const cancelInterview = async () => {
  try {
    await ElMessageBox.confirm('确定要取消面试吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    interviewStarted.value = false
    currentQuestion.value = 0
    questions.value = []
    answer.value = ''
    interviewId.value = null
  } catch (e) {}
}

// 语音相关
const toggleRecording = async () => {
  if (recording.value) {
    stopRecording()
  } else {
    await startRecording()
  }
}

const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder.value = new MediaRecorder(stream)
    const chunks = []
    recordingTime.value = 0

    mediaRecorder.value.ondataavailable = (e) => chunks.push(e.data)
    mediaRecorder.value.onstop = () => {
      audioBlob.value = new Blob(chunks, { type: 'audio/webm' })
      audioUrl.value = URL.createObjectURL(audioBlob.value)
      stream.getTracks().forEach(t => t.stop())
    }

    mediaRecorder.value.start()
    recording.value = true
    recordingTimer.value = setInterval(() => recordingTime.value++, 1000)
  } catch (error) {
    ElMessage.error('无法访问麦克风')
  }
}

const stopRecording = () => {
  if (mediaRecorder.value) {
    mediaRecorder.value.stop()
    recording.value = false
    clearInterval(recordingTimer.value)
  }
}

const clearAudio = () => {
  if (audioUrl.value) URL.revokeObjectURL(audioUrl.value)
  audioBlob.value = null
  audioUrl.value = ''
  recordingTime.value = 0
}

const cleanupRecording = () => {
  if (recordingTimer.value) clearInterval(recordingTimer.value)
  if (mediaRecorder.value && recording.value) mediaRecorder.value.stop()
  if (audioUrl.value) URL.revokeObjectURL(audioUrl.value)
}

const handleTabClick = () => {
  if (inputMode.value === 'voice') {
    answer.value = ''
  } else {
    clearAudio()
  }
}

const getProgressColor = () => {
  const p = (currentQuestion.value / questions.value.length) * 100
  return p < 30 ? '#67C23A' : p < 70 ? '#E6A23C' : '#F56C6C'
}

const logout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    localStorage.clear()
    router.push('/login')
  }).catch(() => {})
}

const goPage = (page) => router.push('/' + page)
</script>

<style scoped>
.interview-container {
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
}

.header {
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.logo {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  background: linear-gradient(45deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.main {
  height: calc(100vh - 60px);
}

.aside {
  background: rgba(255, 255, 255, 0.95);
}

.content {
  background: rgba(245, 247, 250, 0.8);
  padding: 20px;
  overflow-y: auto;
}

.interview-card {
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border: none;
  background: rgba(255, 255, 255, 0.95);
  min-height: calc(100vh - 120px);
}

.welcome-section {
  text-align: center;
  padding: 40px 20px;
}

.welcome-icon {
  color: #667eea;
  margin-bottom: 20px;
}

.welcome-section h2 {
  color: #333;
  margin-bottom: 10px;
}

.description {
  color: #666;
  line-height: 1.6;
}

.selection-section {
  margin: 30px 0;
}

.selection-section h3 {
  color: #333;
  margin-bottom: 15px;
  font-size: 16px;
}

.resume-select {
  width: 100%;
  max-width: 400px;
}

.job-list {
  margin-top: 15px;
}

.job-card {
  margin-bottom: 15px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.3s;
}

.job-card:hover {
  transform: translateY(-2px);
}

.job-card.active {
  border-color: #667eea;
}

.job-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.job-status {
  color: #67C23A;
  font-size: 12px;
}

.job-title {
  margin: 0 0 8px 0;
  color: #333;
}

.job-info {
  font-size: 12px;
  color: #666;
  display: flex;
  gap: 10px;
}

.start-button-section {
  text-align: center;
  margin-top: 40px;
}

.start-button {
  padding: 16px 40px;
  font-size: 18px;
}

.start-tip {
  color: #F56C6C;
  margin-top: 10px;
}

.progress-section {
  margin-bottom: 30px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  color: #666;
}

.question-section {
  margin-bottom: 30px;
}

.answer-section {
  margin-bottom: 30px;
}

.text-input-area {
  padding: 20px 0;
}

.voice-input-area {
  padding: 20px 0;
  text-align: center;
}

.voice-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.record-button {
  padding: 16px 32px;
}

.recording-indicator {
  color: #F56C6C;
  display: flex;
  gap: 15px;
}

.audio-preview {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}
</style>