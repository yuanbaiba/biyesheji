<template>
  <div class="login-container">
    <el-card class="login-card">
      <div class="title">
        <h1>智能面试系统</h1>
        <p>基于大语言模型的自动化招聘面试</p>
      </div>

      <!-- 角色选择 -->
      <el-radio-group v-model="loginType" class="role-select">
        <el-radio-button value="user">用户登录</el-radio-button>
        <el-radio-button value="admin">管理员登录</el-radio-button>
      </el-radio-group>

      <el-form :model="form" label-width="80px" @submit.prevent>
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-button type="primary" native-type="button" @click="login" :loading="loading" class="login-btn">
          登录
        </el-button>
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
import { useUserStore } from '../stores'
import { ElMessage } from 'element-plus'
import api from '../api'

const router = useRouter()
const userStore = useUserStore()
const loginType = ref('user')
const form = ref({ username: '', password: '' })
const loading = ref(false)

const login = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    const res = await api.post(
      '/auth/login',
      new URLSearchParams(form.value).toString(),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    )

    const data = res.data

    // 先设置用户信息（包括token），再获取完整用户数据
    userStore.setUser({
      access_token: data.access_token,
      user_id: data.user_id,
      username: data.username,
      is_admin: data.is_admin || false
    })

    // 如果是管理员登录但不是管理员账号，报错
    if (loginType.value === 'admin' && !data.is_admin) {
      ElMessage.error('该账号不是管理员，请选择用户登录')
      userStore.logout()
      return
    }

    ElMessage.success('登录成功')

    // 根据角色跳转
    if (data.is_admin && loginType.value === 'admin') {
      await router.push('/admin')
    } else {
      await router.push('/home')
    }
  } catch (e) {
    const message = e.response?.data?.detail || e.message || '登录失败，请检查用户名和密码'
    ElMessage.error(message)
  } finally {
    loading.value = false
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
.role-select {
  width: 100%;
  margin-bottom: 20px;
  display: flex;
}
.role-select :deep(.el-radio-button) {
  flex: 1;
}
.role-select :deep(.el-radio-button__inner) {
  width: 100%;
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