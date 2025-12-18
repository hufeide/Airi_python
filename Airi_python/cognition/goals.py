
import time, uuid


class Goal:
    """
    A simple goal object used by the planner.

    - text:     human readable description of the goal
    - priority: numeric score used for ranking (0.0 - 1.0)
    - source:   optional marker of where this goal comes from
                (e.g. "user" / "self"), used only for tracing / debugging
    - goal_type: "short_term" (一次性任务) or "long_term" (需要多轮跟进)
    """

    def __init__(
        self,
        text: str,
        priority: float = 0.5,
        source: str | None = None,
        goal_type: str = "short_term",
    ):
        self.id = str(uuid.uuid4())
        self.text = text
        self.priority = priority
        self.source = source or "user"
        self.goal_type = goal_type  # "short_term" or "long_term"
        self.created_at = time.time()
        self.status = "pending"  # "pending" | "active" | "completed"
        self.completed_at: float | None = None

    def score(self) -> float:
        return float(self.priority)

    def mark_completed(self):
        """标记目标为已完成状态。"""
        self.status = "completed"
        self.completed_at = time.time()

    def is_recent_and_high_priority(self, max_age_seconds: float = 300.0) -> bool:
        """
        判断是否是一个"最近创建且高优先级"的目标，可以被重新激活。

        - priority > 0.9
        - 创建时间在 max_age_seconds 内（默认 5 分钟）
        """
        age = time.time() - self.created_at
        return self.priority > 0.9 and age < max_age_seconds
