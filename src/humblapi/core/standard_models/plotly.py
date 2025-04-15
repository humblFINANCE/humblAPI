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
    shape: str
    smoothing: float


class PlotlyTrace(BaseModel):
    """Represents a single trace in a Plotly chart."""

    hovertemplate: str
    line: PlotlyLine
    marker: PlotlyMarker
    mode: str
    name: str
    text: list[str]
    textfont: dict[str, Any]
    textposition: str
    x: list[float]
    y: list[float]
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
    range: list[float]
    color: str
    showgrid: bool
    zeroline: bool


class PlotlyLayout(BaseModel):
    """Represents the layout properties of a Plotly chart."""

    template: dict[str, Any]
    shapes: list[PlotlyShape]
    title: dict[str, Any]
    xaxis: PlotlyAxis
    yaxis: PlotlyAxis
    font: dict[str, str]
    margin: dict[str, int]
    hovermode: str
    plot_bgcolor: str
    paper_bgcolor: str
