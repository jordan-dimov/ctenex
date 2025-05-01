from pydantic import Field, PostgresDsn, ValidationInfo, field_validator

from ctenex.settings.base import CommonSettings


class PostgresSettings(CommonSettings):
    user: str | None = Field(validation_alias="DB_USER", default="")
    password: str | None = Field(validation_alias="DB_PASS", default="")
    db: str | None = Field(validation_alias="DB_NAME", default="")
    host: str | None = Field(validation_alias="DB_HOST", default="")
    uri: PostgresDsn | str | None = Field(validation_alias="DB_URI", default=None)

    @field_validator("uri")
    def assemble_db_uri(cls, v, values: ValidationInfo):
        if not v:
            # .env file with settings but no URI
            return PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=values.data.get("user", ""),
                password=values.data.get("password", ""),
                host=values.data.get("host", ""),
                port=values.data.get("port", 5432),
                path=f"{values.data.get('db', '')}",
            )

        # .docker.env file
        if isinstance(v, str):
            return v
