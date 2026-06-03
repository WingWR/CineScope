import { Star } from "lucide-react";
import { formatOptionalRating } from "../../../entities/movie/formatters";
import type { Movie } from "../../../entities/movie/types";
import { cx } from "../../../shared/ui/classes";

type MoviePosterCardProps = {
  movie: Movie;
  selected: boolean;
  index: number;
  onSelect: () => void;
};

export function MoviePosterCard({ movie, selected, index, onSelect }: MoviePosterCardProps) {
  return (
    <button
      className="group grid min-w-0 animate-card-in gap-2.5 border-0 bg-transparent p-0 text-left text-inherit"
      data-selected={selected}
      type="button"
      onClick={onSelect}
      style={{ animationDelay: `${Math.min(index, 12) * 36}ms` }}
    >
      <span
        className={cx(
          "relative block aspect-[2/3] overflow-hidden rounded-xl border border-cinema-border bg-[linear-gradient(160deg,rgba(242,177,92,0.26),rgba(85,214,194,0.08)),#211d18] shadow-[0_18px_44px_rgba(0,0,0,0.32)] transition-[transform,border-color,box-shadow] duration-[220ms] ease-linear group-hover:-translate-y-[3px] group-hover:border-[rgba(242,177,92,0.68)] group-hover:shadow-[0_24px_56px_rgba(242,177,92,0.16)]",
          selected && "-translate-y-[3px] border-[rgba(242,177,92,0.68)] shadow-[0_24px_56px_rgba(242,177,92,0.16)]",
        )}
      >
        {movie.posterUrl ? (
          <img className="h-full w-full object-cover" src={movie.posterUrl} alt={`${movie.title} poster`} loading="lazy" />
        ) : (
          <span className="grid h-full w-full place-items-center bg-[radial-gradient(circle_at_72%_18%,rgba(242,177,92,0.2),transparent_28%),linear-gradient(160deg,rgba(85,214,194,0.16),rgba(242,177,92,0.12)),rgba(255,255,255,0.04)] p-[18px] text-center text-[0.94rem] font-[760] leading-[1.2] text-cinema-text">
            {movie.title}
          </span>
        )}
      </span>
      <span className="grid min-w-0 gap-[5px]">
        <strong className="truncate text-[0.92rem] text-cinema-text">{movie.title}</strong>
        <span className="flex items-center gap-1.5 text-[0.8rem] text-cinema-muted">
          {movie.year ?? "Year pending"}
          <i className="size-[3px] rounded-full bg-cinema-muted" aria-hidden="true" />
          <Star size={13} fill="currentColor" strokeWidth={0} />
          {formatOptionalRating(movie.ratingMean)}
        </span>
      </span>
    </button>
  );
}
