from __future__ import annotations

from recommender.core.service import RecommenderService


def main() -> None:
    service = RecommenderService()

    content = service.recommend_by_content("Toy Story", top_k=10)
    print("Content-based recommendations:")
    for item in content.items:
        print(f"{item.movie_id}\t{item.title}\t{item.score:.4f}")

    collaborative = service.recommend_by_collaborative(
        user_id=1,
        movie_name="Toy Story",
        top_k=10,
        neighbor_k=10,
    )
    print("\nCollaborative recommendations:")
    for item in collaborative.items:
        print(f"{item.movie_id}\t{item.title}\t{item.score:.4f}")


if __name__ == "__main__":
    main()

