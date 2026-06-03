import type { CSSProperties } from "react";
import type { GenreDistributionItem } from "../../../../entities/movie/types";
import { ConnectionNotice } from "../../../../shared/ui/ConnectionNotice";
import { chartBodyClass, chartCopyClass, chartKickerClass, chartTitleClass, compactChartPanelClass } from "./chartClasses";

type GenreBarsProps = {
  genres: GenreDistributionItem[];
};

export function GenreBars({ genres }: GenreBarsProps) {
  if (genres.length === 0) {
    return (
      <ConnectionNotice
        title="No genre distribution data"
        message="The genre bar chart appears when the backend returns a genres series."
      />
    );
  }

  const max = Math.max(...genres.map((item) => item.count));

  return (
    <div className={compactChartPanelClass}>
      <div className={chartCopyClass}>
        <span className={chartKickerClass}>Genre volume</span>
        <h2 className={chartTitleClass}>{genres[0]?.genre ?? "Genres"} leads the library</h2>
        <p className={chartBodyClass}>Bars use transform-based linear entry, keeping the chart readable on smaller screens.</p>
      </div>

      <div className="grid gap-[13px] max-[640px]:min-w-[620px]" role="img" aria-label="Genre distribution bar chart">
        {genres.map((item, index) => (
          <div
            className="grid animate-card-in grid-cols-[104px_minmax(0,1fr)_58px] items-center gap-3"
            key={item.genre}
            style={{ animationDelay: `${index * 42}ms` } as CSSProperties}
          >
            <span className="text-[0.84rem] text-cinema-soft">{item.genre}</span>
            <div className="h-3 overflow-hidden rounded-full bg-[rgba(255,255,255,0.07)]">
              <i
                className="block h-full origin-left animate-bar-grow rounded-[inherit] bg-gradient-to-r from-cinema-amber to-cinema-teal"
                style={{ inlineSize: `${(item.count / max) * 100}%` }}
              />
            </div>
            <strong className="text-[0.84rem] text-cinema-soft">{item.count.toLocaleString("en-US")}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}
