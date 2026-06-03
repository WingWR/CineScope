import { ArrowUpRight, Gauge } from "lucide-react";
import { formatScore } from "../../../entities/movie/formatters";
import type { RecommendationItem } from "../../../entities/movie/types";
import { cx, panelClass } from "../../../shared/ui/classes";

type RecommendationCardProps = {
  item: RecommendationItem;
  index: number;
};

export function RecommendationCard({ item, index }: RecommendationCardProps) {
  return (
    <article
      className={cx(
        panelClass,
        "relative grid animate-card-in grid-cols-[76px_minmax(0,1fr)_auto_22px] items-center gap-3.5 p-3 transition-[border-color,transform] duration-[220ms] ease-linear hover:-translate-y-0.5 hover:border-[rgba(242,177,92,0.34)] max-[640px]:grid-cols-[64px_minmax(0,1fr)]",
      )}
      style={{ animationDelay: `${index * 42}ms` }}
    >
      {item.movie.posterUrl ? (
        <img className="h-28 w-[76px] rounded-lg object-cover max-[640px]:h-[94px] max-[640px]:w-16" src={item.movie.posterUrl} alt={`${item.movie.title} poster`} loading="lazy" />
      ) : (
        <span className="grid h-28 w-[76px] place-items-center rounded-lg border border-cinema-border bg-[radial-gradient(circle_at_72%_18%,rgba(242,177,92,0.2),transparent_28%),linear-gradient(160deg,rgba(85,214,194,0.16),rgba(242,177,92,0.12)),rgba(255,255,255,0.04)] p-[18px] text-center text-[0.72rem] font-[760] leading-[1.2] text-cinema-text max-[640px]:h-[94px] max-[640px]:w-16">
          {item.movie.title}
        </span>
      )}
      <div className="grid min-w-0 gap-2.5">
        <div>
          <h2 className="m-0 truncate text-[1.08rem] text-cinema-text">{item.movie.title}</h2>
          <p className="m-0 text-[0.86rem] leading-normal text-cinema-soft">
            {item.movie.year ?? "Year pending"} / {(item.movie.genres ?? []).slice(0, 3).join(" / ") || "Genres pending"}
          </p>
        </div>
        <p className="m-0 text-[0.86rem] leading-normal text-cinema-soft">{item.reason}</p>
      </div>
      <div className="grid min-w-[88px] justify-items-end gap-1 text-cinema-teal max-[640px]:hidden">
        <Gauge size={16} />
        <strong className="text-[1.16rem]">{formatScore(item.score)}</strong>
        <span className="text-[0.74rem] text-cinema-muted">{item.source}</span>
      </div>
      <ArrowUpRight className="text-cinema-muted max-[640px]:hidden" size={17} />
    </article>
  );
}
