<template>
  <div class="register-container">
    <el-card class="register-card">
      <div class="title">
        <h1>用户注册</h1>
        <p>创建账号开始智能面试体验</p>
      </div>

      <!-- 角色选择 -->
      <el-radio-group v-model="registerType" class="role-select">
        <el-radio-button value="user">普通用户</el-radio-button>
        <el-radio-button value="admin">管理员</el-radio-button>
      </el-radio-group>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码"></el-input>
        </el-form-item>
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="form.full_name" placeholder="请输入姓名（选填）"></el-input>
        </el-form-item>

        <!-- 管理员邀请码 -->
        <el-form-item v-if="registerType === 'admin'" label="邀请码" prop="invite_code">
          <el-input v-model="form.invite_code" type="password" placeholder="请输入管理员邀请码"></el-input>
          <div class="invite-tip">邀请码用于验证管理员身份，暂定为123456</div>
        </el-form-item>

        <el-button type="primary" @click="register" :loading="loading" class="register-btn">
          {{ registerType === 'admin' ? '注册管理员' : '注册用户' }}
        </el-button>
        <div class="login-link">
          已有账号？<el-link type="primary" @click="goLogin">立即登录</el-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'

const router = useRouter()
const registerType = ref('user')
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  full_name: '',
  invite_code: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为3-20个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const register = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch (e) {
    return
  }

  // 管理员必须填写邀请码
  if (registerType.value === 'admin' && !form.invite_code) {
    ElMessage.warning('请输入管理员邀请码')
    return
  }

  loading.value = true
  try {
    const res = await api.post('/auth/register', {
      username: form.username,
      email: form.email,
      password: form.password,
      full_name: form.full_name || undefined,
      invite_code: registerType.value === 'admin' ? form.invite_code : undefined
    })

    const data = res.data || res

    if (data.code === 200 || data.id) {
      ElMessage.success('注册成功！请登录')
      router.push('/login')
    } else {
      ElMessage.error(data.message || data.detail || '注册失败')
    }
  } catch (e) {
    const message = e.response?.data?.detail || e.response?.data?.message || e.message || '注册失败'
    ElMessage.error(message)
  } finally {
    loading.value = false
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
  width: 450px;
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
.invite-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
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