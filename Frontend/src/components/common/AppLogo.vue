<template>
  <div class="app-logo" @click="$router.push('/dashboard')">
    <div class="logo-icon">
      <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect width="28" height="28" rx="8" fill="url(#logo-gradient)" />
        <path
          d="M14 6C9.58 6 6 9.58 6 14s3.58 8 8 8 8-3.58 8-8-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6s2.69-6 6-6 6 2.69 6 6-2.69 6-6 6z"
          fill="white"
          opacity="0.9"
        />
        <path
          d="M14 9c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-2.21 0-4 1.79-4 4h8c0-2.21-1.79-4-4-4z"
          fill="white"
        />
        <defs>
          <linearGradient id="logo-gradient" x1="0" y1="0" x2="28" y2="28" gradientUnits="userSpaceOnUse">
            <stop class="grad-stop-start" />
            <stop class="grad-stop-end" offset="1" />
          </linearGradient>
        </defs>
      </svg>
    </div>
    <span v-if="showText" class="logo-text">Knowledge Agent</span>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  showText?: boolean
}>(), {
  showText: true,
})
</script>

<style scoped>
.app-logo {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  cursor: pointer;
  user-select: none;
}

.logo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.logo-text {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  font-weight: 700;
  white-space: nowrap;
  background: var(--gradient-accent);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* SVG gradient colors — controlled via CSS vars */
.grad-stop-start { stop-color: var(--color-primary); }
.grad-stop-end { stop-color: var(--color-accent); }
</style>
