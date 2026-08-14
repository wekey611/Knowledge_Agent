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

/** 知识库列表（GET /knowledge-bases） */
export async function fetchKnowledgeBases(): Promise<KnowledgeBaseList> {
  const res = await http.get<KnowledgeBaseList>('/knowledge-bases')
  return res.data
}

/** 知识库详情（GET /knowledge-bases/{id}） */
export async function fetchKnowledgeBase(id: number): Promise<KnowledgeBase> {
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
