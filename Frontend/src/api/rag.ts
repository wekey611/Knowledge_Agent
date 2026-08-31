// ========================================
// RAG API — 知识库问答
// ========================================
// 后端：POST /knowledge-bases/{kb_id}/query
// ⚠️ MiniMax-M2.7-highspeed 默认会返回 <think>...</think> 推理块，
//    前端要剥掉再渲染，否则用户会看到 AI 的内心独白。
// ========================================
import http from './http'

export interface RagSource {
  chunk_id: string
  score: number | null
  source_file: string
  preview: string
}

export interface RagResponse {
  query: string
  answer: string
  sources: RagSource[]
}

/** 去掉 MiniMax 的 <think>...</think> 块（兼容非贪婪跨行匹配） */
function stripThink(s: string): string {
  return s.replace(/<think>[\s\S]*?<\/think>/g, '').trim()
}

/**
 * 知识库问答（POST /knowledge-bases/{kb_id}/query）
 * - top_k 不传 → 后端走默认
 * - LLM 调 MiniMax 通常 5~30s，前端 timeout 在 vite proxy 配 120000
 */
export async function askRAG(
  kbId: number,
  query: string,
  topK?: number,
): Promise<RagResponse> {
  const body: { query: string; top_k?: number } = { query }
  if (topK !== undefined) body.top_k = topK

  const { data } = await http.post<RagResponse>(
    `/knowledge-bases/${kbId}/query`,
    body,
  )

  // 剥思考块
  data.answer = stripThink(data.answer || '')
  return data
}