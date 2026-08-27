<template>
  <div class="logo-mark" :class="{ 'logo-mark--lg': size === 'lg' }">
    <svg viewBox="0 0 32 32" width="100%" height="100%" fill="none">
      <rect x="2" y="2" width="28" height="28" rx="7" fill="#16181F" stroke="rgba(255,255,255,0.08)" />
      <path d="M9 8h7a5 5 0 0 1 5 5v6a5 5 0 0 1-5 5H9z" stroke="#A8E6CF" stroke-width="1.5" />
      <path d="M13 13h2M13 17h6M13 21h4" stroke="#A8E6CF" stroke-width="1.5" stroke-linecap="round" />
    </svg>
    <span v-if="withText" class="logo-mark__text">
      <span class="logo-mark__brand">Knowledge</span><span class="logo-mark__brand-accent">·</span><span class="logo-mark__brand">Agent</span>
    </span>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ size?: 'md' | 'lg'; withText?: boolean }>(), {
  size: 'md',
  withText: true,
})
</script>

<style lang="scss" scoped>
@use '@/styles/tokens' as *;

.logo-mark {
  display: inline-flex;
  align-items: center;
  gap: $s-2;

  svg {
    width: 24px;
    height: 24px;
  }

  &--lg svg {
    width: 36px;
    height: 36px;
  }

  &__text {
    display: inline-flex;
    align-items: baseline;
    font-family: $font-display;
    font-size: $fs-17;
    font-weight: $fw-semibold;
    letter-spacing: -0.01em;
    color: $text-primary;
  }
  &__brand-accent {
    color: $accent;
    margin: 0 2px;
    font-weight: $fw-regular;
  }
}
</style>