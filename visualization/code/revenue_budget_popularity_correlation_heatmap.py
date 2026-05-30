from __future__ import annotations

import math

from common_svg import GRAPH_DIR, as_float, as_year, diverging_color, esc, load_movies, write_svg


OUTPUT = GRAPH_DIR / "revenue_budget_popularity_correlation_heatmap.svg"

COLUMN_SPECS = [
    ("revenue", lambda row: _positive_log(row, "revenue")),
    ("budget", lambda row: _positive_log(row, "budget")),
    ("tmdb_popularity", lambda row: _non_negative_log1p(row, "tmdb_popularity")),
    ("movie_year", lambda row: as_year(row)),
    ("rating_count", lambda row: _non_negative_log1p(row, "rating_count")),
    ("rating_median", lambda row: as_float(row, "rating_median")),
    ("runtime_minutes", lambda row: _positive_raw(row, "runtime_minutes")),
]


def pearson(xs: list[float], ys: list[float]) -> float:
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    x_denominator = math.sqrt(sum((x - x_mean) ** 2 for x in xs))
    y_denominator = math.sqrt(sum((y - y_mean) ** 2 for y in ys))
    if x_denominator == 0 or y_denominator == 0:
        return 0.0
    return numerator / (x_denominator * y_denominator)


def main() -> None:
    values_by_column = {name: [] for name, _ in COLUMN_SPECS}
    row_count = 0

    for row in load_movies():
        transformed = [(name, transform(row)) for name, transform in COLUMN_SPECS]
        if any(value is None for _, value in transformed):
            continue
        for name, value in transformed:
            values_by_column[name].append(float(value))
        row_count += 1

    series = [(name, values_by_column[name]) for name, _ in COLUMN_SPECS]

    matrix = [[pearson(left[1], right[1]) for right in series] for left in series]

    width, height = 1120, 940
    cell = 95
    start_x, start_y = 250, 200
    elements = [
        '<rect width="100%" height="100%" fill="#fbfcff"/>',
        '<text class="title" x="60" y="54">revenue, budget, popularity and metadata correlation</text>',
    ]

    for i, (label, _) in enumerate(series):
        x = start_x + i * cell + cell / 2
        y = start_y - 18
        elements.append(
            f'<text class="label" text-anchor="end" transform="translate({x:.2f} {y:.2f}) rotate(-35)">{esc(label)}</text>'
        )
        elements.append(
            f'<text class="label" text-anchor="end" x="{start_x - 18}" y="{start_y + i * cell + cell / 2 + 5}">{esc(label)}</text>'
        )

    for row_index, row in enumerate(matrix):
        for col_index, value in enumerate(row):
            x = start_x + col_index * cell
            y = start_y + row_index * cell
            color = diverging_color(value)
            text_color = "#ffffff" if abs(value) > 0.65 else "#243044"
            elements.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{color}" stroke="#ffffff" stroke-width="3"/>'
            )
            elements.append(
                f'<text text-anchor="middle" x="{x + cell / 2}" y="{y + cell / 2 + 7}" '
                f'font-size="22" font-weight="700" style="fill: {text_color}">{value:.2f}</text>'
            )

    legend_x, legend_y = 250, 870
    legend_w, legend_h = 360, 18
    for index in range(120):
        value = -1 + 2 * index / 119
        color = diverging_color(value)
        x = legend_x + index * legend_w / 120
        elements.append(
            f'<rect x="{x:.2f}" y="{legend_y}" width="{legend_w / 120 + 0.5:.2f}" height="{legend_h}" fill="{color}"/>'
        )

    elements.extend(
        [
            f'<text class="tick" text-anchor="middle" x="{legend_x}" y="{legend_y + 42}">-1</text>',
            f'<text class="tick" text-anchor="middle" x="{legend_x + legend_w / 2}" y="{legend_y + 42}">0</text>',
            f'<text class="tick" text-anchor="middle" x="{legend_x + legend_w}" y="{legend_y + 42}">1</text>',
            f'<text class="note" x="{legend_x + legend_w + 26}" y="{legend_y + 14}">negative to positive correlation</text>',
        ]
    )

    write_svg(OUTPUT, width, height, elements)
    print(f"Saved {OUTPUT}")


def _positive_log(row: dict[str, str], key: str) -> float | None:
    value = as_float(row, key)
    if value is None or value <= 0:
        return None
    return math.log10(value)


def _non_negative_log1p(row: dict[str, str], key: str) -> float | None:
    value = as_float(row, key)
    if value is None or value < 0:
        return None
    return math.log10(value + 1)


def _positive_raw(row: dict[str, str], key: str) -> float | None:
    value = as_float(row, key)
    if value is None or value <= 0:
        return None
    return value


if __name__ == "__main__":
    main()
