from __future__ import annotations

from common_svg import (
    GRAPH_DIR,
    as_float,
    color_lerp,
    esc,
    format_money,
    load_movies,
    nice_linear_ticks,
    scale_linear,
    write_svg,
)


OUTPUT = GRAPH_DIR / "language_revenue_tower.svg"

PALETTE = [
    "#f2a3b3",
    "#e2a154",
    "#c9bc5b",
    "#91bd5a",
    "#68c2ad",
    "#59b5b0",
    "#9eb7e8",
    "#c995d9",
    "#c881c3",
    "#e58ac4",
]


def main() -> None:
    groups: dict[str, list[float]] = {}
    for row in load_movies():
        language = (row.get("original_language") or "unknown").strip() or "unknown"
        revenue = as_float(row, "revenue")
        if revenue and revenue > 0:
            groups.setdefault(language, []).append(revenue)

    languages = [language for language, _ in sorted(groups.items(), key=lambda item: len(item[1]), reverse=True)[:10]]
    stats = [
        {
            "language": language,
            "values": sorted(groups[language]),
            "count": len(groups[language]),
        }
        for language in languages
    ]

    max_revenue = max(max(item["values"]) for item in stats)
    y_max = max_revenue * 1.04
    y_min = -max_revenue * 0.12

    bin_count = 24
    bin_size = y_max / bin_count
    max_bin_count = 1
    for item in stats:
        counts = [0 for _ in range(bin_count)]
        for revenue in item["values"]:
            index = min(bin_count - 1, int(revenue / bin_size))
            counts[index] += 1
        item["counts"] = counts
        max_bin_count = max(max_bin_count, max(counts))

    width, height = 1280, 860
    left, right, top, bottom = 90, 70, 85, 130
    plot_w = width - left - right
    plot_h = height - top - bottom
    slot_w = plot_w / len(stats)
    max_tower_w = slot_w * 0.72

    def y_pos(value: float) -> float:
        return scale_linear(value, y_min, y_max, top + plot_h, top)

    elements = [
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text class="title" x="305" y="42">Revenue by original_language movies</text>',
        f'<line class="axis" x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}"/>',
        f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}"/>',
        f'<line x1="{left}" y1="{y_pos(0):.2f}" x2="{left + plot_w}" y2="{y_pos(0):.2f}" stroke="#777777" stroke-width="1"/>',
    ]

    for tick in nice_linear_ticks(y_max, count=8):
        y = y_pos(tick)
        elements.append(f'<line class="grid" x1="{left}" y1="{y:.2f}" x2="{left + plot_w}" y2="{y:.2f}"/>')
        elements.append(f'<text class="tick" text-anchor="end" x="{left - 12}" y="{y + 4:.2f}">{esc(format_money(tick))}</text>')

    negative_tick = -max_revenue * 0.1
    y = y_pos(negative_tick)
    elements.append(f'<text class="tick" text-anchor="end" x="{left - 12}" y="{y + 4:.2f}">{esc(format_money(negative_tick))}</text>')

    for lang_index, item in enumerate(stats):
        center_x = left + slot_w * lang_index + slot_w / 2
        color = PALETTE[lang_index % len(PALETTE)]
        for bin_index, count in enumerate(item["counts"]):
            if count == 0:
                continue
            low = bin_index * bin_size
            high = (bin_index + 1) * bin_size
            y_high = y_pos(high)
            y_low = y_pos(low)
            height_px = max(2.0, y_low - y_high)
            width_px = max(5.0, max_tower_w * (count / max_bin_count) ** 0.55)
            x = center_x - width_px / 2
            shade = color_lerp("#ffffff", color, 0.5 + 0.5 * (count / max_bin_count) ** 0.45)
            elements.append(
                f'<rect x="{x:.2f}" y="{y_high:.2f}" width="{width_px:.2f}" height="{height_px:.2f}" '
                f'fill="{shade}" fill-opacity="0.88" stroke="#252525" stroke-width="0.8"/>'
            )

        _add_outliers(elements, item["values"], center_x, y_pos, color)
        elements.append(
            f'<text class="label" text-anchor="middle" transform="translate({center_x:.2f} {top + plot_h + 32}) rotate(-35)">{esc(item["language"])}</text>'
        )

    elements.extend(
        [
            f'<text class="label" text-anchor="middle" x="{left + plot_w / 2}" y="{height - 28}">Original language</text>',
            f'<text class="label" transform="translate(34 {top + plot_h / 2}) rotate(-90)" text-anchor="middle">Revenue</text>',
        ]
    )

    write_svg(OUTPUT, width, height, elements)
    print(f"Saved {OUTPUT}")


def _add_outliers(elements: list[str], values: list[float], center_x: float, y_pos, color: str) -> None:
    if len(values) < 8:
        return
    q95 = _quantile(values, 0.95)
    outliers = [value for value in values if value > q95]
    if len(outliers) > 24:
        outliers = outliers[-24:]
    for index, value in enumerate(outliers):
        jitter = ((index % 5) - 2) * 1.6
        x = center_x + jitter
        y = y_pos(value)
        elements.append(
            f'<path d="M {x:.2f} {y - 3:.2f} L {x + 3:.2f} {y:.2f} L {x:.2f} {y + 3:.2f} L {x - 3:.2f} {y:.2f} Z" '
            f'fill="{color}" fill-opacity="0.88" stroke="#252525" stroke-width="0.8"/>'
        )


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    position = (len(values) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)
    fraction = position - lower
    return values[lower] * (1 - fraction) + values[upper] * fraction


if __name__ == "__main__":
    main()
