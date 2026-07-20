<template>
  <div class="user-avatar" :class="{ clickable: !!onClick }" @click="onClick">
    <div class="avatar-circle" :style="{ background: avatarColor }">
      <span class="avatar-text">{{ initials }}</span>
    </div>
    <div v-if="showInfo" class="user-info" :class="{ 'on-dark': darkBg }">
      <span class="user-email">{{ email }}</span>
      <el-tag v-if="isAdmin" size="small" type="danger" class="role-tag">管理员</el-tag>
      <el-tag v-else size="small" type="info" class="role-tag">用户</el-tag>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  email?: string
  isAdmin?: boolean
  showInfo?: boolean
  darkBg?: boolean
  onClick?: () => void
}>(), {
  showInfo: false,
  isAdmin: false,
  darkBg: false,
})

const initials = computed(() => {
  if (!props.email) return '?'
  return props.email.charAt(0).toUpperCase()
})

const avatarColor = computed(() => {
  if (props.isAdmin) return 'linear-gradient(135deg, #2563EB, #7C3AED)'
  // Vibrant gradient for regular users — warm accent
  return 'linear-gradient(135deg, #F97316, #EC4899)'
})
</script>

<style scoped>
.user-avatar {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.user-avatar.clickable {
  cursor: pointer;
}

.avatar-circle {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.avatar-text {
  color: white;
  font-size: var(--text-sm);
  font-weight: 600;
  font-family: var(--font-heading);
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.user-email {
  font-size: var(--text-sm);
  color: var(--color-foreground);
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 160px;
}

.on-dark .user-email {
  color: #F1F5F9;
}

.role-tag {
  align-self: flex-start;
}
</style>
