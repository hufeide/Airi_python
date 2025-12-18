
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from graph import app, tracer
from cognition.persona import PersonaState
from cognition.memory import MemoryStore
from cognition.goal_store import GoalStore

api = FastAPI()

# 简单的内存态用户会话存储（仅进程内，重启会丢失）
USERS: dict[str, dict] = {}


@api.post("/chat")
def chat(user_id: str, text: str):
    """
    对话入口：
    - 维护每个用户的 persona / memory / goal_store
    - 调用 LangGraph（planner → tool → analyst → writer）
    """
    u = USERS.setdefault(
        user_id,
        {
            "persona": PersonaState(),
            "memory": MemoryStore(),
            "goal_store": GoalStore(),
        },
    )

    # 更新画像 & 记忆
    u["persona"].update(text)
    u["memory"].add(text)
    u["memory"].consolidate()
    dream = u["memory"].dream()

    # 构造图的初始状态
    state = {
        "user_input": text,
        "persona": u["persona"],
        "goal_store": u["goal_store"],
        "memories": [m for m in u["memory"].long],
        # 将已经生成过的 dream 也注入状态，供 planner 设计长期目标
        "dreams": list(u["memory"].dreams),
    }
    out = app.invoke(state)

    return {
        "reply": out["reply"],
        "trust": u["persona"].trust,
        "relationship": u["persona"].relationship,
        "dream": dream,
    }


@api.get("/trace")
def trace():
    """返回内部各个节点的执行轨迹，供前端 ui/index.html 可视化。"""
    return tracer.traces


@api.get("/", response_class=HTMLResponse)
def index():
    """返回简单的可视化界面（ui/index.html）。"""
    ui_path = Path(__file__).parent / "ui" / "index.html"
    html = ui_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html)

