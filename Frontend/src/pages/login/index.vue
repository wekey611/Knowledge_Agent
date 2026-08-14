<template>
  <AuthCard title="欢迎回来" subtitle="登录你的账户以继续使用 Knowledge Agent">
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      size="large"
      class="login-form"
      @keyup.enter="handleLogin"
    >
      <el-form-item prop="email">
        <template #label>
          <span class="form-label">邮箱</span>
        </template>
        <el-input
          v-model="form.email"
          placeholder="请输入邮箱"
          :prefix-icon="Message"
        />
      </el-form-item>

      <el-form-item prop="password">
        <template #label>
          <span class="form-label">密码</span>
        </template>
        <el-input
          v-model="form.password"
          type="password"
          placeholder="请输入密码"
          show-password
          :prefix-icon="Lock"
        />
      </el-form-item>

      <el-form-item class="form-submit">
        <el-button
          type="primary"
          :loading="loading"
          class="submit-btn"
          @click="handleLogin"
        >
          {{ loading ? '登录中...' : '登 录' }}
        </el-button>
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="footer-text">还没有账号？</span>
      <router-link to="/auth/request" class="footer-link">申请注册</router-link>
    </template>
  </AuthCard>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Message, Lock } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { login } from '@/api/auth'
import AuthCard from '@/components/auth/AuthCard.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  email: '',
  password: '',
})

const rules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' },
  ],
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const tokenRes = await login(form.email, form.password)

    // Parse JWT payload to get user info
    try {
      // JWT payload 是 base64url 编码（含 - _ 字符），需先转换再 atob
      const base64 = tokenRes.access_token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
      const payload = JSON.parse(atob(base64))
      const userId = payload.user_id
      const role = payload.role || 'user'

      authStore.setAuth(tokenRes.access_token, {
        id: userId,
        email: form.email,
        role,
        created_at: '',
      })
    } catch {
      authStore.setAuth(tokenRes.access_token, {
        id: 0,
        email: form.email,
        role: 'user',
        created_at: '',
      })
    }

    ElMessage.success('登录成功')
    const redirect = (route.query.redirect as string) || '/dashboard'
    router.push(redirect)
  } catch {
    // Error handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-form {
  width: 100%;
}

.form-label {
  font-weight: 500;
  font-size: var(--text-sm);
  color: var(--color-foreground);
}

.submit-btn {
  width: 100%;
  height: 44px;
  font-size: var(--text-base);
  font-weight: 600;
  border-radius: var(--radius-md);
  margin-top: var(--space-2);
}

.footer-text {
  font-size: var(--text-sm);
  color: var(--color-muted-foreground);
}

.footer-link {
  font-size: var(--text-sm);
  font-weight: 500;
}
</style>
