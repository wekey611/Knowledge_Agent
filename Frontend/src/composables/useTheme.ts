// ========================================
// useTheme — Theme composable for components
// ========================================
import { computed } from 'vue'
import { useThemeStore } from '@/stores/theme'

export function useTheme() {
  const store = useThemeStore()

  const isDark = computed(() => store.isDark)
  const themeIcon = computed(() => store.isDark ? 'Sunny' : 'Moon')

  function toggle() {
    store.toggle()
  }

  return {
    isDark,
    themeIcon,
    toggle,
  }
}
