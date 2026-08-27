<template>
  <div class="user-avatar" :title="user?.email || ''">
    {{ initials }}
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { User } from '@/types/api'

const props = defineProps<{ user: User | null; size?: number }>()

const initials = computed(() => {
  if (!props.user?.email) return '·'
  const e = props.user.email
  return e[0].toUpperCase()
})
</script>

<style lang="scss" scoped>
@use '@/styles/tokens' as *;

.user-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: $bg-elevated;
  border: 1px solid $border-subtle;
  color: $accent;
  font-family: $font-display;
  font-size: $fs-14;
  font-weight: $fw-semibold;
  user-select: none;
}
</style>