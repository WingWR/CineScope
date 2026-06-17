import { Activity, BarChart3, CircleDot, Grid3X3, LineChart } from "lucide-react";
import { useState } from "react";
import { ConnectionNotice } from "../../shared/ui/ConnectionNotice";
import { MetricTile } from "../../shared/ui/MetricTile";
import { SectionHeader } from "../../shared/ui/SectionHeader";
import { cx, panelClass, screenClass } from "../../shared/ui/classes";
import { BudgetTrendChart } from "./components/charts/BudgetTrendChart";
import { CorrelationMatrix } from "./components/charts/CorrelationMatrix";
import { GenreBars } from "./components/charts/GenreBars";
import { RevenueScatter } from "./components/charts/RevenueScatter";
import { useAtlasData } from "./hooks/useAtlasData";

type AtlasView = "scatter" | "trend" | "genres" | "correlation";

const atlasViews: Array<{ id: AtlasView; label: string; icon: typeof CircleDot }> = [
  { id: "scatter", label: "Revenue map", icon: CircleDot },
  { id: "trend", label: "Budget curve", icon: LineChart },
  { id: "genres", label: "Genre volume", icon: BarChart3 },
  { id: "correlation", label: "Correlation", icon: Grid3X3 },
];

export function VisualizationPage() {
  const { data, isLoading, errorMessage } = useAtlasData();
  const [activeView, setActiveView] = useState<AtlasView>("scatter");

  return (
    <section className={screenClass}>
      <SectionHeader
        title="Atlas"
        description="A cinematic data surface for backend-provided revenue, budget, genre, and correlation series."
      />

      <div className="grid grid-cols-[250px_minmax(0,1fr)] items-start gap-[18px] max-[900px]:grid-cols-1">
        <aside className={cx(panelClass, "sticky top-24 grid gap-4 p-[18px] max-[900px]:static")} aria-label="Visualization navigation">
          <div className="flex items-start gap-[9px] font-bold text-cinema-text">
            <Activity size={18} />
            <div className="grid gap-[3px]">
              <strong className="text-cinema-text">Visual modules</strong>
              <span className="text-[0.78rem] font-[760] uppercase text-cinema-amber">Linear animated SVG</span>
            </div>
          </div>

          {atlasViews.map((view) => {
            const Icon = view.icon;
            return (
              <button
                className={cx(
                  "inline-flex min-h-9 w-full items-center justify-start gap-2 rounded-lg border border-[rgba(244,239,228,0.14)] bg-[rgba(255,255,255,0.04)] px-3 text-[0.9rem] text-cinema-soft transition-[background,color,border-color,box-shadow,transform] duration-[220ms] ease-linear hover:border-[rgba(190,132,54,0.62)] hover:bg-[rgba(255,255,255,0.08)] hover:text-cinema-text",
                  activeView === view.id &&
                    "border-[rgba(190,132,54,0.9)] bg-[rgba(190,132,54,0.24)] text-cinema-amber-strong shadow-[0_0_0_1px_rgba(190,132,54,0.28),0_10px_26px_rgba(190,132,54,0.14)] hover:text-cinema-amber-strong",
                )}
                data-selected={activeView === view.id}
                aria-current={activeView === view.id ? "page" : undefined}
                key={view.id}
                type="button"
                onClick={() => setActiveView(view.id)}
              >
                <Icon size={16} />
                <span className="min-w-0 flex-1 text-left">{view.label}</span>
              </button>
            );
          })}
        </aside>

        <div className="grid min-w-0 gap-4">
          <div className="grid grid-cols-3 gap-3 max-[640px]:grid-cols-1">
            <MetricTile label="Movies" value={data?.summary.movieCount?.toLocaleString("en-US") ?? "-"} tone="amber" />
            <MetricTile label="Ratings" value={data?.summary.ratingCount?.toLocaleString("en-US") ?? "-"} tone="teal" />
            <MetricTile label="Genres" value={data?.summary.genreCount ? `${data.summary.genreCount}` : "-"} tone="amber" />
          </div>

          <div className={cx(panelClass, "min-h-[620px] overflow-hidden p-[clamp(16px,2vw,24px)] max-[640px]:min-h-[520px] max-[640px]:overflow-x-auto")}>
            {errorMessage ? (
              <ConnectionNotice
                title="Waiting for visualization API"
                message={errorMessage}
                actionHint="Suggested endpoints: /stats/summary, /stats/genres, /stats/budget-trend, /stats/revenue-budget, /stats/correlations."
              />
            ) : null}
            {!errorMessage && isLoading ? (
              <ConnectionNotice title="Waiting for response" message="Requesting backend visualization data." />
            ) : null}
            {!errorMessage && !isLoading && !data ? (
              <ConnectionNotice title="No chart data" message="This appears when the API returns no visualization payload." />
            ) : null}
            {data && activeView === "scatter" ? <RevenueScatter points={data.points} /> : null}
            {data && activeView === "trend" ? <BudgetTrendChart points={data.trend} /> : null}
            {data && activeView === "genres" ? <GenreBars genres={data.genres} /> : null}
            {data && activeView === "correlation" ? <CorrelationMatrix cells={data.correlations} /> : null}
          </div>
        </div>
      </div>
    </section>
  );
}
