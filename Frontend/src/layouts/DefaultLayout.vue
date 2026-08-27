<template>
  <div class="default-layout">
    <aside class="default-layout__sidebar">
      <div class="sidebar__brand">
        <AppLogo />
      </div>

      <nav class="sidebar__nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ 'nav-item--active': isActive(item.path) }"
        >
          <component :is="item.icon" class="nav-item__icon" />
          <span>{{ item.label }}</span>
          <span v-if="item.badge" class="nav-item__badge">{{ item.badge }}</span>
        </router-link>
      </nav>

      <div class="sidebar__footer">
        <div class="sidebar__hint">
          <span class="eyebrow">RAG · Agent</span>
          <p>知识检索与问答即将上线</p>
        </div>
      </div>
    </aside>

    <div class="default-layout__main">
      <header class="topbar">
        <div class="topbar__bread">
          <span class="muted">{{ breadcrumb[0] }}</span>
          <span v-if="breadcrumb[1]" class="muted faint">/</span>
          <span v-if="breadcrumb[1]">{{ breadcrumb[1] }}</span>
        </div>
        <div class="topbar__spacer" />
        <div class="topbar__actions">
          <button class="btn btn--ghost btn--icon btn--sm" title="搜索">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6">
              <circle cx="11" cy="11" r="7" />
              <path d="m20 20-3.5-3.5" stroke-linecap="round" />
            </svg>
          </button>
          <button class="btn btn--ghost btn--icon btn--sm" title="帮助">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6">
              <circle cx="12" cy="12" r="9" />
              <path d="M9.5 9a2.5 2.5 0 0 1 5 0c0 1.5-2.5 2-2.5 4M12 17h.01" stroke-linecap="round" />
            </svg>
          </button>
          <div class="topbar__user" @click="menuOpen = !menuOpen" v-click-outside="() => menuOpen = false">
            <UserAvatar :user="auth.user" />
            <div class="topbar__user-meta">
              <span class="topbar__user-email">{{ auth.user?.email || '未登录' }}</span>
              <span class="eyebrow">{{ auth.isAdmin ? '管理员' : '成员' }}</span>
            </div>
            <transition name="menu">
              <div v-if="menuOpen" class="user-menu" @click.stop>
                <router-link to="/dashboard" class="user-menu__item" @click="menuOpen = false">
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>
                  工作台
                </router-link>
                <div class="user-menu__sep" />
                <button class="user-menu__item user-menu__item--danger" @click="handleLogout">
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M15 4h4a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-4M10 17l-5-5 5-5M5 12h12" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  退出登录
                </button>
              </div>
            </transition>
          </div>
        </div>
      </header>

      <main class="default-layout__content">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, h, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLogo from '@/components/common/AppLogo.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import { useAuthStore } from '@/stores/auth'
import type { Component, Directive } from 'vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const menuOpen = ref(false)

function iconSvg(paths: unknown[]): Component {
  // 简易 SVG icon 组件
  return {
    render() {
      return h(
        'svg',
        { viewBox: '0 0 24 24', width: 16, height: 16, fill: 'none', stroke: 'currentColor', 'stroke-width': 1.6 },
        paths as any
      )
    },
  }
}

const navItems: { path: string; label: string; icon: Component; badge?: string }[] = [
  {
    path: '/dashboard',
    label: '工作台',
    icon: iconSvg([
      h('rect', { x: 3, y: 3, width: 7, height: 7, rx: 1.5 }),
      h('rect', { x: 14, y: 3, width: 7, height: 7, rx: 1.5 }),
      h('rect', { x: 3, y: 14, width: 7, height: 7, rx: 1.5 }),
      h('rect', { x: 14, y: 14, width: 7, height: 7, rx: 1.5 }),
    ]),
  },
  {
    path: '/knowledge',
    label: '知识库',
    icon: iconSvg([
      h('path', { d: 'M4 5a2 2 0 0 1 2-2h3l2 2h7a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2z' }),
      h('path', { d: 'M8 9h8M8 13h6', 'stroke-linecap': 'round' }),
    ]),
  },
  {
    path: '/organizations',
    label: '组织',
    icon: iconSvg([
      h('circle', { cx: 9, cy: 8, r: 3 }),
      h('path', { d: 'M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6' }),
      h('circle', { cx: 17, cy: 6, r: 2.5 }),
      h('path', { d: 'M15 13v-.5c0-1.4 1.1-2.5 2.5-2.5s2.5 1.1 2.5 2.5' }),
    ]),
  },
  {
    path: '/request',
    label: '我的申请',
    icon: iconSvg([
      h('rect', { x: 4, y: 3, width: 16, height: 18, rx: 2 }),
      h('path', { d: 'M8 8h8M8 12h8M8 16h5', 'stroke-linecap': 'round' }),
    ]),
  },
]

if (auth.isAdmin) {
  navItems.push({
    path: '/admin/requests',
    label: '审核',
    icon: iconSvg([
      h('path', { d: 'M12 2 4 6v6c0 5 3.5 8.5 8 10 4.5-1.5 8-5 8-10V6z' }),
      h('path', { d: 'm9 12 2 2 4-4', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }),
    ]),
  })
}

function isActive(path: string) {
  if (path === '/dashboard') return route.path === '/dashboard' || route.path === '/'
  return route.path.startsWith(path)
}

const breadcrumb = computed(() => {
  if (route.path.startsWith('/knowledge/')) return ['知识库', '对话']
  if (route.path === '/knowledge') return ['知识库', '总览']
  if (route.path.startsWith('/organizations/')) return ['组织', '详情']
  if (route.path === '/organizations') return ['组织', '我的组织']
  if (route.path.startsWith('/admin')) return ['管理员', '审核']
  if (route.path === '/dashboard') return ['工作台', '总览']
  if (route.path === '/request') return ['申请', '账号']
  return ['', '']
})

function handleLogout() {
  menuOpen.value = false
  auth.logout()
  router.push({ name: 'Login' })
}

const vClickOutside: Directive = {
  mounted(el, binding) {
    ;(el as HTMLElement & { __clickOutside__?: (e: MouseEvent) => void }).__clickOutside__ = (e: MouseEvent) => {
      if (!el.contains(e.target as Node)) binding.value()
    }
    document.addEventListener('click', (el as HTMLElement & { __clickOutside__?: (e: MouseEvent) => void }).__clickOutside__!)
  },
  unmounted(el) {
    const fn = (el as HTMLElement & { __clickOutside__?: (e: MouseEvent) => void }).__clickOutside__
    if (fn) document.removeEventListener('click', fn)
  },
}
</script>

<style lang="scss" scoped>
@use '@/styles/tokens' as *;

.default-layout {
  display: flex;
  min-height: 100vh;
  background: $bg-canvas;

  &__sidebar {
    width: $sidebar-w;
    flex-shrink: 0;
    background: $bg-canvas;
    border-right: 1px solid $border-subtle;
    display: flex;
    flex-direction: column;
    position: sticky;
    top: 0;
    height: 100vh;
  }

  &__main {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
  }

  &__content {
    flex: 1;
    padding: $s-8 $s-10;
    max-width: $content-max;
    width: 100%;
    margin: 0 auto;
  }
}

.sidebar__brand {
  padding: $s-5 $s-5 $s-6;
  border-bottom: 1px solid $border-subtle;
}

.sidebar__nav {
  flex: 1;
  padding: $s-4 $s-3;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: $s-3;
  padding: $s-2 $s-3;
  border-radius: $r-md;
  color: $text-secondary;
  font-size: $fs-14;
  font-weight: $fw-medium;
  cursor: pointer;
  transition: background $dur-base $ease-out, color $dur-base $ease-out;

  &__icon { color: $text-tertiary; }
  &:hover {
    background: $bg-surface;
    color: $text-primary;
    .nav-item__icon { color: $text-secondary; }
  }

  &--active {
    background: $bg-surface;
    color: $accent;
    box-shadow: inset 2px 0 0 $accent;
    .nav-item__icon { color: $accent; }
  }
  &__badge {
    margin-left: auto;
    background: $accent-soft;
    color: $accent;
    font-family: $font-mono;
    font-size: $fs-12;
    padding: 1px 6px;
    border-radius: $r-sm;
  }
}

.sidebar__footer {
  padding: $s-4 $s-4 $s-5;
  border-top: 1px solid $border-subtle;
}

.sidebar__hint {
  padding: $s-3 $s-3;
  border-radius: $r-md;
  background: $bg-surface;
  border: 1px dashed $border-subtle;

  .eyebrow { display: block; margin-bottom: $s-1; }
  p {
    font-size: $fs-12;
    color: $text-tertiary;
    line-height: $lh-snug;
    margin-top: $s-1;
  }
}

.topbar {
  height: $topbar-h;
  display: flex;
  align-items: center;
  gap: $s-4;
  padding: 0 $s-10;
  border-bottom: 1px solid $border-subtle;
  background: rgba(14, 15, 19, 0.85);
  backdrop-filter: blur(12px);
  position: sticky;
  top: 0;
  z-index: 10;

  &__bread {
    display: flex;
    align-items: center;
    gap: $s-2;
    font-size: $fs-13;
  }
  &__spacer { flex: 1; }
  &__actions {
    display: flex;
    align-items: center;
    gap: $s-2;
  }
  &__user {
    display: flex;
    align-items: center;
    gap: $s-2;
    padding: $s-1 $s-2 $s-1 $s-1;
    border-radius: $r-md;
    cursor: pointer;
    position: relative;
    transition: background $dur-base $ease-out;
    &:hover { background: $bg-surface; }
  }
  &__user-meta {
    display: flex;
    flex-direction: column;
    line-height: 1.1;
  }
  &__user-email {
    font-size: $fs-13;
    color: $text-primary;
  }
}

.user-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 160px;
  background: $bg-elevated;
  border: 1px solid $border-strong;
  border-radius: $r-md;
  box-shadow: $shadow-md;
  padding: $s-1;
  z-index: 20;

  &__item {
    display: flex;
    align-items: center;
    gap: $s-2;
    width: 100%;
    padding: $s-2 $s-3;
    border-radius: $r-sm;
    font-size: $fs-13;
    color: $text-primary;
    background: transparent;
    border: none;
    text-align: left;
    cursor: pointer;
    transition: background $dur-fast $ease-out;
    &:hover { background: $bg-surface; }
    &--danger { color: $danger; &:hover { background: $danger-soft; } }
  }
  &__sep {
    height: 1px;
    background: $border-subtle;
    margin: $s-1 0;
  }
}

.menu-enter-active, .menu-leave-active {
  transition: opacity $dur-fast $ease-out, transform $dur-fast $ease-out;
}
.menu-enter-from, .menu-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>