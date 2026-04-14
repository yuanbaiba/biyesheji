import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// 用户状态管理
export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userId = ref(localStorage.getItem('user_id') || '')
  const username = ref('')
  const is_admin = ref(localStorage.getItem('is_admin') === 'true')
  const isLoggedIn = computed(() => !!token.value)

  const setUser = (userData) => {
    token.value = userData.access_token
    userId.value = userData.user_id
    username.value = userData.username
    is_admin.value = userData.is_admin || false
    localStorage.setItem('token', userData.access_token)
    localStorage.setItem('user_id', userData.user_id)
    localStorage.setItem('is_admin', is_admin.value ? 'true' : 'false')
  }

  const logout = () => {
    token.value = ''
    userId.value = ''
    username.value = ''
    is_admin.value = false
    localStorage.clear()
  }

  return {
    token,
    userId,
    username,
    is_admin,
    isLoggedIn,
    setUser,
    logout
  }
})

// 简历状态管理
export const useResumeStore = defineStore('resume', () => {
  const resumes = ref([])
  const currentResume = ref(null)
  const analysis = ref(null)

  const setResumes = (resumeList) => {
    resumes.value = resumeList
  }

  const setCurrentResume = (resume) => {
    currentResume.value = resume
    analysis.value = resume.analysis
  }

  const addResume = (resume) => {
    resumes.value.push(resume)
  }

  return {
    resumes,
    currentResume,
    analysis,
    setResumes,
    setCurrentResume,
    addResume
  }
})

// 面试状态管理
export const useInterviewStore = defineStore('interview', () => {
  const currentInterview = ref(null)
  const questions = ref([])
  const currentQuestionIndex = ref(0)
  const answers = ref([])
  const isRecording = ref(false)
  const evaluation = ref(null)

  const startInterview = (interviewData) => {
    currentInterview.value = interviewData.interview
    questions.value = interviewData.questions
    currentQuestionIndex.value = 0
    answers.value = []
    evaluation.value = null
  }

  const nextQuestion = () => {
    if (currentQuestionIndex.value < questions.value.length - 1) {
      currentQuestionIndex.value++
    }
  }

  const addAnswer = (answer) => {
    answers.value.push(answer)
  }

  const setEvaluation = (evalData) => {
    evaluation.value = evalData
  }

  const reset = () => {
    currentInterview.value = null
    questions.value = []
    currentQuestionIndex.value = 0
    answers.value = []
    evaluation.value = null
    isRecording.value = false
  }

  return {
    currentInterview,
    questions,
    currentQuestionIndex,
    answers,
    isRecording,
    evaluation,
    startInterview,
    nextQuestion,
    addAnswer,
    setEvaluation,
    reset
  }
})

// 应用状态管理
export const useAppStore = defineStore('app', () => {
  const loading = ref(false)
  const error = ref(null)

  const setLoading = (value) => {
    loading.value = value
  }

  const setError = (message) => {
    error.value = message
    if (message) {
      setTimeout(() => {
        error.value = null
      }, 5000)
    }
  }

  return {
    loading,
    error,
    setLoading,
    setError
  }
})