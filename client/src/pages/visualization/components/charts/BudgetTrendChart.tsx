import { useMemo } from "react";
import type { BudgetTrendPoint } from "../../../../entities/movie/types";
import { ConnectionNotice } from "../../../../shared/ui/ConnectionNotice";
import {
  chartBodyClass,
  chartCopyClass,
  chartGridLineClass,
  chartKickerClass,
  chartLabelClass,
  chartPanelClass,
  chartSoftGridLineClass,
  chartSvgClass,
  chartTitleClass,
  trendLineClass,
} from "./chartClasses";
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
    return (
      <ConnectionNotice
        title="No budget trend data"
        message="The budget-trend chart appears when the backend returns a budget series."
      />
    );
  }

  return (
    <div className={chartPanelClass}>
      <div className={chartCopyClass}>
        <span className={chartKickerClass}>Yearly budget trend</span>
        <h2 className={chartTitleClass}>Studio scale curve</h2>
        <p className={chartBodyClass}>A linear path animation turns the historical budget series into a readable first-glance motion.</p>
      </div>

      <svg className={chartSvgClass} viewBox="0 0 760 440" role="img" aria-label="Average budget by year line chart">
        <path className={chartGridLineClass} d="M70 370H700" />
        <path className={chartGridLineClass} d="M70 64V370" />
        {[1970, 1980, 1990, 2000, 2010, 2020].map((year, index) => (
          <g key={year}>
            <path className={chartSoftGridLineClass} d={`M${70 + index * 124} 64V370`} />
            <text className={chartLabelClass} x={70 + index * 124} y="406" textAnchor="middle">
              {year}
            </text>
          </g>
        ))}
        <path className="animate-draw-line fill-none stroke-[rgba(85,214,194,0.2)] [stroke-dasharray:1000] [stroke-dashoffset:1000] [stroke-linecap:round] [stroke-linejoin:round] [stroke-width:12]" d={path} />
        <path className={trendLineClass} d={path} />
      </svg>
    </div>
  );
}
