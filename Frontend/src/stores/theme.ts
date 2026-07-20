// ========================================
// Theme Store — Dark Mode State
// ========================================
import { defineStore } from 'pinia'
import { ref } from 'vue'

type Theme = 'light' | 'dark'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref<boolean>(false)

  function init() {
    // 1. Check localStorage
    const stored = localStorage.getItem('theme')
    if (stored === 'dark' || stored === 'light') {
      isDark.value = stored === 'dark'
    } else {
      // 2. Fallback to system preference
      isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    applyTheme()
  }

  function toggle() {
    isDark.value = !isDark.value
    applyTheme()
  }

  function applyTheme() {
    const theme: Theme = isDark.value ? 'dark' : 'light'
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }

  // Watch the system preference changes
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  mediaQuery.addEventListener('change', (e) => {
    if (!localStorage.getItem('theme')) {
      isDark.value = e.matches
      applyTheme()
    }
  })

  return { isDark, init, toggle }
})
