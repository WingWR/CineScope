import { ArrowRight, Clock, DollarSign, Flame, Star } from "lucide-react";
import { formatOptionalMoney, formatOptionalRating, formatOptionalRuntime } from "../../entities/movie/formatters";
import type { Movie } from "../../entities/movie/types";
import { ConnectionNotice } from "../../shared/ui/ConnectionNotice";
import { MetricTile } from "../../shared/ui/MetricTile";

type MovieDetailPanelProps = {
  movie?: Movie;
  onRecommend: () => void;
};

export function MovieDetailPanel({ movie, onRecommend }: MovieDetailPanelProps) {
  if (!movie) {
    return (
      <aside className="movie-detail movie-detail--empty" aria-label="Movie details pending">
        <ConnectionNotice
          title="尚未收到电影详情"
          message="选择真实搜索结果后，这里会展示后端返回的电影详情、指标和推荐入口。"
          actionHint="建议详情字段：title/year/genres/overview/ratingMean/revenue/posterUrl/backdropUrl"
        />
      </aside>
    );
  }

  return (
    <aside className="movie-detail" aria-label={`${movie.title} details`}>
      <div className="movie-detail__hero">
        {movie.backdropUrl ? <img src={movie.backdropUrl} alt="" aria-hidden="true" /> : null}
        <div>
          <span>{movie.genres?.slice(0, 2).join(" / ") || "Genre pending"}</span>
          <h2>{movie.title}</h2>
          <p>{movie.year ?? "Year pending"}</p>
        </div>
      </div>

      <div className="movie-detail__body">
        <div className="movie-detail__stats">
          <MetricTile label="Rating" value={formatOptionalRating(movie.ratingMean)} tone="amber" />
          <MetricTile label="Revenue" value={formatOptionalMoney(movie.revenue)} tone="teal" />
        </div>

        <p className="movie-overview">{movie.overview || "简介等待后端返回。"}</p>

        <div className="fact-list">
          <span>
            <Clock size={15} />
            {formatOptionalRuntime(movie.runtimeMinutes)}
          </span>
          <span>
            <Flame size={15} />
            {typeof movie.tmdbPopularity === "number" ? `${movie.tmdbPopularity.toFixed(1)} popularity` : "热度待接口返回"}
          </span>
          <span>
            <DollarSign size={15} />
            {formatOptionalMoney(movie.budget)} budget
          </span>
          <span>
            <Star size={15} />
            {movie.ratingCount ?? "待接口返回"} ratings
          </span>
        </div>

        <div className="tag-cloud" aria-label="Movie tags">
          {(movie.tags ?? []).map((tag) => (
            <span key={tag}>{tag}</span>
          ))}
          {(movie.tags ?? []).length === 0 ? <span>tags pending</span> : null}
        </div>

        <button className="primary-action" type="button" onClick={onRecommend}>
          Recommended seed
          <ArrowRight size={16} />
        </button>
      </div>
    </aside>
  );
}
