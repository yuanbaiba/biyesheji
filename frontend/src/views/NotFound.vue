<template>
  <div class="not-found-container">
    <div class="error-content">
      <div class="error-code">404</div>
      <h1 class="error-title">页面未找到</h1>
      <p class="error-description">抱歉，您访问的页面不存在或已被移除。</p>
      <el-button type="primary" size="large" @click="goHome">
        返回首页
      </el-button>
    </div>
    <div class="error-illustration">
      <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
        <circle cx="200" cy="150" r="80" fill="#f5f5f5" stroke="#e0e0e0" stroke-width="2"/>
        <circle cx="180" cy="130" r="8" fill="#667eea"/>
        <circle cx="220" cy="130" r="8" fill="#667eea"/>
        <path d="M170 170 Q200 190 230 170" stroke="#667eea" stroke-width="3" fill="none"/>
        <text x="200" y="220" text-anchor="middle" font-size="16" fill="#999">¯\_(ツ)_/¯</text>
      </svg>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/home')
}
</script>

<style scoped>
.not-found-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.error-content {
  text-align: center;
  color: white;
  max-width: 500px;
}

.error-code {
  font-size: 120px;
  font-weight: bold;
  margin-bottom: 20px;
  opacity: 0.8;
}

.error-title {
  font-size: 32px;
  margin-bottom: 16px;
  font-weight: 600;
}

.error-description {
  font-size: 18px;
  margin-bottom: 32px;
  opacity: 0.9;
  line-height: 1.6;
}

.error-illustration {
  margin-left: 60px;
}

.error-illustration svg {
  width: 200px;
  height: 150px;
}

@media (max-width: 768px) {
  .not-found-container {
    flex-direction: column;
    text-align: center;
  }

  .error-illustration {
    margin-left: 0;
    margin-top: 40px;
  }

  .error-illustration svg {
    width: 150px;
    height: 112px;
  }

  .error-code {
    font-size: 80px;
  }

  .error-title {
    font-size: 24px;
  }
}
</style>