"""
Factory：RAG 模块的单一构造入口。

业务代码只调 build_pipeline() 这一个函数，拿到完整的 RAG 系统。
换 Embedding / 向量库 / LLM 实现 = 改这里，其他地方不动。
"""
from rag.config import RAGConfig
from rag.implementations.embeddings.siliconflow import SiliconFlowEmbedding
from rag.implementations.vector_stores.chroma import ChromaVectorStore
from rag.interfaces.embedding import EmbeddingInterface
from rag.interfaces.vector_store import VectorStoreInterface
from rag.interfaces.llm import LLMInterface
from rag.indexer import Indexer


def build_embedding(config: RAGConfig) -> EmbeddingInterface:
    """
    构造 Embedding 实例。

    V1: 只支持硅基流动（最简）。
    V2+: 按 config.embedding_model 路由到不同实现。
    """
    if config.embedding_model == "siliconflow":
        return SiliconFlowEmbedding()
    elif config.embedding_model == "bge-m3":
        # V2 实现：本地 sentence-transformers
        raise NotImplementedError("本地 BGE-M3 V2 实现")
    else:
        raise ValueError(f"不支持的 embedding_model: {config.embedding_model}")


def build_vector_store(config: RAGConfig) -> VectorStoreInterface:
    """
    构造向量库实例。

    V1: 只支持 Chroma。
    V2: 支持 Chroma 的 single_collection / multi_collection 两种策略。
    """
    if config.vector_store_type == "chroma":
        return ChromaVectorStore(
            persist_dir=config.chroma_persist_dir,
            strategy=config.vector_store_strategy,
        )
    elif config.vector_store_type == "in_memory":
        # V2 实现
        raise NotImplementedError("InMemory V2 实现")
    else:
        raise ValueError(f"不支持的 vector_store_type: {config.vector_store_type}")


def build_llm(config: RAGConfig) -> LLMInterface:
    """构造 LLM 实例。V3 实现。

    注意：`llm_provider == "mmx"` 是历史命名（源自 Handoff V3 时期的 mmx-cli 方案），
    实际跑的是 MiniMax API（OpenAI 兼容协议），由 ``MiniMaxLLM`` 实现。
    """
    if config.llm_provider == "mmx":
        from rag.implementations.llms.mmx import MiniMaxLLM
        return MiniMaxLLM()
    elif config.llm_provider == "fake":
        from rag.implementations.llms.fake import FakeLLM
        return FakeLLM()
    elif config.llm_provider == "deepseek":
        from rag.implementations.llms.deepseek import DeepSeekLLM
        return DeepSeekLLM()
    else:
        raise ValueError(f"不支持的 llm_provider: {config.llm_provider}")


def build_indexer(config: RAGConfig) -> Indexer:
    """
    构造 Indexer（V1 新增）。

    Indexer 依赖 Embedding + VectorStore + Chunker，由 factory 统一构造。
    """
    from rag.chunker import RecursiveChunker

    return Indexer(
        embedding=build_embedding(config),
        vector_store=build_vector_store(config),
        chunker=RecursiveChunker(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
        ),
    )


def build_pipeline(config: RAGConfig) -> "RAGPipeline":
    """
    构造完整 RAG Pipeline。V3 实现。

    Pipeline = Retriever + Generator。
    """
    from rag.generator import Generator
    from rag.pipeline import RAGPipeline

    retriever = build_retriever(config)
    generator = Generator(llm=build_llm(config))

    return RAGPipeline(retriever=retriever, generator=generator)


def build_retriever(config: RAGConfig) -> "Retriever":
    """
    构造 Retriever（V2 新增）。

    Retriever = Embedding + VectorStore + top_k 配置。
    业务代码只需要调 retriever.retrieve(query, kb_id) 即可。
    """
    from rag.retriever import Retriever

    return Retriever(
        embedding=build_embedding(config),
        vector_store=build_vector_store(config),
        default_top_k=config.top_k,
    )