from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM
    llm_provider: str = "anthropic"
    llm_model: str = "claude-sonnet-4-6"
    llm_api_key: str = ""

    # Embeddings (local sentence-transformers model — no API key required)
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    vector_size: int = 384

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: str = ""
    qdrant_collection_name: str = "corksy_documents"

    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 64

    # Upload
    supported_extensions: str = ".pdf,.txt,.json,.csv,.md"
    max_file_size_mb: int = 50

    # App
    app_env: str = "development"
    log_level: str = "INFO"


settings = Settings()
