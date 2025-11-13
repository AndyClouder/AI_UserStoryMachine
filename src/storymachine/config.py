from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # TODO: memoize settings so it's only ever read once
    openai_api_key: str | None = Field(None, frozen=True, alias="OPENAI_API_KEY")
    zhipuai_api_key: str | None = Field(None, frozen=True, alias="ZHIPUAI_API_KEY")
    github_token: str | None = Field(None, frozen=True, alias="GITHUB_TOKEN")
    gitlab_token: str | None = Field(None, frozen=True, alias="GITLAB_TOKEN")
    model: str = Field("glm-4-flash", alias="MODEL")
    reasoning_effort: str = Field("low", alias="REASONING_EFFORT")
    api_provider: str = Field("zhipuai", alias="API_PROVIDER")  # "openai" or "zhipuai"

    class Config:
        env_file = ".env"
