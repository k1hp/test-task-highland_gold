from pydantic import computed_field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
import pathlib


BASE_DIR = pathlib.Path(__file__).parent.parent.parent.absolute()
print(BASE_DIR)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / "backend" / ".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    @computed_field
    @property
    def UPLOAD_DIR(self) -> pathlib.Path:
        upload_path = BASE_DIR / 'uploaded_files'
        upload_path.mkdir(parents=True, exist_ok=True)
        return upload_path


settings = Settings()

