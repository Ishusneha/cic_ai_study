import axios from 'axios'

// In production, nginx will proxy /api requests to backend
// In development, use the backend URL directly
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const uploadDocument = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await api.post('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const sendChatMessage = async (question, conversationId = null) => {
  const response = await api.post('/api/chat', {
    question,
    conversation_id: conversationId,
  })
  return response.data
}

export const getChatHistory = async (conversationId) => {
  const response = await api.get('/api/chat/history', {
    params: { conversation_id: conversationId },
  })
  return response.data
}

export const generateQuiz = async (numQuestions, questionType, topic = null) => {
  const response = await api.post('/api/quiz/generate', {
    num_questions: numQuestions,
    question_type: questionType,
    topic,
  })
  return response.data
}

export const submitQuiz = async (quizId, answers) => {
  const response = await api.post('/api/quiz/submit', {
    quiz_id: quizId,
    answers,
  })
  return response.data
}

export const getQuizHistory = async () => {
  const response = await api.get('/api/quiz/history')
  return response.data
}

export const getProgress = async () => {
  const response = await api.get('/api/progress')
  return response.data
}

export const getWeakAreas = async () => {
  const response = await api.get('/api/progress/weak-areas')
  return response.data
}

export default api

