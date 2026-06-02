import { useMemo, useState } from "react";
import type { CSSProperties } from "react";
import type { RevenueBudgetPoint } from "../../../entities/movie/types";
import { ConnectionNotice } from "../../../shared/ui/ConnectionNotice";
import { scaleLinear } from "./chartMath";

type RevenueScatterProps = {
  points: RevenueBudgetPoint[];
};

export function RevenueScatter({ points }: RevenueScatterProps) {
  const [activeTitle, setActiveTitle] = useState(points[0]?.title ?? "");
  const activePoint = points.find((point) => point.title === activeTitle) ?? points[0];

  if (points.length === 0) {
    return <ConnectionNotice title="暂无收入预算数据" message="后端返回 revenue-budget 序列后，这里会渲染气泡图。" />;
  }

  const plotted = useMemo(() => {
    const maxBudget = Math.max(...points.map((point) => point.budget));
    const maxRevenue = Math.max(...points.map((point) => point.revenue));

    return points.map((point) => ({
      ...point,
      x: scaleLinear(point.budget, [0, maxBudget], [64, 680]),
      y: scaleLinear(point.revenue, [0, maxRevenue], [384, 54]),
      r: scaleLinear(point.popularity ?? 50, [0, 100], [7, 22]),
    }));
  }, [points]);

  return (
    <div className="chart-panel">
      <div className="chart-copy">
        <span>Revenue vs Budget</span>
        <h2>{activePoint?.title ?? "Revenue map"}</h2>
        <p>
          Bubble size reflects popularity. The map is intentionally local and can later consume backend chart series
          without changing the component contract.
        </p>
      </div>

      <svg className="chart-svg" viewBox="0 0 760 440" role="img" aria-label="Revenue and budget scatter chart">
        <path className="chart-grid-line" d="M64 384H704" />
        <path className="chart-grid-line" d="M64 54V384" />
        {[0, 1, 2, 3].map((item) => (
          <path key={item} className="chart-grid-line chart-grid-line--soft" d={`M64 ${92 + item * 82}H704`} />
        ))}
        {plotted.map((point, index) => (
          <g key={point.title}>
            <circle
              className="scatter-dot"
              data-active={point.title === activeTitle}
              cx={point.x}
              cy={point.y}
              r={point.r}
              style={{ "--stagger": `${index * 56}ms` } as CSSProperties}
              onMouseEnter={() => setActiveTitle(point.title)}
            />
            {point.title === activeTitle ? (
              <text className="chart-label" x={point.x + point.r + 8} y={point.y + 4}>
                {point.title}
              </text>
            ) : null}
          </g>
        ))}
        <text className="axis-label" x="650" y="420">
          budget
        </text>
        <text className="axis-label" x="18" y="70">
          revenue
        </text>
      </svg>
    </div>
  );
}
