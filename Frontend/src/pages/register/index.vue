<template>
  <AuthCard title="创建账号">
    <!-- Loading state -->
    <EmptyState
      v-if="loadingToken"
      type="loading"
      title="验证邀请链接中..."
      description="请稍候，正在验证您的邀请链接"
    />

    <!-- Token error state -->
    <EmptyState
      v-else-if="tokenError"
      type="error"
      title="链接无效"
      :description="tokenError"
    />

    <!-- Registration form -->
    <template v-else-if="tokenInfo">
      <div class="email-display">
        <el-icon :size="16" color="var(--color-primary)"><Message /></el-icon>
        <span>{{ tokenInfo.email }}</span>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        size="large"
        class="register-form"
        @keyup.enter="handleRegister"
      >
        <el-form-item prop="password">
          <template #label>
            <span class="form-label">设置密码</span>
          </template>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="至少 6 位密码"
            show-password
            :prefix-icon="Lock"
          />
        </el-form-item>

        <el-form-item prop="confirmPassword">
          <template #label>
            <span class="form-label">确认密码</span>
          </template>
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="再次输入密码"
            show-password
            :prefix-icon="Lock"
          />
        </el-form-item>

        <el-form-item class="form-submit">
          <el-button
            type="primary"
            :loading="submitting"
            class="submit-btn"
            @click="handleRegister"
          >
            {{ submitting ? '注册中...' : '注 册' }}
          </el-button>
        </el-form-item>
      </el-form>
    </template>

    <!-- Success state -->
    <EmptyState
      v-if="registered"
      type="success"
      title="注册成功！"
      :description="`欢迎 ${registeredEmail}`"
      action-label="前往登录"
      @action="goLogin"
    />
  </AuthCard>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Message, Lock } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { InviteTokenInfo } from '@/types/api'
import { getInviteInfo, completeRegister } from '@/api/user'
import AuthCard from '@/components/auth/AuthCard.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const router = useRouter()
const formRef = ref<FormInstance>()
const loadingToken = ref(true)
const tokenError = ref('')
const tokenInfo = ref<InviteTokenInfo | null>(null)
const submitting = ref(false)
const registered = ref(false)
const registeredEmail = ref('')

const form = reactive({
  password: '',
  confirmPassword: '',
})

const rules: FormRules = {
  password: [
    { required: true, message: '请设置密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== form.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

onMounted(async () => {
  const params = new URLSearchParams(window.location.search)
  const token = params.get('token') || getHashToken()

  if (!token) {
    tokenError.value = '无效的链接：缺少 token 参数'
    loadingToken.value = false
    return
  }

  try {
    const info = await getInviteInfo(token)
    tokenInfo.value = info

    if (info.expired) {
      tokenError.value = '该链接已过期，请联系管理员重新发送'
    } else if (info.used) {
      tokenError.value = '该链接已被使用'
    }
  } catch {
    tokenError.value = '无效的链接或网络错误'
  } finally {
    loadingToken.value = false
  }
})

function getHashToken(): string | null {
  const hash = window.location.hash
  const match = hash.match(/[?&]token=([^&]+)/)
  return match ? decodeURIComponent(match[1]) : null
}

async function handleRegister() {
  if (tokenError.value || !tokenInfo.value) return

  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  const params = new URLSearchParams(window.location.search)
  const token = params.get('token') || getHashToken()
  if (!token) return

  submitting.value = true
  try {
    const res = await completeRegister({ token, password: form.password })
    registered.value = true
    registeredEmail.value = res.email
    ElMessage.success('注册成功')
  } catch {
    // Error handled by interceptor
  } finally {
    submitting.value = false
  }
}

function goLogin() {
  router.push('/auth/login')
}
</script>

<style scoped>
.register-form {
  width: 100%;
}

.form-label {
  font-weight: 500;
  font-size: var(--text-sm);
  color: var(--color-foreground);
}

.email-display {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  background: var(--color-primary-bg);
  border: 1px solid var(--color-primary-light);
  border-radius: var(--radius-md);
  color: var(--color-primary);
  font-size: var(--text-sm);
  font-weight: 500;
  margin-bottom: var(--space-7);
}

.submit-btn {
  width: 100%;
  height: 44px;
  font-size: var(--text-base);
  font-weight: 600;
  border-radius: var(--radius-md);
  margin-top: var(--space-2);
}
</style>
