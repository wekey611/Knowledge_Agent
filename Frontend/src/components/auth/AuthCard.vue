<template>
  <div class="auth-card">
    <div class="auth-card-header">
      <AppLogo />
      <h1 class="auth-title">{{ title }}</h1>
      <p v-if="subtitle" class="auth-subtitle">{{ subtitle }}</p>
    </div>
    <div class="auth-card-body">
      <slot />
    </div>
    <div v-if="$slots.footer" class="auth-card-footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import AppLogo from '@/components/common/AppLogo.vue'

defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<style scoped>
.auth-card {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl), var(--glass-shadow);
  padding: var(--space-9) var(--space-8);
  width: 100%;
  border: 1px solid var(--glass-border);
}

.auth-card-header {
  text-align: center;
  margin-bottom: var(--space-8);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-5);
}

.auth-title {
  font-family: var(--font-heading);
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--color-foreground);
  line-height: 1.3;
}

.auth-subtitle {
  font-size: var(--text-sm);
  color: var(--color-muted-foreground);
  line-height: 1.6;
  max-width: 320px;
  margin: 0 auto;
}

.auth-card-body {
  max-width: 360px;
  margin: 0 auto;
}

.auth-card-footer {
  margin-top: var(--space-7);
  padding-top: var(--space-6);
  border-top: 1px solid var(--color-border-light);
  text-align: center;
}
</style>
