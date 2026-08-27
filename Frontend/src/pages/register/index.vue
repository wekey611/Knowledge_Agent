<template>
  <div class="auth-form">
    <div class="auth-form__head">
      <span class="eyebrow">邀请注册</span>
      <h2 class="auth-form__title">完成账号</h2>
      <p class="auth-form__sub" v-if="tokenInfo">为 <strong>{{ tokenInfo.email }}</strong> 设置用户名和密码。</p>
    </div>

    <div v-if="loadingToken" class="state-loading">
      <span class="spinner" />
      <p class="muted">正在验证邀请链接…</p>
    </div>

    <div v-else-if="tokenError" class="state-error">
      <div class="state-error__icon">
        <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10" />
          <path d="M12 8v5M12 16h.01" stroke-linecap="round" />
        </svg>
      </div>
      <h3>链接无效</h3>
      <p>{{ tokenError }}</p>
      <router-link to="/auth/request" class="btn btn--ghost">重新申请</router-link>
    </div>

    <form v-else-if="tokenInfo" @submit.prevent="handleSubmit" class="auth-form__body">
      <div class="field">
        <label class="field__label">邮箱</label>
        <input :value="tokenInfo.email" disabled class="input" />
      </div>
      <div class="field">
        <label class="field__label">用户名</label>
        <input v-model="form.username" class="input" placeholder="3-32 位字母/数字" required />
      </div>
      <div class="field">
        <label class="field__label">密码</label>
        <input v-model="form.password" type="password" class="input" placeholder="至少 8 位" required minlength="8" />
      </div>
      <div class="field">
        <label class="field__label">确认密码</label>
        <input v-model="form.password2" type="password" class="input" required minlength="8" />
      </div>

      <div v-if="error" class="auth-form__error">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01" stroke-linecap="round"/></svg>
        <span>{{ error }}</span>
      </div>

      <button class="btn btn--primary btn--lg" :disabled="loading" type="submit">
        {{ loading ? '注册中…' : '创建账号' }}
      </button>
    </form>

    <div v-else-if="success" class="state-success">
      <div class="state-success__icon">
        <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10" />
          <path d="m8 12 3 3 5-6" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </div>
      <h3>账号已创建</h3>
      <p>欢迎加入 · 现在可以登录了。</p>
      <router-link to="/auth/login" class="btn btn--primary">前往登录</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { inviteInfo, register } from '@/api/auth'
import type { InviteTokenInfo } from '@/types/api'

const route = useRoute()
const token = (route.query.token as string) || ''

const tokenInfo = ref<InviteTokenInfo | null>(null)
const loadingToken = ref(true)
const tokenError = ref('')
const form = reactive({ username: '', password: '', password2: '' })
const error = ref('')
const loading = ref(false)
const success = ref(false)

onMounted(async () => {
  if (!token) {
    tokenError.value = '邀请链接缺失 token 参数'
    loadingToken.value = false
    return
  }
  try {
    tokenInfo.value = await inviteInfo(token)
    if (tokenInfo.value.used) tokenError.value = '该邀请链接已被使用'
    else if (tokenInfo.value.expired) tokenError.value = '该邀请链接已过期'
  } catch (e: any) {
    tokenError.value = e?.response?.data?.detail || '邀请链接无效'
  } finally {
    loadingToken.value = false
  }
})

async function handleSubmit() {
  if (!form.username || !form.password) return
  if (form.password !== form.password2) {
    error.value = '两次输入的密码不一致'
    return
  }
  error.value = ''
  loading.value = true
  try {
    await register({ token, username: form.username, password: form.password })
    success.value = true
  } catch (e: any) {
    error.value = e?.response?.data?.detail || '注册失败，请稍后再试'
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
    line-height: $lh-snug;
    strong { color: $accent; font-weight: $fw-medium; }
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
}

.state-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $s-3;
  padding: $s-8 0;

  .spinner {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    border: 2px solid $border-subtle;
    border-top-color: $accent;
    animation: spin 800ms linear infinite;
  }
}

.state-error, .state-success {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $s-3;

  h3 {
    font-family: $font-display;
    font-size: $fs-24;
    font-weight: $fw-semibold;
  }
  p {
    color: $text-secondary;
    font-size: $fs-14;
    line-height: $lh-normal;
  }
}

.state-error__icon {
  width: 56px; height: 56px;
  border-radius: 50%;
  background: $danger-soft;
  color: $danger;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: $s-2;
}
.state-success__icon {
  width: 64px; height: 64px;
  border-radius: 50%;
  background: $success-soft;
  color: $success;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: $s-2;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>