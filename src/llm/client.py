"""多模型 LLM 客户端：统一接口，通过 OpenAI SDK 调用。"""
from abc import ABC, abstractmethod


class BaseClient(ABC):
    @abstractmethod
    def chat(self, messages: list[dict], **kwargs) -> str:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...


class OpenAIClient(BaseClient):
    """基于 OpenAI SDK 的客户端，兼容书生浦语、DeepSeek 等 OpenAI 兼容 API。"""

    def __init__(self, api_key: str, base_url: str, model: str = "intern-latest"):
        from openai import OpenAI

        self._model = model
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._name = f"openai({model})"

    @property
    def name(self) -> str:
        return self._name

    def chat(self, messages: list[dict], temperature: float = 0.7, max_tokens: int = 512) -> str:
        try:
            resp = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            return f"🤖 API 请求失败: {e}"


class MockClient(BaseClient):
    """无 API 时的降级客户端，返回预设俏皮话。"""
    _REPLIES = [
        "今天也是摸鱼的好日子呢～要好好珍惜每一秒的时薪哦！",
        "摸鱼一时爽，一直摸鱼一直爽！但你的时薪正在流逝...",
        "这个功能需要配置 LLM API 才能使用哦，请在上方设置中填入 API Key~",
    ]
    _idx = 0

    @property
    def name(self) -> str:
        return "mock"

    def chat(self, messages: list[dict], **kwargs) -> str:
        reply = self._REPLIES[self._idx % len(self._REPLIES)]
        self._idx += 1
        return reply


def get_client(provider: str, api_key: str = "", base_url: str = "", model: str = "") -> BaseClient:
    if not api_key:
        return MockClient()

    if provider in ("shanghai", "intern", "deepseek", "openai", "custom"):
        return OpenAIClient(api_key=api_key, base_url=base_url, model=model or "intern-latest")

    return MockClient()
