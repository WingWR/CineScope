from __future__ import annotations

from server.app.core.errors import not_implemented


class AgentPlanner:
    def plan(self, message: str):
        not_implemented("agent.planner", "plan")
