import { ArrowRight, Clock, DollarSign, Flame, Star, TrendingUp } from "lucide-react";
import { formatOptionalMoney, formatOptionalRating, formatOptionalRuntime } from "../../../entities/movie/formatters";
import type { Movie } from "../../../entities/movie/types";
import { ConnectionNotice } from "../../../shared/ui/ConnectionNotice";
import { MetricTile } from "../../../shared/ui/MetricTile";
import { cx, panelClass, primaryActionClass } from "../../../shared/ui/classes";

type MovieDetailPanelProps = {
  movie?: Movie;
  onRecommend?: (movie: Movie) => void;
  onPredict?: (movie: Movie) => void;
  showEmptyActionHint?: boolean;
};

export function MovieDetailPanel({ movie, onRecommend, onPredict, showEmptyActionHint = true }: MovieDetailPanelProps) {
  if (!movie) {
    return (
      <aside className={cx(panelClass, "sticky top-24 overflow-hidden p-[18px] max-[1180px]:static max-[1180px]:col-span-full")} aria-label="Movie details pending">
        <ConnectionNotice
          title="Waiting for movie details"
          message="After a real search result is selected, backend movie details, metrics, and recommendation actions appear here."
          actionHint={showEmptyActionHint ? "Suggested detail fields: title/year/genres/overview/ratingMean/revenue/posterUrl/backdropUrl" : undefined}
        />
      </aside>
    );
  }

  return (
    <aside className={cx(panelClass, "sticky top-24 overflow-hidden max-[1180px]:static max-[1180px]:col-span-full")} aria-label={`${movie.title} details`}>
      <div className="relative flex min-h-[210px] items-end p-[18px] after:absolute after:inset-0 after:bg-[linear-gradient(180deg,rgba(14,13,11,0.08),rgba(14,13,11,0.9))] after:content-['']">
        {movie.backdropUrl ? <img className="absolute inset-0 h-full w-full object-cover opacity-[0.74]" src={movie.backdropUrl} alt="" aria-hidden="true" /> : null}
        <div className="relative z-10">
          <span className="text-[0.78rem] font-[760] uppercase text-cinema-amber">{movie.genres?.slice(0, 2).join(" / ") || "Genre pending"}</span>
          <h2 className="my-[7px] text-[clamp(1.7rem,2.2vw,2.25rem)] leading-[1.03] text-cinema-text">{movie.title}</h2>
          <p className="m-0 text-cinema-soft">{movie.year ?? "Year pending"}</p>
        </div>
      </div>

      <div className="grid gap-[18px] p-[18px]">
        <div className="grid grid-cols-2 gap-2.5 max-[640px]:grid-cols-1">
          <MetricTile label="Rating" value={formatOptionalRating(movie.ratingMean)} tone="amber" />
          <MetricTile label="Revenue" value={formatOptionalMoney(movie.revenue)} tone="teal" />
        </div>

        <p className="m-0 text-[0.94rem] leading-[1.65] text-cinema-soft">{movie.overview || "Overview is waiting for the backend response."}</p>

        <div className="grid gap-[9px]">
          <span className="flex items-center gap-2 text-[0.86rem] text-cinema-soft">
            <Clock size={15} />
            {formatOptionalRuntime(movie.runtimeMinutes)}
          </span>
          <span className="flex items-center gap-2 text-[0.86rem] text-cinema-soft">
            <Flame size={15} />
            {typeof movie.tmdbPopularity === "number" ? `${movie.tmdbPopularity.toFixed(1)} popularity` : "Popularity pending"}
          </span>
          <span className="flex items-center gap-2 text-[0.86rem] text-cinema-soft">
            <DollarSign size={15} />
            {formatOptionalMoney(movie.budget)} budget
          </span>
          <span className="flex items-center gap-2 text-[0.86rem] text-cinema-soft">
            <Star size={15} />
            {movie.ratingCount ?? "Pending"} ratings
          </span>
        </div>

        <div className="flex flex-wrap gap-2" aria-label="Movie tags">
          {(movie.tags ?? []).map((tag) => (
            <span
              className="min-h-[30px] rounded-lg border border-[rgba(85,214,194,0.18)] bg-[rgba(85,214,194,0.07)] px-2.5 py-[7px] text-[0.78rem] text-cinema-teal"
              key={tag}
            >
              {tag}
            </span>
          ))}
          {(movie.tags ?? []).length === 0 ? (
            <span className="min-h-[30px] rounded-lg border border-[rgba(85,214,194,0.18)] bg-[rgba(85,214,194,0.07)] px-2.5 py-[7px] text-[0.78rem] text-cinema-teal">
              tags pending
            </span>
          ) : null}
        </div>

        <div className="grid gap-2">
          {onRecommend ? (
            <button className={primaryActionClass} type="button" onClick={() => onRecommend(movie)}>
              Recommend seed
              <ArrowRight size={16} />
            </button>
          ) : null}
          {onPredict ? (
            <button
              className="inline-flex min-h-11 items-center justify-center gap-[9px] rounded-lg border border-[rgba(85,214,194,0.3)] bg-[rgba(85,214,194,0.08)] px-4 font-[760] text-cinema-teal transition-[filter,transform,border-color,background] duration-[220ms] ease-linear hover:-translate-y-0.5 hover:border-[rgba(85,214,194,0.55)] hover:bg-[rgba(85,214,194,0.16)]"
              type="button"
              onClick={() => onPredict(movie)}
            >
              Predict revenue
              <TrendingUp size={16} />
            </button>
          ) : null}
        </div>
      </div>
    </aside>
  );
}
