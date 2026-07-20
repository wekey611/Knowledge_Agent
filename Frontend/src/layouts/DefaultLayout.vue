<template>
  <div class="default-layout">
    <AppSidebar
      :is-collapsed="isCollapsed"
      @toggle="isCollapsed = !isCollapsed"
    />
    <div class="layout-right">
      <AppHeader @toggle="isCollapsed = !isCollapsed" />
      <main class="layout-main">
        <router-view v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'

const isCollapsed = ref(false)
</script>

<style scoped>
.default-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.layout-right {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.layout-main {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-7);
  background: var(--color-bg);
}

/* Page transition */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity var(--transition-normal), transform var(--transition-normal);
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
