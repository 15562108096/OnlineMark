# 云教学服务平台 - 配置
import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "云教学服务平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库配置
    DB_TYPE: str = "sqlite"
    DB_SQLITE_PATH: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "online_mark.db"
    )
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "onlinemark"

    @property
    def DATABASE_URL(self) -> str:
        if self.DB_TYPE.lower() == "mysql":
            return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

        sqlite_path = Path(self.DB_SQLITE_PATH).resolve().as_posix()
        return f"sqlite:///{sqlite_path}"

    # JWT配置
    SECRET_KEY: str = "please-change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # 文件上传
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
    TEMPLATE_DIR: str = os.path.join(UPLOAD_DIR, "templates")
    SCAN_DIR: str = os.path.join(UPLOAD_DIR, "scans")
    SUBJECTIVE_DIR: str = os.path.join(UPLOAD_DIR, "subjective")
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024

    # OMR配置
    OMR_THRESHOLD: float = 0.3
    OMR_BLUR_KERNEL: int = 5
    OMR_ADAPTIVE_BLOCK_SIZE: int = 15

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

for d in [settings.UPLOAD_DIR, settings.TEMPLATE_DIR, settings.SCAN_DIR, settings.SUBJECTIVE_DIR]:
    os.makedirs(d, exist_ok=True)
