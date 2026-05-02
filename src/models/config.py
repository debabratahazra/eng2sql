"""Data models and configuration dataclasses for Eng2SQL."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DBConfig:
    """MySQL database connection configuration."""

    host: str
    port: int
    user: str
    password: str
    database: str
    dialect: str = "mysql+pymysql"
    connect_timeout: int = 5

    @property
    def connection_url(self) -> str:
        """Return a SQLAlchemy connection URL (password redacted in repr)."""
        return (
            f"{self.dialect}://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )

    def __repr__(self) -> str:
        return (
            f"DBConfig(host={self.host!r}, port={self.port}, "
            f"user={self.user!r}, database={self.database!r})"
        )


@dataclass
class AppConfig:
    """OpenAI and application-level configuration."""

    openai_api_key: str
    openai_base_url: str = "https://gpt4ifx.icp.infineon.com"
    openai_cert_path: str = "cert/ca-bundle.crt"
    model_name: str = "gpt-5.2"
    max_tokens: int = 500
    temperature: float = 0.1

    def __repr__(self) -> str:
        masked = self.openai_api_key[:8] + "…" if self.openai_api_key else "(not set)"
        return (
            f"AppConfig(model={self.model_name!r}, "
            f"max_tokens={self.max_tokens}, api_key={masked!r})"
        )

@dataclass
class SchemaColumn:
    """Metadata for a single database column."""

    name: str
    type: str
    nullable: bool = True
    primary_key: bool = False
    default: str | None = None


# TableSchema maps table names → list of column definitions
TableSchema = dict[str, list[SchemaColumn]]


@dataclass
class GenerationResult:
    """Result of a SQL generation attempt."""

    sql: str
    question: str
    schema_tables: list[str] = field(default_factory=list)
    model: str = "gpt-5.2"
    tokens_used: int = 0
