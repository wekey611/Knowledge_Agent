// ========================================
// Document API — 真实后端接口
// ========================================
import http from './http'
import type { DocumentDetail, DocumentList, DocumentSimple } from '@/types/knowledge'

/** 上传文档（POST /knowledge-bases/{kb_id}/documents，multipart） */
export async function uploadDocument(kbId: number, file: File): Promise<DocumentSimple> {
  const formData = new FormData()
  formData.append('file', file)
  const res = await http.post<DocumentSimple>(`/knowledge-bases/${kbId}/documents`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

/** 文档列表（GET /knowledge-bases/{kb_id}/documents） */
export async function fetchDocuments(kbId: number): Promise<DocumentList> {
  const res = await http.get<DocumentList>(`/knowledge-bases/${kbId}/documents`)
  return res.data
}

/** 文档详情（GET /knowledge-bases/{kb_id}/documents/{document_id}） */
export async function fetchDocument(kbId: number, documentId: number): Promise<DocumentDetail> {
  const res = await http.get<DocumentDetail>(`/knowledge-bases/${kbId}/documents/${documentId}`)
  return res.data
}

/** 删除文档（DELETE /knowledge-bases/{kb_id}/documents/{document_id} → 204） */
export async function deleteDocument(kbId: number, documentId: number): Promise<void> {
  await http.delete(`/knowledge-bases/${kbId}/documents/${documentId}`)
}

/** 下载文档（GET .../download → blob），触发浏览器保存 */
export async function downloadDocument(kbId: number, documentId: number, filename: string): Promise<void> {
  const res = await http.get<Blob>(`/knowledge-bases/${kbId}/documents/${documentId}/download`, {
    responseType: 'blob',
  })
  // 从 Content-Disposition 提取服务端文件名（兜底用传入 filename）
  let name = filename
  const disposition = res.headers['content-disposition'] as string | undefined
  if (disposition) {
    const match = disposition.match(/filename\*?=(?:UTF-8'')?"?([^";]+)"?/i)
    if (match) name = decodeURIComponent(match[1])
  }
  const url = URL.createObjectURL(res.data)
  const a = document.createElement('a')
  a.href = url
  a.download = name
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

/** 支持的预览类型（与后端 PREVIEW_TYPES 保持一致） */
export const PREVIEW_EXTENSIONS = ['pdf', 'txt', 'md', 'markdown']

export function isPreviewable(filename: string): boolean {
  const ext = filename.split('.').pop()?.toLowerCase() || ''
  return PREVIEW_EXTENSIONS.includes(ext)
}

/** 文档预览（GET .../preview → blob），返回 objectURL */
export async function previewDocument(kbId: number, documentId: number): Promise<string> {
  const res = await http.get<Blob>(`/knowledge-bases/${kbId}/documents/${documentId}/preview`, {
    responseType: 'blob',
  })
  return URL.createObjectURL(res.data)
}
