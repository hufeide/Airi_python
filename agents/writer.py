
import json

from llm import llm


def _parse_analysis(analysis_text: str):
    try:
        return json.loads(analysis_text or "{}")
    except Exception:
        return {}


def writer(state: dict):
    """
    Writer 作为唯一对用户"说话"的出口：
    - 使用 user_input / current_goal / plan / analysis（结构化）/ persona / memories；
    - 严禁再对内部话术做元评述，始终面向用户。
    - 必须基于对话历史（memories）给出连贯、具体的回答。
    """
    persona = state.get("persona")
    user_input = state.get("user_input", "")
    current_goal = state.get("current_goal", "")
    plan = state.get("plan", "")
    crisis = bool(state.get("crisis"))
    memories = state.get("memories", [])
    analysis_info = _parse_analysis(state.get("analysis", ""))

    # 从 persona 粗略推一个风格
    style_hint = "balanced"
    if hasattr(persona, "emotional") and hasattr(persona, "rational"):
        style_hint = "warm" if persona.emotional > persona.rational else "logical"

    risk_level = analysis_info.get("risk_level", "low")
    need_hotline = bool(analysis_info.get("need_hotline", False))
    focus = analysis_info.get("focus", "")

    # 格式化对话历史，供 LLM 参考
    context_history = ""
    if memories:
        context_history = "\n".join([f"- {m}" for m in memories[-5:]])  # 只取最近 5 条
        context_history = f"\n\n之前的对话历史（请基于这些信息给出连贯的回答）：\n{context_history}"

    # 构造 writer 的最终提示
    prompt = f"""
你是一个支持性助理，正在和用户进行对话。

用户刚刚说：
{user_input}
{context_history}

当前支持目标：
{current_goal}

内部拟定的行动策略（请基于这些策略，自然地给出具体、有用的回答）：
{plan}

内部风险评估：
- 危险等级: {risk_level}
- 是否需要提供危机热线: {need_hotline}
- 本轮回应重点: {focus}

对话风格偏好: {style_hint}

重要要求：
1. **必须基于对话历史给出连贯回答**：如果用户之前提到过某些信息（如"我想去东北"），要自然地关联起来，不要每次都重新问一遍。
2. **给出具体、有用的信息**：不要只说"我可以帮你"，而要基于 plan 中的策略，自然地提供具体建议、推荐、步骤等。
3. **直接回答用户的问题**：如果用户问"我想去东北"，不要只问"你想做什么"，而要给出关于东北旅行的具体建议（季节、景点、注意事项等）。
4. **保持自然对话**：不要暴露"这是内部计划"等细节，但要自然地融入 plan 中的信息。

请你用简洁、温柔且真诚的中文，直接对用户说话：
- 如果用户处在高风险（例如有强烈绝望、自杀念头），务必先承接情绪、表达理解，再提醒其生命价值，最后温和地建议寻求专业帮助或危机热线；
- 如果风险较低，则自然、友好地陪伴和引导，给出具体、有用的回答，但仍保持尊重与敏感；
- 可以适当追问（开放式问题），但不要给出医疗诊断。
"""
    state["reply"] = llm(prompt)
    return state

