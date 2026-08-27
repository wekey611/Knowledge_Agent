<template>
  <div class="empty-state">
    <div class="empty-state__icon">
      <slot name="icon">
        <svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="3" y="4" width="18" height="16" rx="2" />
          <path d="M3 10h18M9 4v16" />
        </svg>
      </slot>
    </div>
    <h3 class="empty-state__title">{{ title }}</h3>
    <p v-if="description" class="empty-state__desc">{{ description }}</p>
    <div v-if="$slots.action" class="empty-state__action">
      <slot name="action" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string; description?: string }>()
</script>

<style lang="scss" scoped>
@use '@/styles/tokens' as *;

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: $s-14 $s-6;
  text-align: center;

  &__icon {
    width: 64px;
    height: 64px;
    border-radius: $r-lg;
    background: $bg-surface;
    border: 1px solid $border-subtle;
    color: $text-tertiary;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: $s-4;
  }
  &__title {
    font-family: $font-display;
    font-size: $fs-20;
    color: $text-primary;
    margin-bottom: $s-2;
  }
  &__desc {
    color: $text-secondary;
    font-size: $fs-14;
    max-width: 360px;
    line-height: $lh-normal;
  }
  &__action {
    margin-top: $s-5;
  }
}
</style>