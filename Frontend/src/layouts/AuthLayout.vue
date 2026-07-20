<template>
  <div class="auth-layout">
    <div class="auth-container">
      <div class="auth-decoration" />
      <div class="auth-content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.auth-layout {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, var(--auth-bg-start) 0%, var(--auth-bg-mid) 50%, var(--auth-bg-end) 100%);
  padding: var(--space-7);
  position: relative;
  overflow: hidden;
}

.auth-container {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: var(--auth-card-width);
  position: relative;
}

/* Decorative background elements */
.auth-decoration {
  position: fixed;
  top: -200px;
  right: -200px;
  width: 500px;
  height: 500px;
  border-radius: 50%;
  background: radial-gradient(circle, color-mix(in srgb, var(--color-primary) 6%, transparent) 0%, transparent 70%);
  pointer-events: none;
}

.auth-decoration::after {
  content: '';
  position: fixed;
  bottom: -200px;
  left: -200px;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  background: radial-gradient(circle, color-mix(in srgb, var(--color-accent) 5%, transparent) 0%, transparent 70%);
  pointer-events: none;
}

.auth-content {
  width: 100%;
  position: relative;
  z-index: 1;
}
</style>
