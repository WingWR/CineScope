import type { CSSProperties } from "react";
import type { CorrelationCell } from "../../../../entities/movie/types";
import { ConnectionNotice } from "../../../../shared/ui/ConnectionNotice";
import { cx } from "../../../../shared/ui/classes";
import { chartBodyClass, chartCopyClass, chartKickerClass, chartTitleClass, compactChartPanelClass } from "./chartClasses";

type CorrelationMatrixProps = {
  cells: CorrelationCell[];
};

const labels = ["Budget", "Revenue", "Rating", "Popularity"];

export function CorrelationMatrix({ cells }: CorrelationMatrixProps) {
  if (cells.length === 0) {
    return (
      <ConnectionNotice
        title="No correlation data"
        message="The heatmap appears when the backend returns a correlations matrix."
      />
    );
  }

  return (
    <div className={compactChartPanelClass}>
      <div className={chartCopyClass}>
        <span className={chartKickerClass}>Correlation</span>
        <h2 className={chartTitleClass}>Signal heatmap</h2>
        <p className={chartBodyClass}>Prepared for model diagnostics, feature exploration, and later backend-computed correlation matrices.</p>
      </div>

      <div className="grid grid-cols-[92px_repeat(4,minmax(76px,1fr))] items-stretch gap-2 max-[640px]:min-w-[620px]" role="img" aria-label="Correlation heatmap">
        <span />
        {labels.map((label) => (
          <strong className="grid min-h-[42px] place-items-center text-[0.78rem] text-cinema-soft" key={label}>
            {label}
          </strong>
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
      <strong className="grid min-h-[42px] place-items-center text-[0.78rem] text-cinema-soft">{row}</strong>
      {labels.map((column) => {
        const cell =
          cells.find((item) => item.x === column && item.y === row) ??
          cells.find((item) => item.x === row && item.y === column);
        const value = row === column ? 1 : cell?.value ?? 0;

        return (
          <span
            className={cx(
              "grid min-h-[62px] animate-dot-in place-items-center rounded-lg border border-[rgba(244,239,228,0.1)] bg-[rgba(255,255,255,0.045)] font-[720] text-cinema-text",
              value > 0.6 && "border-[rgba(242,177,92,0.38)]",
            )}
            data-strong={value > 0.6}
            key={`${row}-${column}`}
            style={
              {
                background: `linear-gradient(135deg, rgba(242, 177, 92, ${value * 0.44}), rgba(85, 214, 194, ${
                  value * 0.28
                })), rgba(255, 255, 255, 0.045)`,
              } as CSSProperties
            }
          >
            {value.toFixed(2)}
          </span>
        );
      })}
    </>
  );
}
