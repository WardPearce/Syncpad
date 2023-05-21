from pydantic import BaseModel, Field


class CanaryModel(BaseModel):
    domain: str = Field(
        ...,
        regex=r"(?i)^((?!(?:www|www\d+)\.)[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+(?:[a-zA-Z]{2,})$",
    )
