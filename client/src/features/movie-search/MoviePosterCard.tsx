import { Star } from "lucide-react";
import type { CSSProperties } from "react";
import { formatOptionalRating } from "../../entities/movie/formatters";
import type { Movie } from "../../entities/movie/types";

type MoviePosterCardProps = {
  movie: Movie;
  selected: boolean;
  index: number;
  onSelect: () => void;
};

export function MoviePosterCard({ movie, selected, index, onSelect }: MoviePosterCardProps) {
  return (
    <button
      className="movie-card"
      data-selected={selected}
      type="button"
      onClick={onSelect}
      style={{ "--stagger": `${Math.min(index, 12) * 36}ms` } as CSSProperties}
    >
      <span className="poster-frame">
        {movie.posterUrl ? (
          <img src={movie.posterUrl} alt={`${movie.title} poster`} loading="lazy" />
        ) : (
          <span className="poster-placeholder">{movie.title}</span>
        )}
      </span>
      <span className="movie-card__meta">
        <strong>{movie.title}</strong>
        <span>
          {movie.year ?? "Year pending"}
          <i aria-hidden="true" />
          <Star size={13} fill="currentColor" strokeWidth={0} />
          {formatOptionalRating(movie.ratingMean)}
        </span>
      </span>
    </button>
  );
}
