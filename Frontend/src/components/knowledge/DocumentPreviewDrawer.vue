<template>
  <transition name="drawer">
    <aside v-if="modelValue" class="preview-drawer">
      <header class="preview-drawer__head">
        <div class="preview-drawer__meta">
          <span class="eyebrow">文档预览</span>
          <h3 class="preview-drawer__title">{{ doc?.title }}</h3>
          <div class="preview-drawer__info mono">
            <span>{{ formatSize(doc?.file_size) }}</span>
            <span class="faint">·</span>
            <span>{{ formatDate(doc?.updated_at) }}</span>
            <span class="faint">·</span>
            <span>{{ extLabel }}</span>
          </div>
        </div>
        <div class="preview-drawer__actions">
          <button class="btn btn--ghost btn--icon btn--sm" title="全屏预览" @click="$emit('fullscreen')">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6">
              <path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </button>
          <button class="btn btn--ghost btn--icon btn--sm" title="关闭" @click="$emit('update:modelValue', false)">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6">
              <path d="M6 6l12 12M6 18L18 6" stroke-linecap="round" />
            </svg>
          </button>
        </div>
      </header>

      <div class="preview-drawer__body">
        <div v-if="!src" class="preview-drawer__loading">
          <span class="spinner" />
          <p class="muted">加载中…</p>
        </div>
        <iframe
          v-else-if="kind === 'pdf' && !isDemo"
          :src="src"
          class="preview-drawer__iframe"
          :title="doc?.title"
        />
        <pre v-else-if="kind === 'text' || (kind === 'pdf' && isDemo)" class="preview-drawer__text">{{ textContent }}</pre>
        <div v-else-if="kind === 'markdown'" class="preview-drawer__md" v-html="renderedMarkdown" />
        <div v-else class="preview-drawer__unsupported">
          <p>此文件类型暂不支持预览</p>
          <p class="muted">{{ extLabel }}</p>
        </div>
      </div>
    </aside>
  </transition>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { DocumentSimple } from '@/types/knowledge'

const props = defineProps<{
  modelValue: boolean
  doc: DocumentSimple | null
  src: string | null
  previewKey?: number
}>()
defineEmits<{ 'update:modelValue': [v: boolean]; 'fullscreen': [] }>()

const textContent = ref<string>('')
const isDemo = computed(() => (localStorage.getItem('access_token') || '').startsWith('demo.'))

async function loadContent(src: string) {
  textContent.value = ''
  if (kind.value === 'text' || kind.value === 'markdown' || (kind.value === 'pdf' && isDemo.value)) {
    try {
      const res = await fetch(src)
      textContent.value = await res.text()
    } catch {
      textContent.value = '无法加载预览内容'
    }
  }
}

watch(
  () => props.src,
  async (src) => {
    if (!src || !props.modelValue) return
    await loadContent(src)
  },
  { immediate: true }
)

// 每次打开新文档预览时强制重新加载（src 可能复用同一 URL 被浏览器缓存）
watch(
  () => props.previewKey,
  async (key) => {
    if (key && props.modelValue && props.src) await loadContent(props.src)
  },
  { immediate: true }
)

const ext = computed(() => {
  const name = props.doc?.filename || ''
  return name.split('.').pop()?.toLowerCase() || ''
})

const kind = computed<'pdf' | 'text' | 'markdown' | 'unsupported'>(() => {
  if (ext.value === 'pdf') return 'pdf'
  if (ext.value === 'md' || ext.value === 'markdown') return 'markdown'
  if (ext.value === 'txt') return 'text'
  return 'unsupported'
})

const extLabel = computed(() => ext.value.toUpperCase() || '—')

const renderedMarkdown = computed(() => renderMd(textContent.value))

function formatSize(bytes?: number) {
  if (!bytes) return '—'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(iso?: string) {
  if (!iso) return ''
  try {
    return new Date(iso).toLocaleString('zh-CN', { dateStyle: 'short' })
  } catch {
    return iso
  }
}

function escapeHtml(s: string) {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

function renderMd(src: string) {
  if (!src) return ''
  const lines = src.split(/\r?\n/)
  let html = ''
  let inList = false
  for (const raw of lines) {
    const line = raw.replace(/\s+$/, '')
    if (/^#{1,6}\s/.test(line)) {
      if (inList) { html += '</ul>'; inList = false }
      const level = (line.match(/^#+/) || ['#'])[0].length
      const text = line.replace(/^#+\s*/, '')
      html += `<h${level}>${inline(escapeHtml(text))}</h${level}>`
    } else if (/^[-*]\s+/.test(line)) {
      if (!inList) { html += '<ul>'; inList = true }
      html += `<li>${inline(escapeHtml(line.replace(/^[-*]\s+/, '')))}</li>`
    } else if (line.trim() === '') {
      if (inList) { html += '</ul>'; inList = false }
    } else {
      if (inList) { html += '</ul>'; inList = false }
      html += `<p>${inline(escapeHtml(line))}</p>`
    }
  }
  if (inList) html += '</ul>'
  return html
}

function inline(s: string) {
  return s
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
}
</script>

<style lang="scss" scoped>
@use '@/styles/tokens' as *;

.preview-drawer {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: 800px;
  max-width: 90vw;
  background: $bg-canvas;
  border-left: 1px solid $border-subtle;
  z-index: 50;
  display: flex;
  flex-direction: column;
  box-shadow: -16px 0 40px rgba(0, 0, 0, 0.5);

  &__head {
    display: flex;
    align-items: flex-start;
    gap: $s-3;
    padding: $s-5 $s-6 $s-4;
    border-bottom: 1px solid $border-subtle;
  }

  &__meta {
    flex: 1;
    min-width: 0;
    .eyebrow { display: block; margin-bottom: $s-1; }
  }

  &__title {
    font-family: $font-display;
    font-size: $fs-20;
    font-weight: $fw-semibold;
    color: $text-primary;
    letter-spacing: -0.01em;
    margin-bottom: $s-2;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__info {
    display: flex;
    align-items: center;
    gap: $s-2;
    font-size: $fs-12;
    color: $text-secondary;
  }

  &__actions {
    display: flex;
    gap: $s-1;
    flex-shrink: 0;
  }

  &__body {
    flex: 1;
    overflow: hidden;
    position: relative;
    background: $bg-inset;
  }

  &__iframe {
    width: 100%;
    height: 100%;
    border: none;
    background: #1a1d23;
  }

  &__text {
    margin: 0;
    padding: $s-5 $s-6;
    overflow: auto;
    height: 100%;
    box-sizing: border-box;
    color: $text-primary;
    font-family: $font-mono;
    font-size: $fs-13;
    line-height: $lh-normal;
    white-space: pre-wrap;
    word-wrap: break-word;
  }

  &__md {
    padding: $s-5 $s-6;
    overflow: auto;
    height: 100%;
    box-sizing: border-box;
    color: $text-primary;
    line-height: $lh-normal;

    :deep(h1), :deep(h2), :deep(h3) {
      font-family: $font-display;
      font-weight: $fw-semibold;
      color: $text-primary;
      margin: $s-5 0 $s-3;
    }
    :deep(h1) { font-size: $fs-24; }
    :deep(h2) { font-size: $fs-20; }
    :deep(h3) { font-size: $fs-17; }

    :deep(p) { margin: $s-2 0; color: $text-primary; }
    :deep(ul) {
      margin: $s-2 0;
      padding-left: $s-5;
    }
    :deep(li) { margin: $s-1 0; }
    :deep(strong) { color: $accent; font-weight: $fw-semibold; }
    :deep(code) {
      background: $bg-elevated;
      padding: 1px 6px;
      border-radius: $r-sm;
      font-family: $font-mono;
      font-size: 0.9em;
      color: $accent;
    }
  }

  &__loading,
  &__unsupported {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    text-align: center;
    color: $text-secondary;
    gap: $s-3;
    p { font-size: $fs-14; }
  }

  .spinner {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    border: 2px solid $border-subtle;
    border-top-color: $accent;
    animation: spin 800ms linear infinite;
  }
}

@keyframes spin { to { transform: rotate(360deg); } }

.drawer-enter-active, .drawer-leave-active {
  transition: transform $dur-base $ease-out, opacity $dur-base $ease-out;
}
.drawer-enter-from, .drawer-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>