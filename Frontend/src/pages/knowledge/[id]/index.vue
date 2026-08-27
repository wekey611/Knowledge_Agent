<template>
  <div class="chat-page">
    <!-- Side drawer (document list, toggled) -->
    <transition name="drawer">
      <aside v-if="drawerOpen" class="drawer">
        <div class="drawer__head">
          <h3 class="drawer__title">本知识库文档</h3>
          <button class="btn btn--icon btn--ghost btn--sm" @click="drawerOpen = false">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M6 6l12 12M6 18L18 6" stroke-linecap="round"/></svg>
          </button>
        </div>
        <div class="drawer__search">
          <input v-model="docQuery" class="input" placeholder="搜索文档" />
        </div>
        <ul class="drawer__list">
          <li
            v-for="doc in filteredDocs"
            :key="doc.id"
            class="drawer__item"
            @click="citeDocument(doc)"
          >
            <div class="drawer__item-icon">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/></svg>
            </div>
            <div class="drawer__item-body">
              <span class="drawer__item-name">{{ doc.title }}</span>
              <span class="drawer__item-meta mono">
                <span class="doc-mini-dot" :class="`doc-mini-dot--${doc.parser_status}`"></span>
                {{ PARSER_STATUS_LABELS[doc.parser_status] }}
                · {{ doc.chunk_count }} 块
              </span>
            </div>
          </li>
          <li v-if="filteredDocs.length === 0" class="drawer__empty">
            <p class="muted">没有匹配的文档</p>
          </li>
        </ul>
      </aside>
    </transition>

    <!-- Main chat area -->
    <div class="chat-main">
      <div class="chat-toolbar">
        <button class="btn btn--ghost btn--sm" @click="drawerOpen = !drawerOpen">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>
          {{ drawerOpen ? '隐藏' : '显示' }}文档
        </button>
        <div class="chat-toolbar__sep" />
        <button
          v-for="tpl in templates"
          :key="tpl.label"
          class="chip chip--ghost"
          @click="applyTemplate(tpl)"
        >{{ tpl.label }}</button>
        <button class="btn btn--ghost btn--sm" style="margin-left: auto" @click="clearChat">清空对话</button>
      </div>

      <div ref="scrollRef" class="chat-scroll">
        <!-- Empty state -->
        <div v-if="messages.length === 0" class="chat-empty">
          <div class="chat-empty__brand">
            <svg viewBox="0 0 48 48" width="48" height="48" fill="none">
              <rect x="2" y="2" width="44" height="44" rx="10" fill="#16181F" stroke="rgba(255,255,255,0.08)"/>
              <path d="M14 12h11a8 8 0 0 1 8 8v8a8 8 0 0 1-8 8H14z" stroke="#A8E6CF" stroke-width="2"/>
              <path d="M20 20h3M20 26h10M20 32h6" stroke="#A8E6CF" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <h2 class="chat-empty__title">向你的知识库提问</h2>
          <p class="chat-empty__sub">
            基于已上传的文档回答问题，并标注引用来源。RAG 检索 + Agent 接入中，先体验界面。
          </p>
          <div class="chat-empty__suggest">
            <button
              v-for="s in suggestions"
              :key="s"
              class="suggestion"
              @click="input = s"
            >{{ s }}</button>
          </div>
        </div>

        <!-- Messages -->
        <div v-else class="messages">
          <article
            v-for="m in messages"
            :key="m.id"
            class="msg"
            :class="`msg--${m.role}`"
          >
            <div class="msg__avatar" v-if="m.role === 'assistant'">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 12a8 8 0 0 1-11.6 7.2L4 21l1.8-5.4A8 8 0 1 1 21 12z"/></svg>
            </div>

            <div class="msg__body">
              <div class="msg__meta">
                <span class="msg__role">{{ m.role === 'user' ? '你' : 'Agent' }}</span>
                <span class="msg__time mono faint">{{ m.time }}</span>
              </div>
              <div class="msg__bubble" :class="{ 'msg__bubble--streaming': m.streaming }">
                <p
                  v-for="(para, i) in m.paragraphs"
                  :key="i"
                  class="msg__para"
                >{{ para }}</p>

                <!-- Sources -->
                <div v-if="m.sources && m.sources.length" class="msg__sources">
                  <span class="eyebrow">来源</span>
                  <div class="msg__sources-list">
                    <button
                      v-for="(s, i) in m.sources"
                      :key="i"
                      class="source-chip"
                      @click="openSource(s)"
                    >
                      <span class="source-chip__num mono">[{{ i + 1 }}]</span>
                      <span class="source-chip__title">{{ s.documentTitle }}</span>
                      <span class="source-chip__score mono">{{ Math.round(s.score * 100) }}%</span>
                    </button>
                  </div>
                </div>

                <!-- Streaming cursor -->
                <span v-if="m.streaming" class="cursor" />
              </div>
            </div>

            <div class="msg__avatar msg__avatar--user" v-if="m.role === 'user'">
              <span>{{ userInitial }}</span>
            </div>
          </article>
        </div>
      </div>

      <!-- Source preview drawer (inline, bottom of input) -->
      <transition name="slide-up">
        <div v-if="previewSource" class="source-preview">
          <div class="source-preview__head">
            <span class="eyebrow">引用片段</span>
            <strong>{{ previewSource.documentTitle }}</strong>
            <span class="mono faint">相关度 {{ Math.round(previewSource.score * 100) }}%</span>
            <button class="btn btn--icon btn--ghost btn--sm" style="margin-left: auto" @click="previewSource = null">
              <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M6 6l12 12M6 18L18 6" stroke-linecap="round"/></svg>
            </button>
          </div>
          <blockquote class="source-preview__body">"{{ previewSource.snippet }}"</blockquote>
        </div>
      </transition>

      <!-- Input -->
      <form class="chat-input" @submit.prevent="send">
        <textarea
          ref="inputRef"
          v-model="input"
          class="chat-input__field"
          rows="1"
          placeholder="问点什么…  (Shift+Enter 换行，Enter 发送)"
          @keydown.enter.exact.prevent="send"
          @input="autoResize"
        />
        <button class="chat-input__send" :disabled="!canSend" type="submit">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 19V5M5 12l7-7 7 7" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { fetchDocuments } from '@/api/document'
import { useAuthStore } from '@/stores/auth'
import type { DocumentSimple, SourceReference } from '@/types/knowledge'
import { PARSER_STATUS_LABELS } from '@/types/knowledge'

const route = useRoute()
const auth = useAuthStore()
const kbId = computed(() => Number(route.params.id))

const docs = ref<DocumentSimple[]>([])
const docQuery = ref('')
const drawerOpen = ref(true)

const input = ref('')
const inputRef = ref<HTMLTextAreaElement | null>(null)
const scrollRef = ref<HTMLDivElement | null>(null)

interface Msg {
  id: string
  role: 'user' | 'assistant'
  paragraphs: string[]
  sources?: SourceReference[]
  time: string
  streaming?: boolean
}

const messages = ref<Msg[]>([])
const previewSource = ref<SourceReference | null>(null)

const userInitial = computed(() => auth.user?.email?.[0]?.toUpperCase() || '·')

const filteredDocs = computed(() => {
  const q = docQuery.value.toLowerCase()
  if (!q) return docs.value
  return docs.value.filter((d) => d.title.toLowerCase().includes(q))
})

const suggestions = [
  '总结这份文档的主要观点',
  '提取所有涉及金额的条款',
  '对比第一段和最后一段的差异',
  '用三句话解释核心概念',
]

const templates = [
  { label: '总结文档', prompt: '总结这份知识库所有文档的核心要点' },
  { label: '提取关键词', prompt: '提取本知识库最近文档的高频关键词' },
  { label: '生成问答', prompt: '基于已有文档生成 5 个常见问题与答案' },
]

const canSend = computed(() => input.value.trim().length > 0)

onMounted(async () => {
  try {
    const res = await fetchDocuments(kbId.value)
    docs.value = res.data
  } catch {
    /* noop */
  }
  // seed mock conversation
  if (messages.value.length === 0 && docs.value.length > 0) {
    seedDemo()
  }
})

function seedDemo() {
  const t = (offset: number) => {
    const d = new Date(Date.now() - offset)
    return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  messages.value.push({
    id: 'm1',
    role: 'user',
    paragraphs: ['这份知识库里有哪些产品相关的内容？'],
    time: t(60_000),
  })
  messages.value.push({
    id: 'm2',
    role: 'assistant',
    paragraphs: [
      `基于当前 ${docs.value.length} 份文档的检索结果，我整理出三类主要内容：`,
      '产品手册中描述了核心功能的实现细节；会议纪要里记录了最近两次需求评审的结论；调研报告汇总了用户访谈中的高频反馈。',
      '需要我针对哪一类展开深入分析？',
    ],
    sources: docs.value.slice(0, 2).map((d, i) => ({
      documentId: d.id,
      documentTitle: d.title,
      snippet: '相关片段将在这里展示，包含最相关的句子片段和上下文…',
      score: 0.92 - i * 0.07,
    })),
    time: t(50_000),
  })
}

function send() {
  if (!canSend.value) return
  const text = input.value.trim()
  const userMsg: Msg = {
    id: String(Date.now()),
    role: 'user',
    paragraphs: [text],
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
  }
  messages.value.push(userMsg)
  input.value = ''
  autoResize()
  scrollToBottom()
  mockReply(text)
}

function mockReply(question: string) {
  const id = String(Date.now()) + '-a'
  const placeholder: Msg = {
    id,
    role: 'assistant',
    paragraphs: [''],
    sources: docs.value.slice(0, Math.min(3, docs.value.length)).map((d, i) => ({
      documentId: d.id,
      documentTitle: d.title,
      snippet: '相关片段将在这里展示，包含最相关的句子片段和上下文…',
      score: 0.88 - i * 0.08,
    })),
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
    streaming: true,
  }
  messages.value.push(placeholder)
  scrollToBottom()

  // 模拟打字机效果
  const fullText = `根据检索到 ${placeholder.sources!.length} 份相关文档，关于「${question}」我整理如下：\n\n这些文档从不同角度覆盖了你的问题。核心观点集中在第一段，第二段提供了具体的实现细节。建议先阅读引用度最高的文档，再展开。\n\n如需深入某个文档的具体章节，可以告诉我。`
  let i = 0
  const interval = setInterval(() => {
    i += 2
    const cur = fullText.slice(0, i)
    placeholder.paragraphs = cur.split('\n')
    if (i >= fullText.length) {
      clearInterval(interval)
      placeholder.streaming = false
    }
    scrollToBottom()
  }, 30)
}

function applyTemplate(t: { prompt: string }) {
  input.value = t.prompt
  nextTick(autoResize)
}

function clearChat() {
  messages.value = []
  previewSource.value = null
}

function citeDocument(doc: DocumentSimple) {
  input.value = input.value
    ? `${input.value}\n（参考：${doc.title}）`
    : `请基于「${doc.title}」回答：`
  nextTick(autoResize)
}

function openSource(s: SourceReference) {
  previewSource.value = s
}

function autoResize() {
  const el = inputRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 200) + 'px'
}

function scrollToBottom() {
  nextTick(() => {
    if (scrollRef.value) scrollRef.value.scrollTop = scrollRef.value.scrollHeight
  })
}
</script>

<style lang="scss" scoped>
@use '@/styles/tokens' as *;

.chat-page {
  display: flex;
  gap: $s-5;
  height: calc(100vh - #{$topbar-h} - 200px);
  min-height: 540px;
}

.drawer {
  width: 260px;
  flex-shrink: 0;
  background: $bg-surface;
  border: 1px solid $border-subtle;
  border-radius: $r-lg;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  &__head {
    padding: $s-4;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid $border-subtle;
  }
  &__title {
    font-family: $font-body;
    font-weight: $fw-semibold;
    font-size: $fs-14;
  }
  &__search {
    padding: $s-3 $s-4;
    border-bottom: 1px solid $border-subtle;
  }
  &__list {
    list-style: none;
    margin: 0;
    padding: $s-2;
    flex: 1;
    overflow-y: auto;
  }
  &__item {
    display: flex;
    gap: $s-2;
    padding: $s-3;
    border-radius: $r-md;
    cursor: pointer;
    transition: background $dur-base $ease-out;

    &:hover { background: $bg-elevated; }
  }
  &__item-icon {
    width: 28px; height: 28px;
    flex-shrink: 0;
    background: $bg-elevated;
    border-radius: $r-sm;
    display: flex;
    align-items: center;
    justify-content: center;
    color: $text-secondary;
  }
  &__item-body {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  &__item-name {
    font-size: $fs-13;
    color: $text-primary;
    font-weight: $fw-medium;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  &__item-meta {
    font-size: $fs-12;
    color: $text-tertiary;
    display: inline-flex;
    align-items: center;
    gap: $s-1;
  }
  &__empty {
    padding: $s-6;
    text-align: center;
  }
}

.doc-mini-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;

  &--completed { background: $success; }
  &--failed { background: $danger; }
  &--parsing, &--embedding { background: $info; animation: pulse 1.6s $ease-out infinite; }
  &--waiting { background: $text-tertiary; }
}

.drawer-enter-active, .drawer-leave-active {
  transition: opacity $dur-base $ease-out, transform $dur-base $ease-out;
}
.drawer-enter-from, .drawer-leave-to {
  opacity: 0;
  transform: translateX(-12px);
}

.chat-main {
  flex: 1;
  min-width: 0;
  background: $bg-surface;
  border: 1px solid $border-subtle;
  border-radius: $r-lg;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-toolbar {
  display: flex;
  align-items: center;
  gap: $s-2;
  padding: $s-3 $s-4;
  border-bottom: 1px solid $border-subtle;

  &__sep {
    width: 1px;
    height: 20px;
    background: $border-subtle;
    margin: 0 $s-1;
  }
}

.chip--ghost {
  font-size: $fs-12;
  padding: 4px $s-2;
  height: auto;
  color: $text-secondary;
  background: transparent;
  border: 1px solid $border-subtle;
  border-radius: $r-sm;

  &:hover { color: $accent; border-color: $accent; }
}

.chat-scroll {
  flex: 1;
  overflow-y: auto;
  padding: $s-6 $s-6 0;
}

.chat-empty {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: $s-10 $s-6;

  &__brand {
    margin-bottom: $s-5;
    color: $accent;
  }
  &__title {
    font-family: $font-display;
    font-size: $fs-32;
    font-weight: $fw-semibold;
    letter-spacing: -0.015em;
  }
  &__sub {
    margin-top: $s-3;
    color: $text-secondary;
    font-size: $fs-15;
    max-width: 460px;
    line-height: $lh-snug;
  }
  &__suggest {
    display: flex;
    flex-wrap: wrap;
    gap: $s-2;
    margin-top: $s-6;
    justify-content: center;
  }
}

.suggestion {
  padding: $s-2 $s-4;
  border-radius: $r-md;
  background: $bg-elevated;
  border: 1px solid $border-subtle;
  color: $text-secondary;
  font-size: $fs-13;
  cursor: pointer;
  transition: all $dur-base $ease-out;

  &:hover {
    background: $bg-surface;
    color: $accent;
    border-color: $accent;
  }
}

.messages {
  display: flex;
  flex-direction: column;
  gap: $s-6;
  padding-bottom: $s-6;
}

.msg {
  display: flex;
  gap: $s-3;
  max-width: 760px;
  margin: 0 auto;

  &--user {
    flex-direction: row-reverse;
    .msg__body { align-items: flex-end; }
    .msg__meta { flex-direction: row-reverse; }
    .msg__bubble {
      background: $accent-soft;
      border-color: rgba(168, 230, 207, 0.3);
    }
  }

  &__avatar {
    width: 32px; height: 32px;
    flex-shrink: 0;
    border-radius: 50%;
    background: $bg-elevated;
    display: flex;
    align-items: center;
    justify-content: center;
    color: $accent;
    border: 1px solid $border-subtle;

    &--user {
      background: $accent;
      color: $text-inverse;
      font-family: $font-display;
      font-size: $fs-14;
      font-weight: $fw-semibold;
      border-color: $accent;
    }
  }

  &__body {
    display: flex;
    flex-direction: column;
    gap: $s-2;
    max-width: calc(100% - 48px);
  }

  &__meta {
    display: flex;
    align-items: baseline;
    gap: $s-2;
    font-size: $fs-12;
  }
  &__role {
    color: $text-secondary;
    font-weight: $fw-medium;
  }

  &__bubble {
    background: $bg-elevated;
    border: 1px solid $border-subtle;
    border-radius: $r-lg;
    padding: $s-4 $s-5;
    line-height: $lh-normal;
    color: $text-primary;
    font-size: $fs-14;
    position: relative;

    &--streaming {
      min-height: 48px;
    }
  }

  &__para {
    margin: 0 0 $s-2 0;
    &:last-child { margin-bottom: 0; }
  }

  &__sources {
    margin-top: $s-4;
    padding-top: $s-3;
    border-top: 1px solid $border-subtle;
    display: flex;
    flex-direction: column;
    gap: $s-2;
  }
  &__sources-list {
    display: flex;
    flex-wrap: wrap;
    gap: $s-2;
  }
}

.source-chip {
  display: inline-flex;
  align-items: center;
  gap: $s-2;
  padding: 4px $s-2;
  border-radius: $r-sm;
  background: $bg-inset;
  border: 1px solid $border-subtle;
  color: $text-secondary;
  font-size: $fs-12;
  cursor: pointer;
  transition: all $dur-base $ease-out;

  &:hover {
    color: $accent;
    border-color: $accent;
  }

  &__num { color: $accent; font-weight: $fw-semibold; }
  &__title { color: $text-primary; }
  &__score { color: $text-tertiary; font-size: $fs-12; }
}

.cursor {
  display: inline-block;
  width: 8px;
  height: 14px;
  background: $accent;
  margin-left: 2px;
  vertical-align: -2px;
  animation: blink 1s steps(2) infinite;
}
@keyframes blink { 50% { opacity: 0; } }

.source-preview {
  margin: 0 $s-6 $s-3;
  background: $bg-inset;
  border: 1px solid $accent;
  border-left-width: 3px;
  border-radius: $r-md;
  padding: $s-3 $s-4;

  &__head {
    display: flex;
    align-items: baseline;
    gap: $s-2;
    font-size: $fs-12;
    margin-bottom: $s-2;

    strong { color: $text-primary; font-weight: $fw-semibold; font-size: $fs-13; }
  }
  &__body {
    margin: 0;
    font-size: $fs-13;
    color: $text-secondary;
    line-height: $lh-snug;
    font-style: italic;
  }
}

.slide-up-enter-active, .slide-up-leave-active {
  transition: all $dur-base $ease-out;
}
.slide-up-enter-from, .slide-up-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

.chat-input {
  margin: $s-3 $s-6 $s-6;
  display: flex;
  align-items: flex-end;
  gap: $s-2;
  padding: $s-3;
  background: $bg-elevated;
  border: 1px solid $border-subtle;
  border-radius: $r-lg;
  transition: border-color $dur-base $ease-out;

  &:focus-within { border-color: $accent; }

  &__field {
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: $text-primary;
    font-size: $fs-14;
    line-height: $lh-normal;
    resize: none;
    max-height: 200px;
    min-height: 24px;
    font-family: inherit;
    padding: 6px 8px;
    &::placeholder { color: $text-tertiary; }
  }
  &__send {
    width: 36px;
    height: 36px;
    flex-shrink: 0;
    border-radius: $r-md;
    background: $accent;
    color: $text-inverse;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all $dur-base $ease-out;

    &:hover:not(:disabled) {
      background: $accent-hover;
      transform: scale(1.05);
    }
    &:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }
  }
}

@media (max-width: 900px) {
  .chat-page { height: auto; }
  .drawer { display: none; }
}
</style>