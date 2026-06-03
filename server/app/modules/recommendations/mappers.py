from __future__ import annotations

from typing import Any

from server.app.modules.recommendations.schemas import RecommendationItem


def recommender_item_to_schema(item: dict[str, Any]) -> RecommendationItem:
    raise NotImplementedError("Recommendation mapping is not implemented yet.")
