from __future__ import annotations


def render_kpi_card(title: str, value: str, subtitle: str = "", tone: str = "neutral") -> str:
    return (
        f'<section class="kpi-card kpi-card--{tone}">'
        f'<div class="kpi-card__title">{title}</div>'
        f'<div class="kpi-card__value">{value}</div>'
        f'<div class="kpi-card__subtitle">{subtitle}</div>'
        f"</section>"
    )
