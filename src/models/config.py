"""Data models and configuration dataclasses for Eng2SQL."""
from __future__ import annotations

import urllib.parse
from dataclasses import dataclass, field


# SQLAlchemy driver scheme map for short-form dialect names.
# Extended in EPIC-009 (Sprint 10) to support PostgreSQL via psycopg3.
_DRIVER_SCHEMES: dict[str, str] = {
    "mysql": "mysql+pymysql",
    "postgresql": "postgresql+psycopg",
}

# Allowed PostgreSQL sslmode values (matches libpq).
_VALID_SSLMODES: frozenset[str] = frozenset(
    {"disable", "allow", "prefer", "require", "verify-ca", "verify-full"}
)


@dataclass
class DBConfig:
    """Relational database connection configuration (MySQL / PostgreSQL).

    The ``dialect`` field accepts the short form ("mysql", "postgresql") and the
    URL builder picks the right SQLAlchemy driver scheme. Legacy long-form values
    such as ``"mysql+pymysql"`` are still accepted for backward compatibility
    (Sprint 1\u20139 callers may still pass them) but new code SHOULD use the
    short form.

    PostgreSQL only:
        ``sslmode`` must be one of ``disable``, ``allow``, ``prefer``,
        ``require``, ``verify-ca``, ``verify-full``. Defaults to ``"prefer"``
        (the libpq default) when unset.
    """

    host: str
    port: int
    user: str
    password: str
    database: str
    dialect: str = "mysql"
    connect_timeout: int = 5
    sslmode: str | None = None

    def __post_init__(self) -> None:
        # Normalise legacy long-form dialect strings to the new short form.
        if "+" in self.dialect:
            short = self.dialect.split("+", 1)[0]
            if short in _DRIVER_SCHEMES:
                self.dialect = short
        if self.dialect not in _DRIVER_SCHEMES:
            raise ValueError(
                f"Unsupported dialect {self.dialect!r}. "
                f"Expected one of {sorted(_DRIVER_SCHEMES)}."
            )
        if self.sslmode is not None and self.sslmode not in _VALID_SSLMODES:
            raise ValueError(
                f"Invalid sslmode {self.sslmode!r}. "
                f"Expected one of {sorted(_VALID_SSLMODES)}."
            )

    @property
    def connection_url(self) -> str:
        """Return a SQLAlchemy connection URL for this dialect.

        - MySQL  → ``mysql+pymysql://user:pw@host:port/db``
        - PostgreSQL → ``postgresql+psycopg://user:pw@host:port/db?sslmode=<mode>``
        """
        scheme = _DRIVER_SCHEMES[self.dialect]
        encoded_pw = urllib.parse.quote_plus(self.password)
        base = f"{scheme}://{self.user}:{encoded_pw}@{self.host}:{self.port}/{self.database}"
        if self.dialect == "postgresql":
            sslmode = self.sslmode or "prefer"
            return f"{base}?sslmode={sslmode}"
        return base

    def __repr__(self) -> str:
        return (
            f"DBConfig(host={self.host!r}, port={self.port}, "
            f"user={self.user!r}, database={self.database!r}, "
            f"dialect={self.dialect!r})"
        )

@dataclass
class MongoConfig:
    """MongoDB connection configuration."""

    host: str
    port: int = 27017
    username: str = ""
    password: str = ""
    auth_source: str = "admin"
    auth_mechanism: str = "SCRAM-SHA-256"
    connect_timeout_ms: int = 5000
    raw_uri: str = ""

    @property
    def connection_uri(self) -> str:
        """Return a mongodb:// URI with percent-encoded password.

        When ``raw_uri`` is non-empty the URI-mode path is used:
        - If the URI already contains embedded credentials (``@`` in netloc),
          a ``ValueError`` is raised asking the user to supply them separately.
        - If ``username`` is provided, credentials are injected into the netloc.
        - If ``username`` is empty, the URI is returned as-is.

        When ``raw_uri`` is empty the field-based path is used:
        - When username is empty, returns an unauthenticated URI.
        - When username is set but auth_mechanism is "None / No Auth", includes
          credentials without an authMechanism parameter so the driver can
          auto-negotiate SCRAM (fixes BUG-004).
        """
        if self.raw_uri:
            return self._connection_uri_from_raw()

        # Field-based path (original logic)
        if not self.username:
            return f"mongodb://{self.host}:{self.port}/"
        encoded_pw = urllib.parse.quote_plus(self.password)
        base = f"mongodb://{self.username}:{encoded_pw}@{self.host}:{self.port}/"
        if self.auth_mechanism == "None / No Auth":
            return f"{base}?authSource={self.auth_source}"
        return (
            f"{base}?authSource={self.auth_source}"
            f"&authMechanism={self.auth_mechanism}"
        )

    def _connection_uri_from_raw(self) -> str:
        """Build a URI from ``raw_uri`` with optional credential injection.

        If the URI already contains embedded credentials (``user:pass@host``),
        it is returned as-is and the separate ``username``/``password`` fields
        are ignored.  Otherwise credentials are injected from those fields.

        Returns:
            The resolved URI string.
        """
        parsed = urllib.parse.urlparse(self.raw_uri)
        if "@" in (parsed.netloc or ""):
            # URI already contains embedded credentials — use it as-is.
            # The separate Username/Password fields are ignored when the URI
            # already carries credentials (standard full-URI workflow).
            return self.raw_uri
        if not self.username:
            return self.raw_uri
        encoded_pw = urllib.parse.quote_plus(self.password)
        # Reconstruct netloc with injected credentials
        host_part = parsed.netloc or parsed.path
        new_netloc = f"{self.username}:{encoded_pw}@{host_part}"
        if parsed.netloc:
            injected = parsed._replace(netloc=new_netloc)
        else:
            # Handles edge cases where urlparse puts host in path (rare)
            injected = parsed._replace(netloc=new_netloc, path="")
        return urllib.parse.urlunparse(injected)

    def __repr__(self) -> str:
        return (
            f"MongoConfig(host={self.host!r}, port={self.port}, "
            f"username={self.username!r}, auth_mechanism={self.auth_mechanism!r})"
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
        masked = self.openai_api_key[:8] + "..." if self.openai_api_key else "(not set)"
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


# TableSchema maps table names to list of column definitions
TableSchema = dict[str, list[SchemaColumn]]


@dataclass
class GenerationResult:
    """Result of a SQL generation attempt."""

    sql: str
    question: str
    schema_tables: list[str] = field(default_factory=list)
    model: str = "gpt-5.2"
    tokens_used: int = 0


