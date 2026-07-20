import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'

const http: AxiosInstance = axios.create({
  baseURL: '/',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器：自动注入 token
http.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：统一错误处理
http.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      const detail = data?.detail || '请求失败'

      if (status === 401) {
        // Token 过期或无效，清除本地状态，跳转登录页
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
        window.location.href = '/#/login'
        ElMessage.error('登录已过期，请重新登录')
      } else if (status === 403) {
        ElMessage.error('无权限执行此操作')
      } else if (status === 404) {
        ElMessage.error(detail || '资源不存在')
      } else if (status === 400) {
        ElMessage.error(detail)
      } else if (status >= 500) {
        ElMessage.error('服务器错误，请稍后重试')
      }
    } else {
      ElMessage.error('网络错误，请检查连接')
    }
    return Promise.reject(error)
  }
)

export default http
