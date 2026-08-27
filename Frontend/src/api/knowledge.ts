// ========================================
// Knowledge Base API — 真实后端接口
// ========================================
import http from './http'
import type {
  KnowledgeBase,
  KnowledgeBaseCreate,
  KnowledgeBaseList,
  KnowledgeBaseUpdate,
} from '@/types/knowledge'

/** Demo 模式：从 localStorage 注入 mock 数据 */
function isDemo() {
  return (localStorage.getItem('access_token') || '').startsWith('demo.')
}

function mockKbList(): KnowledgeBaseList {
  const raw = localStorage.getItem('demo_kbs')
  if (!raw) return { total: 0, data: [] }
  return { total: 0, data: JSON.parse(raw) as any }
}

function mockKb(id: number): KnowledgeBase {
  const list = mockKbList().data
  const k = list.find((x) => x.id === id)
  return {
    ...(k as any),
    chunk_size: 500,
    chunk_overlap: 50,
    chunk_count: (k?.document_count ?? 0) * 47,
    owner_id: 1,
    org_id: null,
    organization: null,
    updated_at: k?.created_at ?? new Date().toISOString(),
  } as KnowledgeBase
}

/** 知识库列表（GET /knowledge-bases） */
export async function fetchKnowledgeBases(): Promise<KnowledgeBaseList> {
  if (isDemo()) return mockKbList()
  const res = await http.get<KnowledgeBaseList>('/knowledge-bases')
  return res.data
}

/** 知识库详情（GET /knowledge-bases/{id}） */
export async function fetchKnowledgeBase(id: number): Promise<KnowledgeBase> {
  if (isDemo()) return mockKb(id)
  const res = await http.get<KnowledgeBase>(`/knowledge-bases/${id}`)
  return res.data
}

/** 创建知识库（POST /knowledge-bases） */
export async function createKnowledgeBase(data: KnowledgeBaseCreate): Promise<KnowledgeBase> {
  const res = await http.post<KnowledgeBase>('/knowledge-bases', data)
  return res.data
}

/** 更新知识库（PATCH /knowledge-bases/{id}） */
export async function updateKnowledgeBase(
  id: number,
  data: KnowledgeBaseUpdate
): Promise<KnowledgeBase> {
  const res = await http.patch<KnowledgeBase>(`/knowledge-bases/${id}`, data)
  return res.data
}

/** 删除知识库（DELETE /knowledge-bases/{id}） */
export async function deleteKnowledgeBase(id: number): Promise<{ message: string }> {
  const res = await http.delete<{ message: string }>(`/knowledge-bases/${id}`)
  return res.data
}
