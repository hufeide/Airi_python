
import os
from typing import Optional

import requests


# vLLM 本地服务配置（可通过环境变量覆盖）
VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://192.168.1.212:9401")
VLLM_MODEL = os.getenv("VLLM_MODEL", "")
VLLM_API_KEY = os.getenv("VLLM_API_KEY", "")  # 如果你的服务需要 key，则在这里传


def _call_vllm_chat(prompt: str, system_prompt: Optional[str] = None) -> str:
    """
    调用本地 vLLM 的 OpenAI-chat 兼容接口：
    默认假设为:  POST {VLLM_BASE_URL}/v1/chat/completions
    请求/返回格式与 OpenAI 官方基本一致。
    """
    url = f"{VLLM_BASE_URL.rstrip('/')}/v1/chat/completions"

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    headers = {}
    if VLLM_API_KEY:
        headers["Authorization"] = f"Bearer {VLLM_API_KEY}"

    resp = requests.post(
        url,
        headers=headers,
        json={
            "model": VLLM_MODEL,
            "messages": messages,
            "max_tokens": 4000,
            "temperature": 0.7,
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def llm(prompt: str) -> str:
    """
    统一的大模型调用入口。

    当前实现：调用本地 vLLM 的 /v1/chat/completions 接口。
    - 如需修改 URL / 模型，在环境变量中设置：
      - VLLM_BASE_URL  (默认: http://127.0.0.1:8000)
      - VLLM_MODEL     (默认: gpt-4o-mini)
      - VLLM_API_KEY   (如有需要)
    """
    try:
        return _call_vllm_chat(
            prompt,
            system_prompt="你是一个中文友好的助理，回答要简洁、清晰。",
        )
    except Exception as e:
        # 兜底：避免整个应用崩溃，同时把错误信息暴露出来便于排查
        return f"[LLM error: {e}]\nPrompt tail: {prompt[-200:]}"

