import type { CSSProperties } from "react";
import type { GenreDistributionItem } from "../../../../entities/movie/types";
import { ConnectionNotice } from "../../../../shared/ui/ConnectionNotice";

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
    <div className="chart-panel chart-panel--bars">
      <div className="chart-copy">
        <span>Genre volume</span>
        <h2>{genres[0]?.genre ?? "Genres"} leads the library</h2>
        <p>Bars use transform-based linear entry, keeping the chart readable on smaller screens.</p>
      </div>

      <div className="bar-chart" role="img" aria-label="Genre distribution bar chart">
        {genres.map((item, index) => (
          <div className="bar-row" key={item.genre} style={{ "--stagger": `${index * 42}ms` } as CSSProperties}>
            <span>{item.genre}</span>
            <div>
              <i style={{ inlineSize: `${(item.count / max) * 100}%` }} />
            </div>
            <strong>{item.count.toLocaleString("en-US")}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}
