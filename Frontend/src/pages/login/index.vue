<template>
  <div class="auth-form">
    <div class="auth-form__head">
      <span class="eyebrow">登录</span>
      <h2 class="auth-form__title">欢迎回来</h2>
      <p class="auth-form__sub">使用你的邮箱和密码进入工作台。</p>
    </div>

    <form @submit.prevent="handleLogin" class="auth-form__body">
      <div v-if="expired" class="auth-form__expired">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01" stroke-linecap="round"/></svg>
        <span>登录已过期，请重新登录</span>
      </div>

      <div class="field">
        <label class="field__label">邮箱</label>
        <input
          v-model="form.email"
          type="email"
          class="input"
          placeholder="you@company.com"
          autocomplete="email"
          required
        />
      </div>

      <div class="field">
        <div class="field__label-row">
          <label class="field__label">密码</label>
          <a class="field__link" @click.prevent="showHint = !showHint">忘记密码？</a>
        </div>
        <input
          v-model="form.password"
          type="password"
          class="input"
          placeholder="••••••••"
          autocomplete="current-password"
          required
        />
        <p v-if="showHint" class="field__hint">
          请联系管理员重置密码。
        </p>
      </div>

      <div v-if="error" class="auth-form__error">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01" stroke-linecap="round"/></svg>
        <span>{{ error }}</span>
      </div>

      <button class="btn btn--primary btn--lg" :disabled="loading" type="submit">
        <span v-if="!loading">登录</span>
        <span v-else>登录中…</span>
      </button>

      <div class="auth-form__divider"><span>或</span></div>

      <div class="auth-form__alt">
        没有账号？
        <router-link to="/auth/request" class="link-accent">提交申请</router-link>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchMyProfile, login } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'

const form = reactive({ email: '', password: '' })
const loading = ref(false)
const error = ref('')
const expired = ref(false)
const showHint = ref(false)
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

onMounted(() => {
  // 401 过期跳转会带 expired=1，登录页显示提示
  if (route.query.expired === '1') {
    expired.value = true
    setTimeout(() => (expired.value = false), 6000)
  }
})

async function handleLogin() {
  if (!form.email || !form.password) return
  error.value = ''
  loading.value = true
  try {
    const token = await login(form.email, form.password)
    // 先用最小占位信息塞进去保证路由守卫放行
    auth.setAuth(token.access_token, {
      id: 0,
      email: form.email,
      created_at: new Date().toISOString(),
      role: 'user',
    })
    // 再用真实 token 拉一次 /me 拿完整用户信息（id/role），覆盖占位
    try {
      const me = await fetchMyProfile()
      console.log('[login] /me success:', me)
      // 防御：确保是合法用户对象（id 为数字且 email 存在），否则保留占位
      if (me && typeof me === 'object' && typeof me.id === 'number' && me.email) {
        auth.setAuth(token.access_token, me)
      } else {
        console.warn('[login] /me returned invalid shape, keep placeholder', me)
      }
    } catch (meErr: any) {
      // /me 失败时保留上面的占位，至少能登录成功
      console.warn(
        '[login] /me failed, keep placeholder user. status:',
        meErr?.response?.status,
        'body:',
        meErr?.response?.data
      )
    }
    // 登录成功，清掉过期防抖标记（避免下次检查被跳过）
    sessionStorage.removeItem('ka_expiring')
    const redirect = (route.query.redirect as string) || '/dashboard'
    router.push(redirect)
  } catch (e: any) {
    const msg = e?.response?.data?.detail || '登录失败，请检查邮箱或密码'
    error.value = msg
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/tokens' as *;

.auth-form {
  width: 100%;
  max-width: 380px;

  &__head { margin-bottom: $s-8; }
  &__title {
    margin-top: $s-3;
    font-family: $font-display;
    font-size: $fs-32;
    font-weight: $fw-semibold;
    letter-spacing: -0.015em;
    line-height: 1.1;
  }
  &__sub {
    margin-top: $s-2;
    color: $text-secondary;
    font-size: $fs-14;
  }

  &__body { display: flex; flex-direction: column; gap: $s-4; }

  &__error {
    display: flex;
    align-items: center;
    gap: $s-2;
    padding: $s-3 $s-4;
    border-radius: $r-md;
    background: $danger-soft;
    color: $danger;
    font-size: $fs-13;
    border: 1px solid rgba(229, 72, 77, 0.3);
  }

  &__expired {
    display: flex;
    align-items: center;
    gap: $s-2;
    padding: $s-3 $s-4;
    border-radius: $r-md;
    background: $warning-soft;
    color: $warning;
    font-size: $fs-13;
    border: 1px solid rgba(245, 166, 35, 0.3);
  }

  &__divider {
    display: flex;
    align-items: center;
    gap: $s-3;
    color: $text-tertiary;
    font-size: $fs-12;
    &::before, &::after {
      content: '';
      flex: 1;
      height: 1px;
      background: $border-subtle;
    }
  }
  &__alt {
    text-align: center;
    color: $text-secondary;
    font-size: $fs-13;
  }
}

.field {
  display: flex;
  flex-direction: column;
  gap: $s-2;

  &__label {
    font-size: $fs-13;
    font-weight: $fw-medium;
    color: $text-secondary;
  }
  &__label-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  &__link {
    font-size: $fs-12;
    color: $accent;
    cursor: pointer;
    text-decoration: none;
    &:hover { color: $accent-hover; text-decoration: underline; }
  }
  &__hint {
    font-size: $fs-12;
    color: $text-tertiary;
    line-height: $lh-snug;
    background: $bg-surface;
    padding: $s-2 $s-3;
    border-radius: $r-sm;
    border: 1px dashed $border-subtle;
  }
}

.link-accent {
  color: $accent;
  font-weight: $fw-medium;
  text-decoration: none;
  &:hover { color: $accent-hover; text-decoration: underline; }
}
</style>