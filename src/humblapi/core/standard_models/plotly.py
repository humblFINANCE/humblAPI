"""
Standard Plotly models used across the humblAPI.

This module contains shared Pydantic models for Plotly chart components.
"""

from typing import Any

from pydantic import BaseModel


class PlotlyMarker(BaseModel):
    """Represents the marker properties for a Plotly trace."""

    color: list[int]
    colorscale: list[list[Any]]
    showscale: bool
    size: int


class PlotlyLine(BaseModel):
    """Represents the line properties for a Plotly trace."""

    color: str
    width: int | None = None
    shape: str | None = "linear"
    smoothing: float | None = 0.0


class PlotlyTrace(BaseModel):
    """Represents a single trace in a Plotly chart."""

    hovertemplate: str | None = "%{x}<br>%{y:.2f} USD<br><extra>%{text}</extra>"
    line: PlotlyLine
    marker: PlotlyMarker | None = None
    mode: str = "lines"  # Default to 'lines' mode if not specified
    name: str
    text: list[str] | None = None
    textfont: dict[str, Any] | None = None
    textposition: str | None = "top"
    x: list[float | str | None]  # Allow None values for missing data points
    y: list[float | None]
    type: str
    customdata: list[list[float | None]] | None = None


class PlotlyShape(BaseModel):
    """Represents a shape in a Plotly chart layout."""

    fillcolor: str | None = None
    layer: str | None = None
    line: dict[str, Any]
    type: str
    x0: float | None = None
    x1: float | None = None
    y0: float | None = None
    y1: float | None = None
    xref: str | None = None
    yref: str | None = None


class PlotlyAxis(BaseModel):
    """Represents the properties of an axis in a Plotly chart."""

    title: dict[str, str]
    range: list[float] | None = None
    color: str | None = "#FFFFFF"
    showgrid: bool | None = True
    zeroline: bool | None = True


class PlotlyLayout(BaseModel):
    """Represents the layout properties of a Plotly chart."""

    template: dict[str, Any]
    shapes: list[PlotlyShape] | None = None
    title: dict[str, Any] | None = None
    xaxis: PlotlyAxis
    yaxis: PlotlyAxis
    font: dict[str, str] | None = {
        "family": "Arial",
        "size": "12",
        "color": "#FFFFFF",
    }
    margin: dict[str, int] | None = {"l": 50, "r": 50, "t": 50, "b": 50}
    hovermode: str | None = "closest"
    plot_bgcolor: str | None = "#000000"
    paper_bgcolor: str | None = "#000000"
