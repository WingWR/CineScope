import type { CSSProperties } from "react";
import type { CorrelationCell } from "../../../entities/movie/types";
import { ConnectionNotice } from "../../../shared/ui/ConnectionNotice";

type CorrelationMatrixProps = {
  cells: CorrelationCell[];
};

const labels = ["Budget", "Revenue", "Rating", "Popularity"];

export function CorrelationMatrix({ cells }: CorrelationMatrixProps) {
  if (cells.length === 0) {
    return <ConnectionNotice title="暂无相关性数据" message="后端返回 correlations 矩阵后，这里会渲染热力图。" />;
  }

  return (
    <div className="chart-panel chart-panel--matrix">
      <div className="chart-copy">
        <span>Correlation</span>
        <h2>Signal heatmap</h2>
        <p>Prepared for model diagnostics, feature exploration, and later backend-computed correlation matrices.</p>
      </div>

      <div className="matrix-grid" role="img" aria-label="Correlation heatmap">
        <span />
        {labels.map((label) => (
          <strong key={label}>{label}</strong>
        ))}
        {labels.map((row) => (
          <MatrixRow cells={cells} row={row} key={row} />
        ))}
      </div>
    </div>
  );
}

type MatrixRowProps = {
  cells: CorrelationCell[];
  row: string;
};

function MatrixRow({ cells, row }: MatrixRowProps) {
  return (
    <>
      <strong>{row}</strong>
      {labels.map((column) => {
        const cell =
          cells.find((item) => item.x === column && item.y === row) ??
          cells.find((item) => item.x === row && item.y === column);
        const value = row === column ? 1 : cell?.value ?? 0;

        return (
          <span
            className="matrix-cell"
            data-strong={value > 0.6}
            key={`${row}-${column}`}
            style={{ "--value": value } as CSSProperties}
          >
            {value.toFixed(2)}
          </span>
        );
      })}
    </>
  );
}
