from __future__ import annotations

import json

from recommender.algorithms.content_based.builder import build_content_artifacts


def main() -> None:
    metadata = build_content_artifacts()
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

