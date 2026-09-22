from __future__ import annotations

from pathlib import Path
from typing import Sequence


def render_helicorder(samples: Sequence[Sequence[float]], outpath: str | Path, width: int = 1200, height: int = 800) -> str:
    """Render a minimal rolling helicorder preview as SVG.

    This intentionally stays lightweight so it can run on a Pi, even when the
    live stream is being updated in near real time. The output is an SVG file that
    an HTTP endpoint or browser can refresh periodically.
    """
    output_path = Path(outpath)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not samples:
        svg = "<svg xmlns='http://www.w3.org/2000/svg' width='{0}' height='{1}'></svg>".format(width, height)
        output_path.write_text(svg, encoding="utf-8")
        return str(output_path)

    max_x = max(len(row) for row in samples) if samples else 1
    max_y = max(max(abs(float(v)) for v in row) for row in samples) if samples else 1.0
    max_y = max(max_y, 1.0)

    rows = []
    for row_idx, row in enumerate(samples):
        y0 = (row_idx / max(1, len(samples))) * (height - 20) + 10
        points = []
        for col_idx, value in enumerate(row):
            x = (col_idx / max(1, max_x)) * (width - 20) + 10
            y = y0 - (float(value) / max_y) * 30
            points.append(f"{x:.2f},{y:.2f}")
        rows.append("<polyline fill='none' stroke='black' stroke-width='1' points='{}' />".format(" ".join(points)))

    svg = """
    <svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'>
      <rect width='100%' height='100%' fill='white' />
      {rows}
    </svg>
    """.format(width=width, height=height, rows="\n      ".join(rows))

    output_path.write_text(svg, encoding="utf-8")
    return str(output_path)
