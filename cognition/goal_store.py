
import time


class GoalStore:
    def __init__(self):
        self.goals = []

    def add(self, goal):
        self.goals.append(goal)

    def next_goal(self):
        """
        选择下一个要执行的目标。

        规则：
        1. 优先从 pending 状态中选择
        2. 如果没有 pending，考虑重新激活符合条件的 active 目标：
           - 优先级 > 0.9
           - 创建时间在 5 分钟内
        3. 只考虑 pending 和符合条件的 active，忽略 completed
        """
        # 1. 收集所有可候选的目标：pending + 符合条件的 active
        candidates = []
        for g in self.goals:
            if g.status == "pending":
                candidates.append(g)
            elif g.status == "active" and g.is_recent_and_high_priority():
                # 允许高优先级且最近创建的 active 目标被重新选中
                candidates.append(g)

        if not candidates:
            return None

        # 2. 按优先级排序，选择最高的
        selected = max(candidates, key=lambda g: g.score())

        # 3. 如果选中的是 active，说明是重新激活，保持 active 状态
        # 如果是 pending，则改为 active
        if selected.status == "pending":
            selected.status = "active"

        return selected

    def mark_short_term_goals_completed(self):
        """
        自动将所有 active 状态的短期目标标记为 completed。

        这个方法应该在每轮对话结束后调用，确保短期目标不会一直占用 active 状态。
        """
        for g in self.goals:
            if g.status == "active" and g.goal_type == "short_term":
                g.mark_completed()
