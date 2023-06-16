import secrets
from typing import List, Optional

from pydantic import BaseModel, BaseSettings, Field


class MongoDB(BaseModel):
    host: str = "localhost"
    port: int = 27017
    collection: str = "purplix"


class ProxiedUrls(BaseModel):
    frontend: str = "http://localhost"
    backend: str = "http://localhost/api"


class S3(BaseModel):
    region_name: str
    secret_access_key: str
    access_key_id: str
    bucket: str
    folder: str = "purplix"
    download_url: str
    endpoint_url: Optional[str] = None
    chunk_size = 655400


class OpenAPI(BaseModel):
    title: str = "Purplix.io"
    version: str = "0.0.1"


class Redis(BaseModel):
    host: str = "localhost"
    port: int = 6379
    db: int = 0


class mCaptcha(BaseModel):
    verify_url: str
    site_key: str
    account_secret: str


class Documents(BaseModel):
    max_amount: int = 3
    max_size: int = 31460000
    allowed_extensions: List[str] = [
        ".pdf",
        ".png",
        ".jpeg",
        ".jpg",
        ".mp4",
        ".mp3",
        ".gif",
        ".7z",
        ".pub",
        ".txt",
    ]


class Jwt(BaseModel):
    secret: str = Field(default=secrets.token_urlsafe(32), min_length=32)
    expire_days: int = 30


class DomainVerify(BaseModel):
    prefix: str = "purplix.io__verify="
    timeout: int = 60


class Proxycheck(BaseModel):
    api_key: Optional[str] = None
    url: str = "https://proxycheck.io/v2/"


class Smtp(BaseModel):
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    email: str


class CanaryLogo(BaseModel):
    max_size = 358400
    allowed_extensions: List[str] = [
        ".png",
        ".jpeg",
        ".jpg",
    ]


class Canary(BaseModel):
    domain_verify: DomainVerify = DomainVerify()
    documents: Documents = Documents()
    logo: CanaryLogo = CanaryLogo()


class Settings(BaseSettings):
    mongo: MongoDB = MongoDB()
    redis: Redis = Redis()
    proxy_urls: ProxiedUrls = ProxiedUrls()
    open_api: OpenAPI = OpenAPI()
    mcaptcha: Optional[mCaptcha] = None
    site_name = "Purplix.io"
    proxy_check: Optional[Proxycheck] = None
    smtp: Optional[Smtp] = None
    canary: Canary = Canary()
    s3: S3
    untrusted_request_proxy: str = Field(
        ...,
        description="It's recommended to simply use a proxy for untrusted requests.",
    )

    jwt: Jwt = Jwt()
    csrf_secret: str = Field(default=secrets.token_urlsafe(32), min_length=32)

    class Config:
        env_prefix = "purplix_"


SETTINGS = Settings()  # type: ignore
