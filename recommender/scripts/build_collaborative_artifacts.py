from __future__ import annotations

import json

from recommender.algorithms.collaborative.builder import build_collaborative_artifacts


def main() -> None:
    metadata = build_collaborative_artifacts()
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

