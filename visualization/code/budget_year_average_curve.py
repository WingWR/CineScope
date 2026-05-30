from __future__ import annotations

import math
from statistics import mean

from common_svg import (
    GRAPH_DIR,
    as_float,
    as_year,
    esc,
    format_money,
    load_movies,
    nice_linear_ticks,
    scale_linear,
    write_svg,
)


OUTPUT = GRAPH_DIR / "budget_year_average_curve.svg"


def main() -> None:
    by_year: dict[int, list[float]] = {}
    for row in load_movies():
        year = as_year(row)
        budget = as_float(row, "budget")
        if year is not None and budget and budget > 0:
            by_year.setdefault(year, []).append(budget)

    annual = [
        {
            "movie_year": year,
            "average_budget": mean(values),
            "count": len(values),
        }
        for year, values in sorted(by_year.items())
    ]
    min_year = min(item["movie_year"] for item in annual)
    max_year = max(item["movie_year"] for item in annual)

    smooth = []
    sigma = 2.8
    for year in range(min_year, max_year + 1):
        weighted_sum = 0.0
        weight_total = 0.0
        for item in annual:
            distance = year - item["movie_year"]
            weight = math.exp(-0.5 * (distance / sigma) ** 2) * math.sqrt(item["count"])
            weighted_sum += item["average_budget"] * weight
            weight_total += weight
        if weight_total > 0:
            smooth.append({"movie_year": year, "average_budget": weighted_sum / weight_total})

    width, height = 1240, 780
    left, right, top, bottom = 95, 80, 105, 95
    plot_w = width - left - right
    plot_h = height - top - bottom
    max_budget = max(
        max(item["average_budget"] for item in annual),
        max(item["average_budget"] for item in smooth),
    )
    y_max = max_budget * 1.08

    def x_pos(year: int) -> float:
        return scale_linear(year, min_year, max_year, left, left + plot_w)

    def y_pos(value: float) -> float:
        return scale_linear(value, 0, y_max, top + plot_h, top)

    elements = [
        '<rect width="100%" height="100%" fill="#fbfcff"/>',
        '<text class="title" x="60" y="54">movie_year vs average budget</text>',
        f'<line class="axis" x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}"/>',
        f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}"/>',
    ]

    decade_start = (min_year // 10) * 10
    for year in range(decade_start, max_year + 1, 10):
        if year < min_year:
            continue
        x = x_pos(year)
        elements.append(f'<line class="grid" x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{top + plot_h}"/>')
        elements.append(f'<text class="tick" text-anchor="middle" x="{x:.2f}" y="{top + plot_h + 25}">{year}</text>')

    for tick in nice_linear_ticks(y_max):
        y = y_pos(tick)
        elements.append(f'<line class="grid" x1="{left}" y1="{y:.2f}" x2="{left + plot_w}" y2="{y:.2f}"/>')
        elements.append(f'<text class="tick" text-anchor="end" x="{left - 12}" y="{y + 4:.2f}">{esc(format_money(tick))}</text>')

    raw_path = " ".join(
        f"{'M' if index == 0 else 'L'} {x_pos(item['movie_year']):.2f} {y_pos(item['average_budget']):.2f}"
        for index, item in enumerate(annual)
    )
    elements.append(f'<path d="{raw_path}" fill="none" stroke="#b8c2d0" stroke-width="1.4" stroke-opacity="0.55"/>')

    smooth_points = [
        (x_pos(item["movie_year"]), y_pos(item["average_budget"]))
        for item in smooth
    ]
    elements.append(
        f'<path d="{_smooth_path(smooth_points)}" fill="none" stroke="#4e79a7" stroke-width="4" stroke-linecap="round"/>'
    )

    for item in annual:
        radius = 2.0 + min(4.0, math.sqrt(item["count"]) * 0.25)
        elements.append(
            f'<circle cx="{x_pos(item["movie_year"]):.2f}" cy="{y_pos(item["average_budget"]):.2f}" '
            f'r="{radius:.2f}" fill="#4e79a7" fill-opacity="0.42" stroke="#ffffff" stroke-width="0.7"/>'
        )

    elements.extend(
        [
            f'<text class="label" text-anchor="middle" x="{left + plot_w / 2}" y="{height - 34}">movie_year</text>',
            f'<text class="label" transform="translate(34 {top + plot_h / 2}) rotate(-90)" text-anchor="middle">average budget</text>',
        ]
    )

    write_svg(OUTPUT, width, height, elements)
    print(f"Saved {OUTPUT}")


def _smooth_path(points: list[tuple[float, float]]) -> str:
    if not points:
        return ""
    if len(points) == 1:
        x, y = points[0]
        return f"M {x:.2f} {y:.2f}"

    commands = [f"M {points[0][0]:.2f} {points[0][1]:.2f}"]
    for index in range(len(points) - 1):
        p0 = points[index - 1] if index > 0 else points[index]
        p1 = points[index]
        p2 = points[index + 1]
        p3 = points[index + 2] if index + 2 < len(points) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        commands.append(
            f"C {c1[0]:.2f} {c1[1]:.2f}, {c2[0]:.2f} {c2[1]:.2f}, {p2[0]:.2f} {p2[1]:.2f}"
        )
    return " ".join(commands)


if __name__ == "__main__":
    main()
