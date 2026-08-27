import { onMounted, onBeforeUnmount } from 'vue'
import { showToast } from '@/api/http'

/**
 * JWT 过期主动检测
 * - 启动时立即检查一次
 * - 之后每 30 秒检查一次（token 过期发生在页面无请求的空闲期也能被发现）
 * - 过期则：提示 → 清除登录态 → 跳登录页（带 expired=1）
 */
export function useTokenExpiryWatcher() {
  function base64UrlDecode(str: string): string {
    // JWT 用 urlsafe base64（-/_），atob 只认标准 base64（+/）
    const b64 = str.replace(/-/g, '+').replace(/_/g, '/')
    const pad = b64.length % 4 === 0 ? '' : '='.repeat(4 - (b64.length % 4))
    return atob(b64 + pad)
  }

  function decodeExp(token: string): number | null {
    try {
      const parts = token.split('.')
      if (parts.length !== 3) return null
      const payload = JSON.parse(base64UrlDecode(parts[1]))
      return typeof payload.exp === 'number' ? payload.exp : null
    } catch {
      return null
    }
  }

  function check() {
    // demo token 不检查（fake token 没有真实 exp）
    const token = localStorage.getItem('access_token')
    if (!token || token.startsWith('demo.')) return

    const exp = decodeExp(token)
    if (exp === null) return

    // 已过期（留 5 秒缓冲）
    if (exp * 1000 <= Date.now() + 5000) {
      // 防抖：已经在跳转就不重复
      if (sessionStorage.getItem('ka_expiring')) return
      sessionStorage.setItem('ka_expiring', '1')

      showToast('登录已过期，请重新登录')
      setTimeout(() => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
        const current = window.location.hash.replace(/^#/, '') || '/dashboard'
        window.location.href = `/#/auth/login?redirect=${encodeURIComponent(current)}&expired=1`
      }, 1200) // 让 toast 先显示一下再跳转
    }
  }

  let timer: number | undefined

  onMounted(() => {
    check()
    timer = window.setInterval(check, 30_000)
  })

  onBeforeUnmount(() => {
    if (timer) clearInterval(timer)
  })

  return { check }
}
