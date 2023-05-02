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


class Settings(BaseSettings):
    mongo: MongoDB = MongoDB()
    proxy_urls: ProxiedUrls = ProxiedUrls()
    open_api: OpenAPI = OpenAPI()

    class Config:
        env_prefix = "canary_"


SETTINGS = Settings()  # type: ignore
