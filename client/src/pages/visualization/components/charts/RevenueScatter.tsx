import { useMemo, useState } from "react";
import type { CSSProperties } from "react";
import type { RevenueBudgetPoint } from "../../../../entities/movie/types";
import { ConnectionNotice } from "../../../../shared/ui/ConnectionNotice";
import { cx } from "../../../../shared/ui/classes";
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
} from "./chartClasses";
import { scaleLinear } from "./chartMath";

type RevenueScatterProps = {
  points: RevenueBudgetPoint[];
};

export function RevenueScatter({ points }: RevenueScatterProps) {
  const [activeTitle, setActiveTitle] = useState(points[0]?.title ?? "");
  const activePoint = points.find((point) => point.title === activeTitle) ?? points[0];

  const plotted = useMemo(() => {
    if (points.length === 0) {
      return [];
    }

    const maxBudget = Math.max(...points.map((point) => point.budget));
    const maxRevenue = Math.max(...points.map((point) => point.revenue));

    return points.map((point) => ({
      ...point,
      x: scaleLinear(point.budget, [0, maxBudget], [64, 680]),
      y: scaleLinear(point.revenue, [0, maxRevenue], [384, 54]),
      r: scaleLinear(point.popularity ?? 50, [0, 100], [7, 22]),
    }));
  }, [points]);

  if (points.length === 0) {
    return (
      <ConnectionNotice
        title="No revenue-budget data"
        message="The scatter chart appears when the backend returns a revenue-budget series."
      />
    );
  }

  return (
    <div className={chartPanelClass}>
      <div className={chartCopyClass}>
        <span className={chartKickerClass}>Revenue vs Budget</span>
        <h2 className={chartTitleClass}>{activePoint?.title ?? "Revenue map"}</h2>
        <p className={chartBodyClass}>
          Bubble size reflects popularity. The map can consume backend chart series without changing the component
          contract.
        </p>
      </div>

      <svg className={chartSvgClass} viewBox="0 0 760 440" role="img" aria-label="Revenue and budget scatter chart">
        <path className={chartGridLineClass} d="M64 384H704" />
        <path className={chartGridLineClass} d="M64 54V384" />
        {[0, 1, 2, 3].map((item) => (
          <path key={item} className={chartSoftGridLineClass} d={`M64 ${92 + item * 82}H704`} />
        ))}
        {plotted.map((point, index) => (
          <g key={point.title}>
            <circle
              className={cx(
                "origin-center animate-dot-in fill-[rgba(85,214,194,0.42)] stroke-[rgba(244,239,228,0.78)] transition-[fill,r] duration-[220ms] ease-linear [stroke-width:1]",
                point.title === activeTitle && "fill-[rgba(242,177,92,0.82)]",
              )}
              data-active={point.title === activeTitle}
              cx={point.x}
              cy={point.y}
              r={point.r}
              style={{ animationDelay: `${index * 56}ms` } as CSSProperties}
              onMouseEnter={() => setActiveTitle(point.title)}
            />
          </g>
        ))}
        <text className={chartLabelClass} x="650" y="420">
          budget
        </text>
        <text className={chartLabelClass} x="18" y="70">
          revenue
        </text>
      </svg>
    </div>
  );
}
