<template>
  <div class="kb-layout">
    <div class="kb-layout__topbar">
      <button class="back-btn" @click="$router.push('/knowledge')">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6">
          <path d="m15 6-6 6 6 6" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        <span>知识库</span>
      </button>

      <div class="kb-layout__title-block">
        <h1 class="kb-layout__title">{{ kbName || '知识库' }}</h1>
        <span class="kb-layout__id mono">#{{ kbId }}</span>
      </div>

      <div class="kb-layout__tabs">
        <router-link
          v-for="tab in tabs"
          :key="tab.path"
          :to="tab.path"
          custom
          v-slot="{ navigate, isActive }"
        >
          <button
            class="tab-item"
            :class="{ 'tab-item--active': isActive }"
            @click="navigate"
          >
            <component :is="tab.icon" />
            <span>{{ tab.label }}</span>
          </button>
        </router-link>
      </div>

      <div class="kb-layout__right">
        <span v-if="kbScope" class="badge" :class="`badge--${scopeVariant(kbScope)}`">
          <span class="dot" /> {{ SCOPE_LABELS[kbScope] }}
        </span>
        <span v-if="kbStatus" class="kb-layout__status">
          <StatusDot :status="kbStatus" />
          <span class="muted">{{ KB_STATUS_LABELS[kbStatus] }}</span>
        </span>
      </div>
    </div>

    <div class="kb-layout__body">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" :kb-id="kbId" :can-manage="canManage" />
        </transition>
      </router-view>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, h, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import StatusDot from '@/components/common/StatusDot.vue'
import { fetchKnowledgeBase } from '@/api/knowledge'
import { useAuthStore } from '@/stores/auth'
import { KB_STATUS_LABELS, SCOPE_LABELS } from '@/types/knowledge'
import type { KnowledgeBase, KnowledgeScope } from '@/types/knowledge'

const route = useRoute()
const auth = useAuthStore()
const kbId = computed(() => Number(route.params.id))
const kb = ref<KnowledgeBase | null>(null)

const kbName = computed(() => kb.value?.name || '')
const kbScope = computed(() => kb.value?.scope)
const kbStatus = computed(() => kb.value?.status)
const canManage = computed(() => {
  if (!kb.value || !auth.user) return false
  return kb.value.owner_id === auth.user.id || auth.isAdmin
})

async function load() {
  try {
    kb.value = await fetchKnowledgeBase(kbId.value)
  } catch {
    /* ignore */
  }
}

onMounted(load)
watch(kbId, load)

const tabs = [
  {
    path: '',
    label: '对话',
    icon: () => h('svg', { viewBox: '0 0 24 24', width: 16, height: 16, fill: 'none', stroke: 'currentColor', 'stroke-width': 1.6 }, [
      h('path', { d: 'M21 12a8 8 0 0 1-11.6 7.2L4 21l1.8-5.4A8 8 0 1 1 21 12z' }),
    ]),
  },
  {
    path: 'documents',
    label: '文档',
    icon: () => h('svg', { viewBox: '0 0 24 24', width: 16, height: 16, fill: 'none', stroke: 'currentColor', 'stroke-width': 1.6 }, [
      h('path', { d: 'M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z' }),
      h('path', { d: 'M14 3v6h6' }),
    ]),
  },
  {
    path: 'settings',
    label: '设置',
    icon: () => h('svg', { viewBox: '0 0 24 24', width: 16, height: 16, fill: 'none', stroke: 'currentColor', 'stroke-width': 1.6 }, [
      h('circle', { cx: 12, cy: 12, r: 3 }),
      h('path', { d: 'M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z' }),
    ]),
  },
]

function scopeVariant(s: KnowledgeScope): string {
  return s === 'public' ? 'info' : s === 'org' ? 'accent' : 'success'
}
</script>

<style lang="scss" scoped>
@use '@/styles/tokens' as *;

.kb-layout {
  min-height: calc(100vh - #{$topbar-h} - 64px);

  &__topbar {
    display: flex;
    align-items: center;
    gap: $s-4;
    padding: $s-5 0;
    margin-bottom: $s-4;
    border-bottom: 1px solid $border-subtle;
    background: $bg-canvas;
    position: sticky;
    top: $topbar-h;
    z-index: 5;
  }

  &__title-block {
    display: flex;
    align-items: baseline;
    gap: $s-2;
    padding-right: $s-4;
    border-right: 1px solid $border-subtle;
  }
  &__title {
    font-family: $font-display;
    font-size: $fs-20;
    font-weight: $fw-semibold;
    color: $text-primary;
    letter-spacing: -0.01em;
  }
  &__id {
    color: $text-tertiary;
    font-size: $fs-12;
  }

  &__tabs {
    display: flex;
    gap: $s-1;
  }

  &__right {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: $s-3;
  }

  &__status {
    display: inline-flex;
    align-items: center;
    gap: $s-2;
    font-size: $fs-13;
  }

  &__body {
    padding-top: $s-4;
  }
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: $s-2;
  padding: $s-2 $s-3;
  border-radius: $r-md;
  background: transparent;
  border: 1px solid $border-subtle;
  color: $text-secondary;
  font-size: $fs-13;
  cursor: pointer;
  transition: background $dur-base $ease-out, color $dur-base $ease-out;
  &:hover { background: $bg-surface; color: $text-primary; }
}

.tab-item {
  display: inline-flex;
  align-items: center;
  gap: $s-2;
  padding: $s-2 $s-3;
  border-radius: $r-md;
  background: transparent;
  border: none;
  color: $text-secondary;
  font-size: $fs-14;
  font-weight: $fw-medium;
  cursor: pointer;
  transition: background $dur-base $ease-out, color $dur-base $ease-out;

  &:hover { color: $text-primary; background: $bg-surface; }
  &--active {
    color: $accent;
    background: $bg-surface;
    box-shadow: inset 0 -1px 0 $accent;
  }
}

.fade-enter-active, .fade-leave-active { transition: opacity $dur-base $ease-out; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>