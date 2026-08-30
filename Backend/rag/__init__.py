"""
RAG 模块：检索增强生成。

本模块独立于 FastAPI / MySQL，可单独运行（见 rag/scripts/）。
通过 rag.factory.build_pipeline() 与业务代码衔接。

模块结构：
    interfaces/        - 抽象接口（ABC），业务代码只依赖这一层
    implementations/   - 具体实现（V1+ 填充）
    chunker.py         - 切块策略（V1 填充）
    indexer.py         - 索引编排（V1 填充）
    retriever.py       - 检索（V2 填充）
    generator.py       - 生成（V3 填充）
    pipeline.py        - 完整 RAG Pipeline（V3 填充）
    evaluation/        - 评估（V4 填充）
    scripts/           - 独立运行入口（V1+ 填充）
"""
from rag.config import RAGConfig, load_config
from rag.exceptions import (
    RAGError,
    IndexingError,
    RetrievalError,
    GenerationError,
    EmbeddingError,
    ParseError,
)

__version__ = "0.1.0"

__all__ = [
    # config
    "RAGConfig",
    "load_config",
    # exceptions
    "RAGError",
    "IndexingError",
    "RetrievalError",
    "GenerationError",
    "EmbeddingError",
    "ParseError",
]