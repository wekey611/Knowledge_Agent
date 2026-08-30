"""
RAG 模块配置。

所有可调参数集中在这里。改一处生效，业务代码完全无感。

设计原则：配置是不可变的、结构化的、有类型提示的
    用 dataclass(frozen=True) 让配置不可变，防止运行中误改。
    自动生成 __init__、IDE 提示、mypy 检查。
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class RAGConfig:
    """
    RAG 模块完整配置。

    Attributes:
        embedding_model: embedding 模型标识
            - "bge-m3": 本地 BGE-M3（中文强、免费、需 GPU）
            - "openai": OpenAI text-embedding-3-small（需 API key、要钱）
        vector_store_type: 向量库类型
            - "chroma": Chroma（学习期默认，零部署）
            - "in_memory": 内存版（仅测试）
        llm_provider: LLM 提供商
            - "mmx": MiniMax（你现有的）
            - "fake": 测试用固定返回

        chunk_size: 切块大小（token 数），常见 300~800
        chunk_overlap: 切块重叠（token 数），通常是 chunk_size 的 10%~20%

        top_k: 检索返回的 chunk 数量

        chroma_persist_dir: Chroma 数据持久化目录
    """

    # === 模型选择 ===
    embedding_model: str = "siliconflow"
    vector_store_type: str = "chroma"
    llm_provider: str = "mmx"

    # === 切块参数 ===
    chunk_size: int = 500
    chunk_overlap: int = 50

    # === 检索参数 ===
    top_k: int = 5

    # === 路径 ===
    chroma_persist_dir: str = "./chroma_data"

    # === 多租户策略（V2 新增） ===
    vector_store_strategy: str = "single_collection"  # V2 默认推荐


def load_config() -> RAGConfig:
    """
    加载配置。

    V0 阶段返回默认值（hardcode）。
    V3+ 可改为读环境变量或 yaml 配置文件。

    自动加载 .env 文件（项目根目录的 Backend/.env），
    这样 SILICONFLOW_API_KEY 等敏感配置可以从 .env 读取，
    不用每次手动 export。

    Returns:
        RAGConfig 实例（不可变）

    Example:
        >>> config = load_config()
        >>> config.chunk_size
        500
        >>> config.top_k
        5
    """
    # 自动加载 .env（如果存在）
    try:
        from dotenv import load_dotenv
        load_dotenv()  # 从 Backend/.env 加载到 os.environ
    except ImportError:
        pass  # dotenv 未安装时跳过（用系统环境变量）

    return RAGConfig()