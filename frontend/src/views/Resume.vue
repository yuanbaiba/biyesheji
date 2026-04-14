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
        <el-card class="resume-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>简历管理</span>
              <el-button type="primary" @click="showUploadDialog">
                <el-icon><Upload /></el-icon>上传简历
              </el-button>
            </div>
          </template>

          <!-- 简历列表 -->
          <div v-if="resumes.length > 0" class="resume-list">
            <el-row :gutter="20">
              <el-col :span="8" v-for="resume in resumes" :key="resume.id">
                <el-card class="resume-item" shadow="hover">
                  <div class="resume-info">
                    <div class="resume-name">
                      <el-icon><Document /></el-icon>
                      <span>{{ resume.file_name || resume.name || '未命名简历' }}</span>
                    </div>
                    <div class="resume-meta" v-if="resume.name">
                      <span>姓名：{{ resume.name }}</span>
                    </div>
                    <div class="resume-meta" v-if="resume.position">
                      <span>应聘职位：{{ resume.position }}</span>
                    </div>
                    <div class="resume-meta" v-if="resume.created_at">
                      <span>上传时间：{{ formatDate(resume.created_at) }}</span>
                    </div>
                    <div class="resume-skills" v-if="resume.skills">
                      <el-tag size="small" type="success" v-for="skill in parseSkills(resume.skills)" :key="skill" class="skill-tag">
                        {{ skill }}
                      </el-tag>
                    </div>
                  </div>
                  <div class="resume-actions">
                    <el-button type="primary" size="small" @click="selectResume(resume)">
                      选择此简历
                    </el-button>
                    <el-button type="danger" size="small" @click="deleteResume(resume.id)">
                      删除
                    </el-button>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>

          <!-- 空状态 -->
          <el-empty v-else description="暂无简历，请上传简历后开始面试" />

          <!-- 简历分析详情 -->
          <div v-if="selectedResume && selectedResume.analysis" class="analysis-section">
            <el-divider content-position="left">简历分析结果</el-divider>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="姓名">{{ selectedResume.analysis.name || '-' }}</el-descriptions-item>
              <el-descriptions-item label="邮箱">{{ selectedResume.analysis.email || '-' }}</el-descriptions-item>
              <el-descriptions-item label="手机">{{ selectedResume.analysis.phone || '-' }}</el-descriptions-item>
              <el-descriptions-item label="应聘职位">{{ selectedResume.analysis.position || '-' }}</el-descriptions-item>
              <el-descriptions-item label="工作经验" :span="2">{{ selectedResume.analysis.experience || '-' }}</el-descriptions-item>
              <el-descriptions-item label="技能特长" :span="2">
                <div v-if="selectedResume.analysis.skills">
                  <el-tag size="small" type="success" v-for="skill in parseSkills(selectedResume.analysis.skills)" :key="skill" style="margin-right: 5px;">
                    {{ skill }}
                  </el-tag>
                </div>
                <span v-else>-</span>
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-main>
    </el-container>

    <!-- 上传对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="上传简历" width="500px">
      <el-upload
        ref="uploadRef"
        class="resume-uploader"
        :auto-upload="false"
        :limit="1"
        :on-change="handleFileChange"
        :file-list="fileList"
        accept=".docx,.pdf"
      >
        <el-button type="primary">选择文件</el-button>
        <template #tip>
          <div class="upload-tip">支持 .docx 和 .pdf 格式文件</div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="uploadResume" :loading="uploading">上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { House, Document, Microphone, TrendCharts, Upload } from '@element-plus/icons-vue'
import api from '../api'

const router = useRouter()

const resumes = ref([])
const selectedResume = ref(null)
const uploadDialogVisible = ref(false)
const uploading = ref(false)
const uploadRef = ref(null)
const fileList = ref([])
const currentFile = ref(null)

onMounted(() => {
  loadResumes()
})

const loadResumes = async () => {
  try {
    const res = await api.get('/resume/list')
    const data = res.data
    if (data.code === 200) {
      resumes.value = data.data || []
    } else {
      resumes.value = data || []
    }
  } catch (error) {
    console.error('获取简历列表失败:', error)
    ElMessage.error('获取简历列表失败')
  }
}

const showUploadDialog = () => {
  uploadDialogVisible.value = true
  fileList.value = []
  currentFile.value = null
}

const handleFileChange = (file) => {
  currentFile.value = file.raw
}

const uploadResume = async () => {
  if (!currentFile.value) {
    ElMessage.warning('请选择简历文件')
    return
  }

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', currentFile.value)

    const res = await api.post('/resume/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 120000 // 上传简历需要AI分析，设置120秒超时
    })

    if (res.data.code === 200) {
      ElMessage.success('简历上传成功')
      uploadDialogVisible.value = false
      loadResumes()
    } else {
      ElMessage.error(res.data.message || res.data.detail || '上传失败')
    }
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error(error.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}

const selectResume = async (resume) => {
  // 获取完整简历信息
  try {
    const res = await api.get(`/resume/${resume.id}`)
    const data = res.data
    if (data.code === 200) {
      selectedResume.value = data.data
      // 保存到localStorage
      localStorage.setItem('resume_id', resume.id)
      localStorage.setItem('job_type', resume.position || '软件工程师')
      ElMessage.success('已选择此简历作为面试简历')
    }
  } catch (error) {
    console.error('获取简历详情失败:', error)
    ElMessage.error('获取简历详情失败')
  }
}

const deleteResume = async (resumeId) => {
  try {
    await ElMessageBox.confirm('确定要删除这份简历吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const res = await api.delete(`/resume/${resumeId}`)
    if (res.data.code === 200) {
      ElMessage.success('删除成功')
      loadResumes()
      if (selectedResume.value && selectedResume.value.id === resumeId) {
        selectedResume.value = null
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString()
}

const parseSkills = (skills) => {
  if (!skills) return []
  if (Array.isArray(skills)) return skills
  if (typeof skills === 'string') {
    return skills.split(/[,，、]/).filter(s => s.trim())
  }
  return []
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

const goPage = (page) => {
  router.push('/' + page)
}
</script>

<style scoped>
.resume-container {
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
}

.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(230, 230, 230, 0.8);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.logo {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  background: linear-gradient(45deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
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

.resume-card {
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border: none;
  background: rgba(255, 255, 255, 0.95);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.resume-list {
  margin-top: 20px;
}

.resume-item {
  margin-bottom: 20px;
  border-radius: 8px;
}

.resume-info {
  margin-bottom: 15px;
}

.resume-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
}

.resume-meta {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.resume-skills {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.skill-tag {
  margin-right: 5px;
}

.resume-actions {
  display: flex;
  gap: 10px;
}

.analysis-section {
  margin-top: 30px;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.resume-uploader {
  text-align: center;
  padding: 20px;
}
</style>