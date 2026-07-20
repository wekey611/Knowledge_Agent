<template>
  <div class="empty-state" :class="`state-${type}`">
    <!-- Loading skeleton -->
    <template v-if="type === 'loading'">
      <div class="skeleton-icon" />
      <div class="skeleton-title" />
      <div class="skeleton-desc" />
    </template>

    <!-- Error state -->
    <template v-else-if="type === 'error'">
      <div class="state-icon error-icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
      </div>
      <h3 class="state-title">{{ title || '加载失败' }}</h3>
      <p v-if="description" class="state-desc">{{ description }}</p>
      <el-button v-if="actionLabel" class="state-btn" @click="$emit('action')">
        {{ actionLabel }}
      </el-button>
    </template>

    <!-- Empty state -->
    <template v-else-if="type === 'empty'">
      <div class="state-icon empty-icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="12" y1="18" x2="12" y2="12" />
          <line x1="9" y1="15" x2="15" y2="15" />
        </svg>
      </div>
      <h3 class="state-title">{{ title || '暂无数据' }}</h3>
      <p v-if="description" class="state-desc">{{ description }}</p>
      <el-button v-if="actionLabel" class="state-btn" type="primary" @click="$emit('action')">
        {{ actionLabel }}
      </el-button>
    </template>

    <!-- Success state -->
    <template v-else-if="type === 'success'">
      <div class="state-icon success-icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
          <polyline points="22 4 12 14.01 9 11.01" />
        </svg>
      </div>
      <h3 class="state-title">{{ title || '操作成功' }}</h3>
      <p v-if="description" class="state-desc">{{ description }}</p>
      <el-button v-if="actionLabel" class="state-btn" type="primary" @click="$emit('action')">
        {{ actionLabel }}
      </el-button>
    </template>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  type: 'loading' | 'empty' | 'error' | 'success'
  title?: string
  description?: string
  actionLabel?: string
}>()

defineEmits<{
  action: []
}>()
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-10) var(--space-7);
  text-align: center;
}

.state-icon {
  margin-bottom: var(--space-6);
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-icon {
  color: var(--color-muted-foreground);
  opacity: 0.5;
}

.error-icon {
  color: var(--color-error);
  opacity: 0.7;
}

.success-icon {
  color: var(--color-success);
  opacity: 0.7;
}

.state-title {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-foreground);
  margin-bottom: var(--space-2);
}

.state-desc {
  font-size: var(--text-sm);
  color: var(--color-muted-foreground);
  max-width: 320px;
  line-height: 1.6;
  margin-bottom: var(--space-6);
}

.state-btn {
  min-width: 120px;
}

/* Skeleton styles */
.skeleton-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  background: var(--color-muted);
  margin-bottom: var(--space-6);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-title {
  width: 180px;
  height: 20px;
  border-radius: var(--radius-sm);
  background: var(--color-muted);
  margin-bottom: var(--space-3);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-desc {
  width: 260px;
  height: 14px;
  border-radius: var(--radius-sm);
  background: var(--color-muted);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}
</style>
