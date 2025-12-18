
from typing import List, Optional
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, END

from agents.planner import planner
from agents.analyst import analyst
from agents.writer import writer
from agents.tool_agent import tool_agent
from runtime.tracer import Tracer


class State(TypedDict, total=False):
    # 输入 / 上下文
    user_input: str
    persona: object
    goal_store: object
    memories: List[str]
    dreams: List[str]

    # 规划 / 工具 / 分析 / 回复
    current_goal: str
    plan: str
    plan_ok: bool
    tool_result: Optional[str]
    analysis: str
    reply: str


tracer = Tracer()


def wrap(name, func):
    """包装每个节点函数，执行后把 state 记录到 tracer。"""

    def _wrapped(state: State) -> State:
        out = func(state)
        tracer.record(name, out)
        return out

    return _wrapped


g = StateGraph(State)
g.add_node("planner", wrap("planner", planner))
g.add_node("tool", wrap("tool", tool_agent))
g.add_node("analyst", wrap("analyst", analyst))
g.add_node("writer", wrap("writer", writer))

g.set_entry_point("planner")
g.add_edge("planner", "tool")
g.add_edge("tool", "analyst")
g.add_edge("analyst", "writer")
g.add_edge("writer", END)
app = g.compile()

