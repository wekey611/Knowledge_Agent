"""
RAG 业务服务：封装权限检查 + Pipeline 调用。
"""
import re
from typing import Optional

from sqlalchemy import select
from app import core, models
from rag.config import load_config
from rag.factory import build_pipeline
from rag.pipeline import RAGResponse


# chunk_id 两种格式都见过：
# - single collection: f"kb_{kb_id}_doc_{doc_id}_chunk_{chunk_index}"（V2 chroma）
# - multi collection:  f"{doc_id}_{chunk_index}"（kb_id 已在 collection 名里）
# 用两个正则分别解析，都拿不到就放弃
_CHUNK_ID_RE_KB_DOC = re.compile(r"^kb_\d+_doc_(\d+)_chunk_\d+$")
_CHUNK_ID_RE_DOC = re.compile(r"^(\d+)_(\d+)$")


def _extract_doc_id(chunk_id: str) -> int | None:
    """从 chunk_id 解析 doc_id，两种格式都支持；失败返回 None"""
    if not chunk_id:
        return None
    m = _CHUNK_ID_RE_KB_DOC.match(chunk_id)
    if m:
        return int(m.group(1))
    m = _CHUNK_ID_RE_DOC.match(chunk_id)
    if m:
        return int(m.group(1))
    return None


class RAGService:
    """
    RAG 业务编排。

    Attributes:
        db: 数据库 session
    """

    def __init__(self, db):
        self.db = db

    async def query(
        self,
        kb_id: int,
        user_query: str,
        current_user,
        top_k: Optional[int] = None,
    ) -> RAGResponse:
        """
        知识库问答。

        Args:
            kb_id: 知识库 ID
            user_query: 用户问题
            current_user: 当前登录用户
            top_k: 检索数量（None 用默认）

        Returns:
            RAGResponse 含答案 + 引用来源
        """
        # 1. 权限检查
        await core.permissions.check_knowledge_base_access(
            kb_id=kb_id, current_user=current_user, db=self.db
        )

        # 2. 构造 Pipeline 并查询
        config = load_config()
        pipeline = build_pipeline(config)

        response = await pipeline.query(
            query=user_query,
            kb_id=kb_id,
            top_k=top_k,
        )

        # 3. 覆盖 source_file：rag 模块返回的是 storage 的 hash 文件名，
        #    前端展示需要原始文件名。这里按 chunk_id 解析 doc_id，批量查一次 db。
        await self._enrich_source_filenames(response)

        # 4. 低分 sources 过滤：用户问"你好"这类寒暄时，LLM 会硬塞一堆不相关 sources，
        #    体验很差。这里把所有 score < 阈值的 sources 丢掉。
        response.sources = [s for s in response.sources if (s.get("score") or 0) >= self.MIN_SOURCE_SCORE]

        return response

    # sources score 阈值：低于此分数视为"无关"，过滤掉。
    # 经验值：BGE-M3 余弦相似度通常相关问答在 0.55+，"你好/谢谢"类寒暄都在 0.5 以下
    MIN_SOURCE_SCORE = 0.5

    async def _enrich_source_filenames(self, response: RAGResponse) -> None:
        """把 sources[].source_file 从 storage hash 文件名改成用户上传时的真实文件名

        背景：
        - rag/ 模块在索引时把 chunk.metadata['source_file'] 存成了 storage 路径里的 hash 文件名
          （例如 caaf18f90a0e4ab1b1c056634f7fa0e7.md），导致前端展示非常丑
        - Document.filename 才是用户上传时的原始文件名
        - 这里不动 rag/ 模块，只在 service 层事后覆盖
        """
        if not response.sources:
            return

        doc_ids: set[int] = set()
        for s in response.sources:
            d = _extract_doc_id(s.get("chunk_id", ""))
            if d is not None:
                doc_ids.add(d)

        if not doc_ids:
            return

        stmt = select(models.knowledge.Document.id, models.knowledge.Document.filename).where(
            models.knowledge.Document.id.in_(doc_ids)
        )
        result = await self.db.execute(stmt)
        filename_map = {row.id: row.filename for row in result.all()}

        for s in response.sources:
            doc_id = _extract_doc_id(s.get("chunk_id", ""))
            if doc_id is not None and doc_id in filename_map:
                s["source_file"] = filename_map[doc_id]


__all__ = ["RAGService"]