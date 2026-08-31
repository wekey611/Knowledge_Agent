import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios'

const http: AxiosInstance = axios.create({
  baseURL: '/',
  // ⚠️ RAG 问答要调 LLM（MiniMax 通常 5~30s），给 60s 兜底
  // vite proxy 自己也有 timeout: 120000（见 vite.config.ts）
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ── 轻量 toast（不依赖 ElementPlus，深色主题适配）───────────────
let toastTimer: number | undefined

export function showToast(message: string, type: 'error' | 'success' = 'error') {
  const existing = document.querySelector('.ka-toast')
  if (existing) existing.remove()

  const el = document.createElement('div')
  el.className = `ka-toast ka-toast--${type}`
  el.textContent = message
  document.body.appendChild(el)

  requestAnimationFrame(() => el.classList.add('ka-toast--show'))

  clearTimeout(toastTimer)
  toastTimer = window.setTimeout(() => {
    el.classList.remove('ka-toast--show')
    setTimeout(() => el.remove(), 250)
  }, 2600)
}

// toast 样式（挂载一次）
const toastStyleId = 'ka-toast-style'
if (!document.getElementById(toastStyleId)) {
  const style = document.createElement('style')
  style.id = toastStyleId
  style.textContent = `
.ka-toast {
  position: fixed;
  top: 16px;
  left: 50%;
  transform: translate(-50%, -12px);
  z-index: 9999;
  padding: 10px 16px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  line-height: 1.4;
  color: #E8EAED;
  background: #1C1F27;
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease, transform 0.2s ease;
  font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;
}
.ka-toast--show {
  opacity: 1;
  transform: translate(-50%, 0);
}
.ka-toast--error { border-color: rgba(229, 72, 77, 0.4); }
.ka-toast--success { border-color: rgba(70, 177, 126, 0.4); }
`
  document.head.appendChild(style)
}

// ── 请求拦截器：自动注入 token ──────────────────────────────────
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

// ── 响应拦截器：统一错误处理 ────────────────────────────────────
http.interceptors.response.use(
  (response) => response,
  (error) => {
    // Demo 模式下不要因为后端 401 把登录态清掉（demo token 后端不认识）
    const isDemo = localStorage.getItem('access_token')?.startsWith('demo.')
    if (isDemo) return Promise.reject(error)

    if (error.response) {
      const { status, data } = error.response
      const detail = data?.detail || '请求失败'

      if (status === 401) {
        // Token 过期或无效，清除本地状态，跳转登录页（带过期标记，登录页会显示提示）
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
        const current = window.location.hash.replace(/^#/, '') || '/dashboard'
        window.location.href = `/#/auth/login?redirect=${encodeURIComponent(current)}&expired=1`
      } else if (status === 403) {
        showToast('无权限执行此操作')
      } else if (status === 404) {
        showToast(detail || '资源不存在')
      } else if (status === 400) {
        showToast(detail)
      } else if (status >= 500) {
        showToast('服务器错误，请稍后重试')
      }
    } else {
      showToast('网络错误，请检查连接')
    }
    return Promise.reject(error)
  }
)

export default http