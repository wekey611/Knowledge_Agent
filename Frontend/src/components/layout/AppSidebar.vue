<template>
  <aside class="app-sidebar" :class="{ collapsed: isCollapsed }">
    <!-- Logo -->
    <div class="sidebar-logo">
      <AppLogo :show-text="!isCollapsed" />
    </div>

    <!-- User info -->
    <div class="sidebar-user" @click="toggleCollapse">
      <UserAvatar
        :email="authStore.user?.email"
        :is-admin="authStore.isAdmin"
        :show-info="!isCollapsed"
        :dark-bg="isDarkMode"
      />
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ active: route.path === item.path, collapsed: isCollapsed }"
      >
        <el-icon :size="20" class="nav-icon">
          <component :is="item.icon" />
        </el-icon>
        <span v-show="!isCollapsed" class="nav-label">{{ item.label }}</span>
      </router-link>
    </nav>

    <!-- Knowledge bases (collapsible section) -->
    <div v-if="knowledgeStore.knowledgeBases.length > 0" class="sidebar-section">
      <div v-show="!isCollapsed" class="section-label">知识库</div>
      <router-link
        v-for="kb in knowledgeStore.knowledgeBases"
        :key="kb.id"
        :to="`/knowledge/${kb.id}`"
        class="nav-item kb-item"
        :class="{ active: route.path.startsWith(`/knowledge/${kb.id}`), collapsed: isCollapsed }"
      >
        <div class="kb-dot" :style="{ background: kbColor(kb) }" />
        <span v-show="!isCollapsed" class="nav-label">{{ kb.name }}</span>
      </router-link>
    </div>

    <!-- Spacer -->
    <div class="sidebar-spacer" />

    <!-- Decorative gradient accent -->
    <div class="sidebar-accent-bar" />

    <!-- Theme toggle + Logout at bottom -->
    <div class="sidebar-footer">
      <button class="sidebar-logout" :title="'退出登录'" @click="handleLogout">
        <el-icon :size="20"><SwitchButton /></el-icon>
        <span v-show="!isCollapsed" class="nav-label">退出登录</span>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { HomeFilled, List, OfficeBuilding, SwitchButton } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useKnowledgeStore } from '@/stores/knowledge'
import { useThemeStore } from '@/stores/theme'
import { SCOPE_COLORS, type KnowledgeBaseSimple } from '@/types/knowledge'
import AppLogo from '@/components/common/AppLogo.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'

defineProps<{
  isCollapsed: boolean
}>()

const emit = defineEmits<{
  toggle: []
}>()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const knowledgeStore = useKnowledgeStore()
const themeStore = useThemeStore()

const isDarkMode = computed(() => themeStore.isDark)

function toggleCollapse() {
  emit('toggle')
}

const navItems = computed(() => {
  const items = [
    { path: '/dashboard', label: '首页', icon: HomeFilled },
    { path: '/organizations', label: '组织', icon: OfficeBuilding },
  ]
  if (authStore.isAdmin) {
    items.push({ path: '/admin/requests', label: '申请管理', icon: List })
  }
  return items
})

function kbColor(kb: KnowledgeBaseSimple): string {
  return SCOPE_COLORS[kb.scope] || 'var(--color-primary)'
}

function handleLogout() {
  authStore.logout()
  router.push('/auth/login')
}
</script>

<style scoped>
.app-sidebar {
  display: flex;
  flex-direction: column;
  width: var(--sidebar-width);
  min-height: 100vh;
  background: var(--sidebar-bg);
  transition: width var(--transition-normal);
  overflow: hidden;
  flex-shrink: 0;
  z-index: 100;
}

.app-sidebar.collapsed {
  width: var(--sidebar-collapsed-width);
}

.sidebar-logo {
  padding: var(--space-6) var(--space-5);
  border-bottom: 1px solid var(--sidebar-border);
  display: flex;
  justify-content: center;
}

.sidebar-user {
  padding: var(--space-5);
  border-bottom: 1px solid var(--sidebar-border);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.sidebar-user:hover {
  background: var(--sidebar-hover);
}

.sidebar-nav {
  padding: var(--space-3);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  color: var(--sidebar-text);
  text-decoration: none;
  transition: all var(--transition-fast);
  cursor: pointer;
  white-space: nowrap;
}

.nav-item:hover {
  color: var(--sidebar-text-active);
  background: var(--sidebar-hover);
}

.nav-item.active {
  color: var(--sidebar-text-active);
  background: var(--gradient-primary);
  opacity: 0.9;
  box-shadow: inset 3px 0 0 var(--color-cyan);
}

.nav-item.collapsed {
  justify-content: center;
  padding: var(--space-3);
}

.nav-icon {
  flex-shrink: 0;
}

.nav-label {
  font-size: var(--text-sm);
  font-weight: 500;
  overflow: hidden;
}

/* Knowledge bases section */
.sidebar-section {
  padding: var(--space-3);
  border-top: 1px solid var(--sidebar-border);
}

.section-label {
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--sidebar-text);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: var(--space-3) var(--space-4);
  opacity: 0.6;
}

.kb-item {
  gap: var(--space-3);
}

.kb-dot {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
  flex-shrink: 0;
}

/* Decorative accent bar */
.sidebar-accent-bar {
  height: 3px;
  margin: 0 var(--space-5);
  background: var(--gradient-tech);
  border-radius: 2px;
  opacity: 0.6;
  flex-shrink: 0;
}

/* Spacer and footer */
.sidebar-spacer {
  flex: 1;
}

.sidebar-footer {
  padding: var(--space-3);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  border-top: 1px solid var(--sidebar-border);
}

.sidebar-logout {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  color: var(--sidebar-text);
  background: none;
  border: none;
  cursor: pointer;
  font-size: var(--text-sm);
  font-family: var(--font-body);
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.sidebar-logout:hover {
  color: var(--color-error);
  background: rgba(239, 68, 68, 0.1);
}
</style>
