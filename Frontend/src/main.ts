import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './styles/global.scss'

// 演示模式：URL 含 demo=1 时自动登录，方便截图与预览
// 必须在 router 创建之前注入 token，否则首屏导航会被踢到登录页
if (new URLSearchParams(window.location.search).get('demo') === '1') {
  console.log('[demo] injecting auth...')
  localStorage.setItem('access_token', 'demo.' + Math.random().toString(36).slice(2))
  localStorage.setItem(
    'user',
    JSON.stringify({ id: 1, email: 'demo@knowledge.dev', created_at: new Date().toISOString(), role: 'admin' })
  )
  console.log('[demo] injected, token =', localStorage.getItem('access_token'))
}

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')