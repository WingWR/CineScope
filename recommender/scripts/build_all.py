from __future__ import annotations

import json

from recommender.algorithms.collaborative.builder import build_collaborative_artifacts
from recommender.algorithms.content_based.builder import build_content_artifacts


def main() -> None:
    payload = {
        "content_based": build_content_artifacts(),
        "collaborative": build_collaborative_artifacts(),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

