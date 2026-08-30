"""
接口抽象层。

业务代码只依赖这里的 ABC，不依赖 rag/implementations/ 里的具体实现。
这是 SOLID 依赖倒置原则 (DIP) 的体现。
"""
from rag.interfaces.embedding import EmbeddingInterface
from rag.interfaces.vector_store import VectorStoreInterface, Chunk
from rag.interfaces.llm import LLMInterface, Message
from rag.interfaces.parser import DocumentParserInterface, ParsedDocument

__all__ = [
    # interfaces
    "EmbeddingInterface",
    "VectorStoreInterface",
    "LLMInterface",
    "DocumentParserInterface",
    # data structures
    "Chunk",
    "Message",
    "ParsedDocument",
]