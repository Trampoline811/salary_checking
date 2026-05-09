"""多模型 LLM 客户端：统一接口，通过 provider 切换后端。"""
from abc import ABC, abstractmethod
import httpx


class BaseClient(ABC):
    @abstractmethod
    def chat(self, messages: list[dict], **kwargs) -> str:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...


class OpenAICompatClient(BaseClient):
    """OpenAI 兼容接口，适用于绝大多数 LLM API（上海AI Lab、DeepSeek、vLLM 等）。"""

    def __init__(self, api_key: str, base_url: str, model: str = "default"):
        self._api_key = api_key
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        self._base_url = base_url
        self._model = model
        self._name = f"openai-compat({model})"

    @property
    def name(self) -> str:
        return self._name

    def chat(self, messages: list[dict], temperature: float = 0.7, max_tokens: int = 512) -> str:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            resp = httpx.post(
                f"{self._base_url}/chat/completions",
                headers=headers,
                json=body,
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPError as e:
            return f"🤖 API 请求失败: {e}"
        except (KeyError, IndexError) as e:
            return f"🤖 响应解析失败: {e}"


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

    if provider in ("shanghai", "deepseek", "openai", "custom"):
        return OpenAICompatClient(api_key=api_key, base_url=base_url, model=model)

    return MockClient()
