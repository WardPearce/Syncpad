import secrets
from typing import Optional

from pydantic import AnyHttpUrl, BaseModel, BaseSettings


class MongoDB(BaseModel):
    host: str = "localhost"
    port: int = 27017
    collection: str = "canary"


class ProxiedUrls(BaseModel):
    frontend: AnyHttpUrl = AnyHttpUrl(url="canary.localhost", scheme="http")
    backend: AnyHttpUrl = AnyHttpUrl(url="canary.localhost/api", scheme="http")


class S3(BaseModel):
    region_name: str
    secret_access_key: str
    access_key_id: str
    bucket: str
    folder: str = "canary"
    download_url: str
    endpoint_url: Optional[str] = None


class OpenAPI(BaseModel):
    title: str = "canary"
    version: str = "0.0.1"


class Redis(BaseModel):
    host: str = "redis://localhost/"
    port: int = 6379
    db: int = 0


class Settings(BaseSettings):
    mongo: MongoDB = MongoDB()
    redis: Redis = Redis()
    proxy_urls: ProxiedUrls = ProxiedUrls()
    open_api: OpenAPI = OpenAPI()
    jwt_secret: str = secrets.token_urlsafe(64)
    csrf_secret: str = secrets.token_urlsafe(64)

    class Config:
        env_prefix = "canary_"


SETTINGS = Settings()  # type: ignore
