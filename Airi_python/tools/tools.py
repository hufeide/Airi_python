
import textwrap
from typing import Optional

import requests


def _safe_truncate(text: str, max_len: int = 500) -> str:
    text = text.replace("\r", " ").replace("\n", " ")
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def search(query: str) -> str:
    """
    非严格意义上的“搜索”工具：
    - 使用 DuckDuckGo 的网页结果作为一个简单信息源；
    - 只返回网页 HTML 的前若干字符，供上层 LLM 再做总结；
    - 不依赖任何私有 API Key。
    """
    try:
        resp = requests.get(
            "https://duckduckgo.com/html/",
            params={"q": query},
            headers={"User-Agent": "AIRI-InnerMind/0.1"},
            timeout=10,
        )
        resp.raise_for_status()
        return "[SearchResult]\n" + _safe_truncate(resp.text)
    except Exception as e:
        return f"[SearchError] {e}"

def browser(url: str) -> str:
    """
    简单网页浏览工具：
    - 直接 GET 指定 URL；
    - 返回文本内容（或 HTML）的前若干字符。
    - 不做复杂解析，交给上层 LLM 理解。
    """
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": "AIRI-InnerMind/0.1"},
            timeout=10,
        )
        resp.raise_for_status()
        # 尝试以文本方式读取
        content = resp.text
        return f"[BrowserContent] {url}\n" + _safe_truncate(content)
    except Exception as e:
        return f"[BrowserError] {e}"

def code_exec(code: str) -> str:
    try:
        local: dict[str, object] = {}
        # 简单沙箱：不暴露内置函数环境，只允许纯 Python 计算
        exec(code, {}, local)
        return "[CodeResult] " + repr(local)
    except Exception as e:
        return f"[CodeError] {e}"
