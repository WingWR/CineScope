import { useMemo } from "react";
import type { BudgetTrendPoint } from "../../../entities/movie/types";
import { ConnectionNotice } from "../../../shared/ui/ConnectionNotice";
import { linePath, scaleLinear } from "./chartMath";

type BudgetTrendChartProps = {
  points: BudgetTrendPoint[];
};

export function BudgetTrendChart({ points }: BudgetTrendChartProps) {
  const path = useMemo(() => {
    if (points.length === 0) {
      return "";
    }

    const minYear = Math.min(...points.map((point) => point.year));
    const maxYear = Math.max(...points.map((point) => point.year));
    const maxBudget = Math.max(...points.map((point) => point.budget));
    const plotted = points.map((point) => ({
      x: scaleLinear(point.year, [minYear, maxYear], [70, 690]),
      y: scaleLinear(point.budget, [0, maxBudget], [370, 64]),
    }));
    return linePath(plotted);
  }, [points]);

  if (points.length === 0) {
    return <ConnectionNotice title="暂无预算趋势数据" message="后端返回 budget-trend 序列后，这里会渲染线性趋势图。" />;
  }

  return (
    <div className="chart-panel">
      <div className="chart-copy">
        <span>Yearly budget trend</span>
        <h2>Studio scale curve</h2>
        <p>A linear path animation turns the historical budget series into a readable first-glance motion.</p>
      </div>

      <svg className="chart-svg" viewBox="0 0 760 440" role="img" aria-label="Average budget by year line chart">
        <path className="chart-grid-line" d="M70 370H700" />
        <path className="chart-grid-line" d="M70 64V370" />
        {[1970, 1980, 1990, 2000, 2010, 2020].map((year, index) => (
          <g key={year}>
            <path className="chart-grid-line chart-grid-line--soft" d={`M${70 + index * 124} 64V370`} />
            <text className="axis-label" x={70 + index * 124} y="406" textAnchor="middle">
              {year}
            </text>
          </g>
        ))}
        <path className="trend-line trend-line--ghost" d={path} />
        <path className="trend-line" d={path} />
      </svg>
    </div>
  );
}
