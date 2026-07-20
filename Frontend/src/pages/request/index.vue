<template>
  <AuthCard title="注册申请" subtitle="提交申请后等待管理员审核，审核通过后将发送邀请邮件到您的邮箱">
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      size="large"
      class="request-form"
      @keyup.enter="handleSubmit"
    >
      <el-form-item prop="email">
        <template #label>
          <span class="form-label">邮箱</span>
        </template>
        <el-input
          v-model="form.email"
          placeholder="请输入您的邮箱"
          :prefix-icon="Message"
        />
      </el-form-item>

      <el-form-item prop="reason">
        <template #label>
          <span class="form-label">申请理由</span>
        </template>
        <el-input
          v-model="form.reason"
          type="textarea"
          :rows="4"
          placeholder="请简要说明使用本系统的目的"
          maxlength="1000"
          show-word-limit
        />
      </el-form-item>

      <el-form-item class="form-submit">
        <el-button
          type="primary"
          :loading="loading"
          class="submit-btn"
          @click="handleSubmit"
        >
          {{ loading ? '提交中...' : '提交申请' }}
        </el-button>
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="footer-text">已有账号？</span>
      <router-link to="/auth/login" class="footer-link">去登录</router-link>
    </template>
  </AuthCard>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Message } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { submitRequest } from '@/api/user'
import AuthCard from '@/components/auth/AuthCard.vue'

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  email: '',
  reason: '',
})

const rules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  reason: [
    { required: true, message: '请输入申请理由', trigger: 'blur' },
    { min: 2, message: '理由至少 2 个字', trigger: 'blur' },
  ],
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await submitRequest({ email: form.email, reason: form.reason })
    ElMessage.success('申请已提交，请等待管理员审核')
    form.email = ''
    form.reason = ''
  } catch {
    // Error handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.request-form {
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
