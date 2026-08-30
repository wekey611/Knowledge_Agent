"""
RAG 模块自定义异常。

为什么需要自定义异常：
    业务代码 (app/) 调 RAG 模块时，可能想知道"是索引失败还是检索失败还是生成失败"，
    分别做不同处理。用自定义异常分类比直接抛 ValueError 更精准。
"""


class RAGError(Exception):
    """RAG 模块所有异常的基类。"""

    pass


class IndexingError(RAGError):
    """索引阶段错误：解析、切块、embedding、写入向量库失败。"""

    pass


class RetrievalError(RAGError):
    """检索阶段错误：向量库查询失败。"""

    pass


class GenerationError(RAGError):
    """生成阶段错误：LLM 调用失败。"""

    pass


class EmbeddingError(RAGError):
    """Embedding 模型调用失败。"""

    pass


class ParseError(RAGError):
    """文档解析失败。"""

    pass