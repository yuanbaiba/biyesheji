<template>
  <div class="register-container">
    <el-card class="register-card">
      <div class="title">
        <h1>用户注册</h1>
        <p>注册账号，开启智能面试之旅</p>
      </div>
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" placeholder="请输入邮箱"></el-input>
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-button type="primary" @click="register" class="register-btn">注册</el-button>
        <div class="login-link">
          已有账号？<el-link type="primary" @click="goLogin">立即登录</el-link>
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
const form = ref({ username: '', email: '', password: '' })

const register = async () => {
  try {
    await api.post('/auth/register', form.value)
    ElMessage.success('注册成功')
    router.push('/login')
  } catch (e) {
    ElMessage.error(e.response.data.detail)
  }
}

const goLogin = () => router.push('/login')
</script>

<style scoped>
.register-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.register-card {
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
.register-btn {
  width: 100%;
  margin-top: 10px;
}
.login-link {
  text-align: center;
  margin-top: 15px;
}
</style>