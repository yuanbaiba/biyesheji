import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores'
import router from '../router'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    const { data } = response
    // 处理后端返回的统一格式 {code: 200, data: ...}
    if (data && typeof data === 'object') {
      // 如果有code字段且不是200，才报错
      if ('code' in data && data.code !== 200) {
        ElMessage.error(data.message || '请求失败')
        return Promise.reject(new Error(data.message || '请求失败'))
      }
    }
    return response
  },
  error => {
    const { response } = error

    if (response) {
      const { status, data } = response

      switch (status) {
        case 401:
          // 未授权，清除登录状态
          const userStore = useUserStore()
          userStore.logout()
          router.push('/login')
          ElMessage.error('登录已过期，请重新登录')
          break
        case 403:
          ElMessage.error('没有权限访问')
          break
        case 404:
          ElMessage.error('请求地址不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(data?.message || data?.detail || `请求失败 (${status})`)
      }
    } else if (error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时，请检查网络连接')
    } else {
      ElMessage.error('网络错误，请检查网络连接')
    }

    return Promise.reject(error)
  }
)

// 上传文件专用方法
export const uploadFile = (url, file, onProgress) => {
  const formData = new FormData()
  formData.append('file', file)

  return api.post(url, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: onProgress
  })
}

// 语音上传专用方法
export const uploadVoice = (url, audioBlob, additionalData = {}) => {
  const formData = new FormData()
  formData.append('audio', audioBlob, 'answer.wav')

  Object.keys(additionalData).forEach(key => {
    formData.append(key, additionalData[key])
  })

  return api.post(url, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export default api