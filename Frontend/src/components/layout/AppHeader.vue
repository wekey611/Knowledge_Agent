<template>
  <header class="app-header">
    <div class="header-left">
      <button class="collapse-btn" @click="$emit('toggle')">
        <svg
          width="20" height="20" viewBox="0 0 24 24"
          fill="none" stroke="currentColor" stroke-width="2"
          stroke-linecap="round" stroke-linejoin="round"
        >
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>
      <div class="header-breadcrumb">
        <router-link
          v-for="(crumb, index) in breadcrumbs"
          :key="crumb.path"
          :to="crumb.path"
          class="breadcrumb-item"
          :class="{ active: index === breadcrumbs.length - 1 }"
        >
          {{ crumb.label }}
          <span v-if="index < breadcrumbs.length - 1" class="breadcrumb-sep">/</span>
        </router-link>
      </div>
    </div>

    <div class="header-right">
      <ThemeToggle />
      <el-dropdown trigger="click" @command="handleCommand">
        <button class="user-dropdown-btn">
          <UserAvatar
            :email="authStore.user?.email"
            :is-admin="authStore.isAdmin"
          />
          <svg
            width="14" height="14" viewBox="0 0 24 24"
            fill="none" stroke="currentColor" stroke-width="2"
            stroke-linecap="round" stroke-linejoin="round"
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><UserFilled /></el-icon>
              个人信息
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { UserFilled, SwitchButton } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useKnowledgeStore } from '@/stores/knowledge'
import UserAvatar from '@/components/common/UserAvatar.vue'
import ThemeToggle from '@/components/common/ThemeToggle.vue'

defineEmits<{
  toggle: []
}>()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const knowledgeStore = useKnowledgeStore()

const breadcrumbs = computed(() => {
  const crumbs: { label: string; path: string }[] = []

  if (route.path.startsWith('/dashboard')) {
    crumbs.push({ label: '仪表盘', path: '/dashboard' })
  } else if (route.path.startsWith('/admin/requests')) {
    crumbs.push({ label: '管理', path: '/admin/requests' })
    crumbs.push({ label: '注册申请', path: '/admin/requests' })
  } else if (route.path.startsWith('/knowledge/')) {
    crumbs.push({ label: '知识库', path: '/dashboard' })
    const kbMatch = route.path.match(/\/knowledge\/(\d+)/)
    if (kbMatch) {
      const kbId = parseInt(kbMatch[1])
      const kb = knowledgeStore.getKnowledgeBase(kbId)
      crumbs.push({ label: kb?.name || `知识库 #${kbId}`, path: route.path })
    } else {
      crumbs.push({ label: '知识库', path: route.path })
    }
  }

  return crumbs.length > 0 ? crumbs : [{ label: 'Knowledge Agent', path: '/' }]
})

function handleCommand(command: string) {
  if (command === 'logout') {
    authStore.logout()
    router.push('/auth/login')
  }
}
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--header-height);
  padding: 0 var(--space-7);
  background: var(--color-card);
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
  gap: var(--space-5);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  flex: 1;
  min-width: 0;
}

.collapse-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  border: none;
  background: transparent;
  color: var(--color-muted-foreground);
  cursor: pointer;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.collapse-btn:hover {
  background: var(--color-muted);
  color: var(--color-foreground);
}

.header-breadcrumb {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  min-width: 0;
  overflow: hidden;
}

.breadcrumb-item {
  font-size: var(--text-sm);
  color: var(--color-muted-foreground);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  white-space: nowrap;
  transition: color var(--transition-fast);
}

.breadcrumb-item:hover:not(.active) {
  color: var(--color-foreground);
}

.breadcrumb-item.active {
  font-weight: 600;
  color: var(--color-foreground);
  cursor: default;
}

.breadcrumb-sep {
  color: var(--color-border);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-shrink: 0;
}

.user-dropdown-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-light);
  background: transparent;
  cursor: pointer;
  color: var(--color-muted-foreground);
  transition: all var(--transition-fast);
}

.user-dropdown-btn:hover {
  border-color: var(--color-border);
  background: var(--color-muted);
}
</style>
