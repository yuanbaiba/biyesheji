<template>
  <div class="login-container">
    <el-card class="login-card">
      <div class="title">
        <h1>智能面试系统</h1>
        <p>基于大语言模型的自动化招聘面试</p>
      </div>
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-button type="primary" @click="login" class="login-btn">登录</el-button>
        <div class="register-link">
          没有账号？<el-link type="primary" @click="goRegister">立即注册</el-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'

const router = useRouter()
const form = ref({ username: '', password: '' })

const login = async () => {
  try {
    const res = await api.post('/auth/login', new URLSearchParams(form.value))
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('user_id', res.data.user_id)
    ElMessage.success('登录成功')
    router.push('/home')
  } catch (e) {
    ElMessage.error(e.response.data.detail)
  }
}

const goRegister = () => router.push('/register')
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  width: 400px;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}
.title {
  text-align: center;
  margin-bottom: 30px;
}
.title h1 {
  color: #333;
  margin-bottom: 8px;
}
.title p {
  color: #666;
  font-size: 14px;
}
.login-btn {
  width: 100%;
  margin-top: 10px;
}
.register-link {
  text-align: center;
  margin-top: 15px;
}
</style>