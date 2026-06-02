import { Activity, BarChart3, CircleDot, Grid3X3, LineChart } from "lucide-react";
import { useState } from "react";
import { ConnectionNotice } from "../../shared/ui/ConnectionNotice";
import { SectionHeader } from "../../shared/ui/SectionHeader";
import { MetricTile } from "../../shared/ui/MetricTile";
import { BudgetTrendChart } from "./charts/BudgetTrendChart";
import { CorrelationMatrix } from "./charts/CorrelationMatrix";
import { GenreBars } from "./charts/GenreBars";
import { RevenueScatter } from "./charts/RevenueScatter";
import { useAtlasData } from "./useAtlasData";

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
    <section className="screen atlas-screen">
      <SectionHeader
        title="Atlas"
        description="A cinematic data surface for backend-provided revenue, budget, genre, and correlation series."
      />

      <div className="atlas-layout">
        <aside className="atlas-rail" aria-label="Visualization navigation">
          <div className="rail-header">
            <Activity size={18} />
            <div>
              <strong>Visual modules</strong>
              <span>Linear animated SVG</span>
            </div>
          </div>

          {atlasViews.map((view) => {
            const Icon = view.icon;
            return (
              <button
                className="atlas-nav-button"
                data-selected={activeView === view.id}
                key={view.id}
                type="button"
                onClick={() => setActiveView(view.id)}
              >
                <Icon size={16} />
                {view.label}
              </button>
            );
          })}
        </aside>

        <div className="atlas-canvas">
          <div className="atlas-metrics">
            <MetricTile label="Movies" value={data?.summary.movieCount?.toLocaleString("en-US") ?? "-"} tone="amber" />
            <MetricTile label="Ratings" value={data?.summary.ratingCount?.toLocaleString("en-US") ?? "-"} tone="teal" />
            <MetricTile label="Genres" value={data?.summary.genreCount ? `${data.summary.genreCount}` : "-"} tone="amber" />
          </div>

          <div className="chart-stage">
            {errorMessage ? (
              <ConnectionNotice
                title="等待可视化接口"
                message={errorMessage}
                actionHint="建议接口：/stats/summary、/stats/genres、/stats/budget-trend、/stats/revenue-budget、/stats/correlations。"
              />
            ) : null}
            {!errorMessage && isLoading ? <ConnectionNotice title="正在等待响应" message="正在请求后端可视化数据。" /> : null}
            {!errorMessage && !isLoading && !data ? (
              <ConnectionNotice title="暂无图表数据" message="接口返回空数据时会显示这里。" />
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
