<template>
  <span class="kb-status-dot" :class="`kb-status-dot--${status}`" :title="label">
    <span class="dot-core"></span>
  </span>
</template>

<script setup lang="ts">
import type { KBStatus } from '@/types/knowledge'
import { KB_STATUS_LABELS } from '@/types/knowledge'
import { computed } from 'vue'

const props = defineProps<{ status: KBStatus }>()
const label = computed(() => KB_STATUS_LABELS[props.status])
</script>

<style lang="scss" scoped>
@use '@/styles/tokens' as *;

.kb-status-dot {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: $bg-elevated;
  border: 1px solid $border-subtle;

  .dot-core {
    width: 6px;
    height: 6px;
    border-radius: 50%;
  }

  &--active {
    .dot-core { background: $success; box-shadow: 0 0 0 3px $success-soft; }
  }
  &--provisioning {
    .dot-core {
      background: $warning;
      animation: kbpulse 2s $ease-out infinite;
    }
  }
  &--archived {
    .dot-core { background: $text-tertiary; }
  }
  &--failed {
    .dot-core { background: $danger; }
  }
}

@keyframes kbpulse {
  0%, 100% { box-shadow: 0 0 0 0 $warning-soft; }
  50% { box-shadow: 0 0 0 5px transparent; }
}
</style>