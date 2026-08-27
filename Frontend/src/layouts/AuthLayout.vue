<template>
  <div class="auth-layout">
    <div class="auth-layout__panel">
      <div class="auth-layout__brand">
        <AppLogo size="lg" />
        <h1 class="auth-layout__title">知识库 · Agent 问答</h1>
        <p class="auth-layout__sub">上传文件，构建索引，向你的知识提问。</p>
      </div>
      <div class="auth-layout__art" aria-hidden="true">
        <svg viewBox="0 0 360 360" width="100%" height="100%">
          <defs>
            <linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stop-color="#A8E6CF" stop-opacity="0.3" />
              <stop offset="100%" stop-color="#A8E6CF" stop-opacity="0" />
            </linearGradient>
          </defs>
          <circle cx="180" cy="180" r="160" fill="url(#g1)" />
          <g stroke="#A8E6CF" stroke-width="1" fill="none" opacity="0.3">
            <circle cx="180" cy="180" r="50" />
            <circle cx="180" cy="180" r="90" />
            <circle cx="180" cy="180" r="130" />
          </g>
          <g fill="#A8E6CF">
            <circle cx="180" cy="50" r="2.5" />
            <circle cx="310" cy="180" r="2.5" />
            <circle cx="180" cy="310" r="2.5" />
            <circle cx="50" cy="180" r="2.5" />
            <circle cx="60" cy="60" r="1.5" opacity="0.6" />
            <circle cx="300" cy="60" r="1.5" opacity="0.6" />
            <circle cx="60" cy="300" r="1.5" opacity="0.6" />
            <circle cx="300" cy="300" r="1.5" opacity="0.6" />
          </g>
          <g stroke="rgba(255,255,255,0.06)" stroke-width="1">
            <line x1="0" y1="180" x2="360" y2="180" />
            <line x1="180" y1="0" x2="180" y2="360" />
          </g>
        </svg>
      </div>
    </div>
    <div class="auth-layout__form">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import AppLogo from '@/components/common/AppLogo.vue'
</script>

<style lang="scss" scoped>
@use '@/styles/tokens' as *;

.auth-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 100vh;
  background: $bg-canvas;

  &__panel {
    position: relative;
    padding: $s-14;
    border-right: 1px solid $border-subtle;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background:
      radial-gradient(circle at 30% 20%, rgba(168, 230, 207, 0.06) 0%, transparent 50%),
      $bg-canvas;
  }

  &__brand {
    position: relative;
    z-index: 2;
    max-width: 380px;
  }

  &__title {
    margin-top: $s-8;
    font-family: $font-display;
    font-size: $fs-44;
    font-weight: $fw-semibold;
    line-height: 1.05;
    letter-spacing: -0.02em;
    color: $text-primary;
    font-variation-settings: "opsz" 144;
  }
  &__sub {
    margin-top: $s-4;
    color: $text-secondary;
    font-size: $fs-17;
    line-height: $lh-snug;
    max-width: 360px;
  }

  &__art {
    position: absolute;
    inset: auto -80px -80px auto;
    width: 540px;
    height: 540px;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1;
    opacity: 0.7;
    pointer-events: none;
  }

  &__form {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: $s-10;
  }

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
    &__panel { padding: $s-8; min-height: 240px; }
    &__art { display: none; }
  }
}
</style>