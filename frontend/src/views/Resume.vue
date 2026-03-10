<template>
  <div class="resume-container">
    <el-header class="header">
      <div class="logo">智能面试系统</div>
      <el-button type="text" @click="logout">退出登录</el-button>
    </el-header>
    <el-container class="main">
      <el-aside width="200px" class="aside">
        <el-menu :default-active="'2'" class="menu">
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
          <h2>简历上传</h2>
          <p>上传你的简历，系统会自动解析，为你生成个性化面试题</p>
          <el-upload
            class="upload-demo"
            drag
            :before-upload="beforeUpload"
            :on-success="onSuccess"
            :on-error="onError"
            action="/api/resume/upload"
            :headers="headers"
          >
            <i class="el-icon--upload"><upload-filled /></i>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <div class="el-upload__tip" slot="tip">支持 .docx .pdf 格式的简历文件</div>
          </el-upload>

          <div v-if="resumeInfo" class="resume-info" style="margin-top: 20px;">
            <el-divider>解析结果</el-divider>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="姓名">{{ resumeInfo.name }}</el-descriptions-item>
              <el-descriptions-item label="电话">{{ resumeInfo.phone }}</el-descriptions-item>
              <el-descriptions-item label="邮箱">{{ resumeInfo.email }}</el-descriptions-item>
              <el-descriptions-item label="工作年限">{{ resumeInfo.experience }}</el-descriptions-item>
              <el-descriptions-item label="期望职位" :span="2">{{ resumeInfo.position }}</el-descriptions-item>
              <el-descriptions-item label="技能" :span="2">{{ resumeInfo.skills }}</el-descriptions-item>
            </el-descriptions>
            <el-button type="primary" @click="goInterview" style="margin-top: 20px;">
              开始面试
            </el-button>
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
import { House, Document, Microphone, TrendCharts, UploadFilled } from '@element-plus/icons-vue'
import api from '../api'

const router = useRouter()
const resumeInfo = ref(null)
const headers = ref({
  Authorization: `Bearer ${localStorage.getItem('token')}`
})

const logout = () => {
  localStorage.clear()
  router.push('/login')
}

const goPage = (page) => {
  router.push('/' + page)
}

const beforeUpload = (file) => {
  const isDoc = file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  const isPdf = file.type === 'application/pdf'
  if (!isDoc && !isPdf) {
    ElMessage.error('只能上传 docx 或 pdf 文件!')
    return false
  }
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) {
    ElMessage.error('文件大小不能超过 2MB!')
    return false
  }
  return true
}

const onSuccess = (res) => {
  ElMessage.success('简历解析成功!')
  resumeInfo.value = res
  localStorage.setItem('resume_id', res.id)
}

const onError = () => {
  ElMessage.error('上传失败!')
}

const goInterview = () => {
  router.push('/interview')
}
</script>

<style scoped>
.resume-container {
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
.upload-demo {
  margin-top: 20px;
}
</style>