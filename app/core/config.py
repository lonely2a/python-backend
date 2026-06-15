"""应用配置管理模块"""
from pydantic_settings import SettingsConfigDict
from pydantic import BaseModel
from typing import Optional


class Settings(BaseModel):
    """应用配置类"""
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # API配置
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Exness Trading Assistant Backend"

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # JWT认证配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时

    # MT5配置
    MT5_PATH: Optional[str] = None  # MT5终端路径,None表示使用默认路径

    # CORS配置
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://192.168.1.*",
    ]

    # 日志配置
    LOG_LEVEL: str = "INFO"


# 创建全局配置实例
settings = Settings()
