from __future__ import annotations


def normalize_scores(scores: dict[int, float]) -> dict[int, float]:
    if not scores:
        return {}
    values = list(scores.values())
    low = min(values)
    high = max(values)
    if high <= low:
        return {key: 1.0 for key in scores}
    return {key: (value - low) / (high - low) for key, value in scores.items()}


def merge_weighted_scores(
    score_groups: list[tuple[dict[int, float], float]],
    exclude: set[int] | None = None,
) -> dict[int, float]:
    excluded = exclude or set()
    merged: dict[int, float] = {}
    for scores, weight in score_groups:
        if not scores or weight <= 0:
            continue
        for movie_id, score in normalize_scores(scores).items():
            if movie_id in excluded:
                continue
            merged[movie_id] = merged.get(movie_id, 0.0) + weight * score
    return merged


def top_scores(scores: dict[int, float], top_k: int) -> list[tuple[int, float]]:
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_k]

