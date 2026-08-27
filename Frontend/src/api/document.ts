// ========================================
// Document API — 真实后端接口
// ========================================
import http from './http'
import type { DocumentDetail, DocumentList, DocumentSimple } from '@/types/knowledge'

function isDemo() {
  return (localStorage.getItem('access_token') || '').startsWith('demo.')
}

function mockDocs(): DocumentList {
  const raw = localStorage.getItem('demo_docs')
  if (!raw) return { total: 0, data: [] }
  return { total: 0, data: JSON.parse(raw) as any }
}

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
  if (isDemo()) return mockDocs()
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
  if (isDemo()) {
    // Demo 模式：从 localStorage 找文档信息，生成对应类型的占位内容
    const list = mockDocs().data
    const doc = list.find((d) => d.id === documentId)
    const ext = doc?.filename.split('.').pop()?.toLowerCase() || 'txt'
    // Demo 模式把 PDF 也当文本处理（因为生成的占位 PDF 不是合法的 PDF 格式）
    if (ext === 'md' || ext === 'markdown') {
      const mime = 'text/markdown'
      const content = `# ${doc?.title || '文档'}\n\n## 一级标题\n\n这是一段普通文字，包含 **粗体**、*斜体* 和 \`代码\` 标记。\n\n## 二级标题\n\n- 列表项 1\n- 列表项 2\n- 列表项 3\n\n### 三级标题\n\n> 引用：这是一段引用文字。\n\n> 文档元数据：${doc?.filename || ''} · ${doc?.file_size || 0} 字节 · 更新于 ${doc?.updated_at || ''}\n`
      const blob = new Blob([content], { type: mime })
      return URL.createObjectURL(blob)
    }
    // txt / pdf 都用文本类型，方便 iframe / pre 渲染
    const mime = 'text/plain'
    const content = `这是「${doc?.title || '文档'}」的预览内容（演示）。\n\n实际的预览文件将在后端接入后提供。\n\n文件名：${doc?.filename || ''}\n大小：${doc?.file_size || 0} 字节\n更新于：${doc?.updated_at || ''}\n\nPDF 文件将以 iframe 嵌入方式预览，TXT 文件以纯文本显示，MD 文件以渲染后的 markdown 显示。`
    const blob = new Blob([content], { type: mime })
    return URL.createObjectURL(blob)
  }
  const res = await http.get<Blob>(`/knowledge-bases/${kbId}/documents/${documentId}/preview`, {
    responseType: 'blob',
  })
  return URL.createObjectURL(res.data)
}
