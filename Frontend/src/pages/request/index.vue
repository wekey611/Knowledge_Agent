<template>
  <div class="auth-form">
    <div class="auth-form__head">
      <span class="eyebrow">注册申请</span>
      <h2 class="auth-form__title">申请一个账号</h2>
      <p class="auth-form__sub">提交后管理员会审核；通过后邀请链接会发到你的邮箱。</p>
    </div>

    <form v-if="!submitted" @submit.prevent="handleSubmit" class="auth-form__body">
      <div class="field">
        <label class="field__label">邮箱</label>
        <input
          v-model="form.email"
          type="email"
          class="input"
          placeholder="you@company.com"
          required
        />
      </div>

      <div class="field">
        <label class="field__label">申请理由</label>
        <textarea
          v-model="form.reason"
          class="textarea"
          rows="4"
          placeholder="简单说明使用目的即可"
          required
        />
      </div>

      <div v-if="error" class="auth-form__error">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.8">
          <circle cx="12" cy="12" r="9" />
          <path d="M12 8v5M12 16h.01" stroke-linecap="round" />
        </svg>
        <span>{{ error }}</span>
      </div>

      <button class="btn btn--primary btn--lg" :disabled="loading" type="submit">
        {{ loading ? '提交中…' : '提交申请' }}
      </button>

      <div class="auth-form__divider"><span>已有账号？</span></div>

      <div class="auth-form__alt">
        <router-link to="/auth/login" class="link-accent">前往登录</router-link>
      </div>
    </form>

    <div v-else class="success-state">
      <div class="success-state__icon">
        <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10" />
          <path d="m8 12 3 3 5-6" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </div>
      <h3 class="success-state__title">申请已提交</h3>
      <p class="success-state__desc">
        我们会在审核通过后发送邀请链接到 <strong>{{ form.email }}</strong>。
      </p>
      <router-link to="/auth/login" class="btn btn--primary">前往登录</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { requestAccount } from '@/api/auth'

const form = reactive({ email: '', reason: '' })
const loading = ref(false)
const error = ref('')
const submitted = ref(false)

async function handleSubmit() {
  if (!form.email || !form.reason) return
  error.value = ''
  loading.value = true
  try {
    await requestAccount({ email: form.email, reason: form.reason })
    submitted.value = true
  } catch (e: any) {
    error.value = e?.response?.data?.detail || '提交失败，请稍后再试'
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
  &__divider {
    text-align: center;
    color: $text-tertiary;
    font-size: $fs-12;
    margin: $s-2 0;
  }
  &__alt {
    text-align: center;
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
}

.success-state {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $s-3;

  &__icon {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background: $success-soft;
    color: $success;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: $s-2;
  }
  &__title {
    font-family: $font-display;
    font-size: $fs-24;
    font-weight: $fw-semibold;
  }
  &__desc {
    color: $text-secondary;
    font-size: $fs-14;
    line-height: $lh-normal;
    margin-bottom: $s-4;
    strong { color: $accent; font-weight: $fw-medium; }
  }
}

.link-accent {
  color: $accent;
  font-weight: $fw-medium;
  text-decoration: none;
  &:hover { color: $accent-hover; text-decoration: underline; }
}
</style>