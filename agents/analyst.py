
from llm import llm


def analyst(state: dict):
    """
    分析节点：
    - 不再输出长篇“话术点评”，而是给出结构化信号，辅助 writer 决策。
    """
    user_input = state.get("user_input", "")
    plan = state.get("plan", "")
    crisis = bool(state.get("crisis"))

    # 让 LLM 做一个简短的结构化评估
    prompt = f"""
你是一个心理支持助理的内部分析模块。请根据下面信息，给出简短、结构化的结论：

用户输入：
{user_input}

当前行动策略概要：
{plan}

是否判定为危机场景：{crisis}

请返回 JSON，字段包括：
- "risk_level": "low" | "medium" | "high"
- "need_hotline": true/false
- "style": "high_empathy" | "calm_rational" | "mixed"
- "focus": 一句话概述这一步回复的重点。
只返回 JSON，不要解释。
"""
    try:
        analysis_text = llm(prompt)
        state["analysis"] = analysis_text
    except Exception as e:
        state["analysis"] = f'{{"risk_level":"unknown","need_hotline":false,"style":"high_empathy","focus":"陪伴用户","error":"{e}"}}'

    return state

