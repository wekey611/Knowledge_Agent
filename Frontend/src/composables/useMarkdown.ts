// ========================================
// Markdown 渲染器（用于 RAG 答案）
// ========================================
// 用 markdown-it 渲染后端返回的 markdown 答案。
// 配 highlight.js 做代码块语法高亮。
// 主题用 github-dark（适配项目深色风格），token 样式挂 scoped 不污染全局。
// ========================================
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js/lib/core'
// 注册常用语言（避免全量注册打大包）
import javascript from 'highlight.js/lib/languages/javascript'
import typescript from 'highlight.js/lib/languages/typescript'
import python from 'highlight.js/lib/languages/python'
import bash from 'highlight.js/lib/languages/bash'
import json from 'highlight.js/lib/languages/json'
import xml from 'highlight.js/lib/languages/xml'
import css from 'highlight.js/lib/languages/css'
import sql from 'highlight.js/lib/languages/sql'

hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('js', javascript)
hljs.registerLanguage('typescript', typescript)
hljs.registerLanguage('ts', typescript)
hljs.registerLanguage('python', python)
hljs.registerLanguage('py', python)
hljs.registerLanguage('bash', bash)
hljs.registerLanguage('sh', bash)
hljs.registerLanguage('json', json)
hljs.registerLanguage('html', xml)
hljs.registerLanguage('xml', xml)
hljs.registerLanguage('css', css)
hljs.registerLanguage('sql', sql)

const md = new MarkdownIt({
  html: false,    // 安全：禁止原始 HTML
  linkify: true,  // URL 自动转链接
  breaks: true,   // \n 变 <br>
  highlight(code: string, lang: string): string {
    if (lang && hljs.getLanguage(lang)) {
      try {
        const out = hljs.highlight(code, { language: lang, ignoreIllegals: true }).value
        return `<pre class="hljs"><code class="hljs language-${lang}">${out}</code></pre>`
      } catch {
        /* fallback */
      }
    }
    // 无 lang 或不支持：原样输出（保留换行）
    const escaped = md.utils.escapeHtml(code)
    return `<pre class="hljs"><code class="hljs">${escaped}</code></pre>`
  },
})

/** 渲染 markdown 为 HTML 字符串（用于 v-html） */
export function renderMarkdown(text: string): string {
  if (!text) return ''
  return md.render(text)
}