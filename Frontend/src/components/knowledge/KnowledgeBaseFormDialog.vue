<template>
  <transition name="fade">
    <div v-if="modelValue" class="modal-backdrop" @click.self="$emit('update:modelValue', false)">
      <div class="modal">
        <header class="modal__head">
          <div>
            <span class="eyebrow">新建</span>
            <h2 class="modal__title">创建知识库</h2>
          </div>
          <button class="btn btn--icon btn--ghost btn--sm" @click="$emit('update:modelValue', false)">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M6 6l12 12M6 18L18 6" stroke-linecap="round"/></svg>
          </button>
        </header>

        <form @submit.prevent="handleSubmit" class="modal__body">
          <div class="field">
            <label class="field__label">名称</label>
            <input
              ref="firstField"
              v-model="form.name"
              class="input"
              placeholder="例如：产品手册 2025"
              maxlength="100"
              required
            />
            <span class="field__counter mono faint">{{ form.name.length }}/100</span>
          </div>

          <div class="field">
            <label class="field__label">描述</label>
            <textarea
              v-model="form.description"
              class="textarea"
              placeholder="简单说明用途（可选）"
              rows="2"
            />
          </div>

          <div class="field">
            <label class="field__label">可见范围</label>
            <div class="radio-row">
              <label
                v-for="opt in scopeOptions"
                :key="opt.value"
                class="radio-card"
                :class="{ 'radio-card--active': form.scope === opt.value }"
              >
                <input type="radio" v-model="form.scope" :value="opt.value" :disabled="opt.disabled" />
                <div class="radio-card__body">
                  <span class="radio-card__title">{{ opt.label }}</span>
                  <span class="radio-card__hint">{{ opt.hint }}</span>
                </div>
              </label>
            </div>
          </div>

          <div v-if="form.scope === 'org'" class="field">
            <label class="field__label">所属组织</label>
            <select v-model="form.org_id" class="input" required>
              <option :value="null" disabled>选择组织</option>
              <option v-for="org in organizations" :key="org.id" :value="org.id">{{ org.name }}</option>
            </select>
            <p v-if="organizations.length === 0" class="field__hint">尚未加入任何组织，请先创建或加入组织</p>
          </div>

          <div class="field-row">
            <div class="field">
              <label class="field__label">分块大小</label>
              <input v-model.number="form.chunk_size" type="number" class="input" min="100" step="100" />
              <span class="field__hint">默认 500</span>
            </div>
            <div class="field">
              <label class="field__label">分块重叠</label>
              <input v-model.number="form.chunk_overlap" type="number" class="input" min="0" step="10" />
              <span class="field__hint">默认 50</span>
            </div>
          </div>

          <div v-if="error" class="form-error">{{ error }}</div>

          <footer class="modal__foot">
            <button type="button" class="btn btn--ghost" @click="$emit('update:modelValue', false)">取消</button>
            <button type="submit" class="btn btn--primary" :disabled="loading">
              {{ loading ? '创建中…' : '创建' }}
            </button>
          </footer>
        </form>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { createKnowledgeBase } from '@/api/knowledge'
import { fetchOrganizations } from '@/api/organization'
import { useAuthStore } from '@/stores/auth'

defineProps<{ modelValue: boolean }>()
const emit = defineEmits<{ 'update:modelValue': [v: boolean] }>()

const router = useRouter()
const auth = useAuthStore()
const firstField = ref<HTMLInputElement | null>(null)
const organizations = ref<{ id: number; name: string }[]>([])
const loading = ref(false)
const error = ref('')

const form = reactive({
  name: '',
  description: '',
  scope: 'personal' as 'personal' | 'org' | 'public',
  org_id: null as number | null,
  chunk_size: 500,
  chunk_overlap: 50,
})

const scopeOptions = computed(() => [
  { value: 'personal', label: '个人', hint: '仅自己可见', disabled: false },
  { value: 'org', label: '组织', hint: '组织内成员可见', disabled: organizations.value.length === 0 },
  { value: 'public', label: '公开', hint: '所有用户可见', disabled: !auth.isAdmin },
])

onMounted(async () => {
  try {
    const orgs = await fetchOrganizations()
    organizations.value = orgs
  } catch {
    /* ignore */
  }
  setTimeout(() => firstField.value?.focus(), 100)
})

async function handleSubmit() {
  if (!form.name.trim()) {
    error.value = '请输入名称'
    return
  }
  if (form.scope === 'org' && !form.org_id) {
    error.value = '请选择组织'
    return
  }
  error.value = ''
  loading.value = true
  try {
    const kb = await createKnowledgeBase({
      name: form.name.trim(),
      description: form.description.trim() || null,
      scope: form.scope,
      org_id: form.scope === 'org' ? form.org_id : null,
      chunk_size: form.chunk_size,
      chunk_overlap: form.chunk_overlap,
    })
    emit('update:modelValue', false)
    router.push(`/knowledge/${kb.id}`)
  } catch (e: any) {
    error.value = e?.response?.data?.detail || '创建失败'
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/tokens' as *;

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: $s-6;
}

.modal {
  width: 100%;
  max-width: 540px;
  background: $bg-surface;
  border: 1px solid $border-strong;
  border-radius: $r-lg;
  box-shadow: $shadow-lg;
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  overflow: hidden;

  &__head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    padding: $s-5 $s-6 $s-4;
    border-bottom: 1px solid $border-subtle;
  }
  &__title {
    margin-top: $s-2;
    font-family: $font-display;
    font-size: $fs-24;
    font-weight: $fw-semibold;
    letter-spacing: -0.01em;
  }

  &__body {
    padding: $s-5 $s-6;
    display: flex;
    flex-direction: column;
    gap: $s-4;
    overflow-y: auto;
  }

  &__foot {
    display: flex;
    justify-content: flex-end;
    gap: $s-2;
    padding-top: $s-3;
    border-top: 1px solid $border-subtle;
    margin-top: $s-2;
  }
}

.field {
  display: flex;
  flex-direction: column;
  gap: $s-2;
  position: relative;

  &__label {
    font-size: $fs-13;
    font-weight: $fw-medium;
    color: $text-secondary;
  }
  &__hint {
    font-size: $fs-12;
    color: $text-tertiary;
  }
  &__counter {
    position: absolute;
    right: $s-2;
    bottom: $s-1;
    font-size: $fs-12;
  }
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: $s-4;
}

.radio-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: $s-2;
}

.radio-card {
  position: relative;
  padding: $s-3;
  background: $bg-inset;
  border: 1px solid $border-subtle;
  border-radius: $r-md;
  cursor: pointer;
  transition: all $dur-base $ease-out;

  input { position: absolute; opacity: 0; pointer-events: none; }

  &:hover { border-color: $border-strong; }
  &--active {
    border-color: $accent;
    background: $accent-soft;
  }

  &__title {
    display: block;
    font-size: $fs-14;
    font-weight: $fw-medium;
    color: $text-primary;
  }
  &__hint {
    display: block;
    font-size: $fs-12;
    color: $text-tertiary;
    margin-top: 2px;
  }
}

.form-error {
  padding: $s-3 $s-4;
  background: $danger-soft;
  color: $danger;
  border-radius: $r-md;
  font-size: $fs-13;
}

.fade-enter-active, .fade-leave-active { transition: opacity $dur-base $ease-out; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>