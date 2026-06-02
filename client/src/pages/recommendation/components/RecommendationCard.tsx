import { ArrowUpRight, Gauge } from "lucide-react";
import type { CSSProperties } from "react";
import { formatScore } from "../../../entities/movie/formatters";
import type { RecommendationItem } from "../../../entities/movie/types";

type RecommendationCardProps = {
  item: RecommendationItem;
  index: number;
};

export function RecommendationCard({ item, index }: RecommendationCardProps) {
  return (
    <article className="recommend-card" style={{ "--stagger": `${index * 42}ms` } as CSSProperties}>
      {item.movie.posterUrl ? (
        <img src={item.movie.posterUrl} alt={`${item.movie.title} poster`} loading="lazy" />
      ) : (
        <span className="recommend-poster-placeholder">{item.movie.title}</span>
      )}
      <div className="recommend-card__content">
        <div>
          <h2>{item.movie.title}</h2>
          <p>
            {item.movie.year ?? "Year pending"} / {(item.movie.genres ?? []).slice(0, 3).join(" / ") || "Genres pending"}
          </p>
        </div>
        <p>{item.reason}</p>
      </div>
      <div className="recommend-card__score">
        <Gauge size={16} />
        <strong>{formatScore(item.score)}</strong>
        <span>{item.source}</span>
      </div>
      <ArrowUpRight className="recommend-card__arrow" size={17} />
    </article>
  );
}
