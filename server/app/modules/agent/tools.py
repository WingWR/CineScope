from __future__ import annotations

from server.app.core.errors import not_implemented


class AgentTools:
    def call(self, tool_name: str, payload: dict):
        not_implemented("agent.tools", "call")
