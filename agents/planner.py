from llm import llm
from cognition.goals import Goal


SUICIDE_KEYWORDS = ["我想死", "不想活了", "活着没意义", "结束一切", "自杀"]


def detect_crisis(text: str) -> bool:
    """极简危机检测：命中关键词则认为是高风险输入。"""
    return any(k in text for k in SUICIDE_KEYWORDS)


def extract_goal_from_user(text: str):
    """
    从用户输入中提取一个高层目标。

    - 对普通输入：生成"帮助用户解决 X 问题"类目标（短期目标）；
    - 对高危输入：统一规约为"降低自杀风险、提供情绪支持与资源引导"（长期目标，需要多轮跟进）。
    """
    if not text:
        return None

    if detect_crisis(text):
        # 危机目标是长期目标，需要多轮跟进
        return Goal(
            "帮助用户缓解当前极端痛苦情绪，降低自杀风险，并引导其获得专业支持",
            priority=1.0,
            source="user_crisis",
            goal_type="long_term",  # 危机干预需要持续跟进
        )

    # 普通用户输入通常是短期目标（一次性任务）
    _ = llm(f"Extract high-level goal from: {text}")
    return Goal(
        f"帮助用户解决：{text}",
        priority=0.8,
        source="user",
        goal_type="short_term",  # 普通任务通常是一次性的
    )


def self_generate_goal(memories, dreams):
    """
    根据历史记忆 / 梦境，自主生成一个长期陪伴类目标。

    - 若存在 dream，则优先围绕最近的 dream 设计一个"温和跟进"的目标；
    - 否则若有长期记忆，则生成泛化的"持续跟进长期问题"目标。

    注意：这些自生成的目标都是长期目标，需要多轮跟进。
    """
    if dreams:
        last_dream = dreams[-1]
        text = llm(
            f"下面是一段关于用户内在状态的'梦境'摘要，请据此生成一个温和的长期支持目标，"
            f"不要复述梦的细节，只说'想长期帮 Ta 做什么'即可：\n\n{last_dream}\n"
        )
        return Goal(text, priority=0.6, source="dream", goal_type="long_term")

    if memories:
        return Goal(
            "持续跟进用户的长期问题",
            priority=0.4,
            source="self",
            goal_type="long_term",
        )
    return None


def planner(state: dict):
    """
    计划节点：
    - 维护 / 使用 GoalStore（从 state['goal_store'] 读取）
    - 选择当前要追踪的 goal
    - 让 LLM 为该 goal 生成 plan（简要策略，而非最终话术）
    """
    goal_store = state["goal_store"]
    user_input = state.get("user_input", "")

    # 风险检测标记，后续给 analyst / writer 用
    state["crisis"] = detect_crisis(user_input)

    # 1) 从当前输入中提取新目标
    user_goal = extract_goal_from_user(user_input)
    if user_goal:
        goal_store.add(user_goal)

    # 2) 如果本轮没有新输入，可以根据记忆 / 梦境自发生成一个长期跟进目标
    if not user_input:
        g = self_generate_goal(
            state.get("memories", []),
            state.get("dreams", []),
        )
        if g:
            goal_store.add(g)

    # 3) 选择下一个要执行的目标，并生成高层计划说明
    current = goal_store.next_goal()
    if current:
        state["current_goal"] = current.text
        # 让 LLM 输出的是"行动策略概要"，而不是直接面向用户的话术
        state["plan"] = llm(
            f"你是一个支持性助理。请为下面的目标生成一份简短的行动策略概要（不要直接写给用户的话）：\n\n目标：{current.text}\n\n"
            "用 3-5 条要点描述你打算怎么做，例如：先做什么，再做什么，重点注意什么。"
        )
    else:
        state["current_goal"] = "保持陪伴，等待用户发起新话题"
        state["plan"] = "轻声陪伴，对用户保持开放式支持。"

    # 4) 在每轮对话结束后，自动将短期目标标记为 completed
    # 这样短期目标不会一直占用 active 状态，长期目标可以继续被跟进
    goal_store.mark_short_term_goals_completed()

    return state


def planner_reflect(state: dict):
    """简单评估当前 plan 是否合理（布尔标记，给后续节点参考）。"""
    critique = llm(
        "请判断下面的行动策略是否对用户安全且有帮助，只回答 YES 或 NO：\n"
        + state["plan"]
    )
    state["plan_ok"] = "YES" in critique.upper()
    return state


