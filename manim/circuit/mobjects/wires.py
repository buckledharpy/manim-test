"""Orthogonal (Manhattan) wires, junction dots, and wire bridges for circuit schematics."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from manim.constants import ORIGIN
from manim.mobject.geometry.arc import Dot
from manim.mobject.types.vectorized_mobject import VMobject
from manim.utils.color import ManimColor

from ..core.pin import LogicPin
from ..core.state import LogicState, color_for_state

if TYPE_CHECKING:
    from manim.typing import Point3D

__all__ = [
    "OrthogonalWire",
    "JunctionDot",
    "WireBridge",
]


class OrthogonalWire(VMobject):
    """A Manhattan (orthogonal right-angle) wire connecting two terminals.

    Parameters
    ----------
    start
        Starting pin or 3D point.
    end
        Ending pin or 3D point.
    routing
        Routing strategy: 'auto', 'x_first', 'y_first', or 'mid_x'.
    mid_x
        Custom x-coordinate for the vertical segment (when routing='mid_x' or 'auto').
    stroke_color
        Initial stroke color (defaults to color of initial LogicState.LOW).
    stroke_width
        Wire stroke width (default 3.0).
    corner_radius
        Optional rounding of 90-degree corners (default 0.0 for sharp corners).
    """

    def __init__(
        self,
        start: LogicPin | Point3D,
        end: LogicPin | Point3D,
        routing: str = "auto",
        mid_x: float | None = None,
        stroke_color: ManimColor | None = None,
        stroke_width: float = 3.0,
        corner_radius: float = 0.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.start_target = start
        self.end_target = end
        self.routing = routing
        self.custom_mid_x = mid_x
        self.corner_radius = corner_radius
        self.current_state: LogicState = LogicState.LOW

        init_color = stroke_color or color_for_state(self.current_state)
        self.set_stroke(color=init_color, width=stroke_width)
        self.update_routing()

        # Connect to pins' nets if available
        if isinstance(self.start_target, LogicPin) and isinstance(
            self.end_target, LogicPin
        ):
            net = self.start_target.connect_to(self.end_target)
            net.add_wire(self)
            self.current_state = net.state
            self.update_state_color(self.current_state)

    def _resolve_point(self, target: LogicPin | Point3D) -> np.ndarray:
        if isinstance(target, LogicPin):
            return np.array(target.get_point(), dtype=float)
        return np.array(target, dtype=float)

    def compute_waypoints(self) -> list[np.ndarray]:
        """Compute the Manhattan corner vertices connecting start to end."""
        p_start = self._resolve_point(self.start_target)
        p_end = self._resolve_point(self.end_target)

        x1, y1, z1 = p_start
        x2, y2, z2 = p_end

        if np.allclose(p_start, p_end):
            return [p_start, p_end]

        # Horizontal or vertical alignment
        if np.isclose(y1, y2):
            return [p_start, p_end]
        if np.isclose(x1, x2):
            return [p_start, p_end]

        if self.routing == "x_first":
            corner = np.array([x2, y1, z1])
            return [p_start, corner, p_end]

        if self.routing == "y_first":
            corner = np.array([x1, y2, z1])
            return [p_start, corner, p_end]

        # 'auto' or 'mid_x' routing
        if self.custom_mid_x is not None:
            xm = self.custom_mid_x
        elif x2 >= x1:
            xm = (x1 + x2) / 2.0
        else:
            # Loopback routing when target is behind source
            offset = 0.5
            xm = max(x1, x2) + offset

        c1 = np.array([xm, y1, z1])
        c2 = np.array([xm, y2, z1])
        return [p_start, c1, c2, p_end]

    def update_routing(self) -> None:
        """Recompute path geometry from current terminal coordinates."""
        waypoints = self.compute_waypoints()
        self.clear_points()
        self.set_points_as_corners(waypoints)

    def update_state_color(self, state: LogicState | Any) -> None:
        """Update the wire stroke color based on logical state."""
        self.current_state = LogicState.parse(state)
        self.set_stroke(color=color_for_state(self.current_state))


class JunctionDot(Dot):
    """Visual solder dot representing an electrical node branch (T-junction)."""

    def __init__(
        self,
        point: Point3D = ORIGIN,
        radius: float = 0.08,
        state: LogicState = LogicState.LOW,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            point=point,
            radius=radius,
            color=color_for_state(state),
            **kwargs,
        )
        self.current_state = state

    def update_state_color(self, state: LogicState | Any) -> None:
        """Recolor dot to match net state."""
        self.current_state = LogicState.parse(state)
        self.set_color(color_for_state(self.current_state))


class WireBridge(VMobject):
    """An arc/hop glyph rendered when one wire crosses over another without connecting."""

    def __init__(
        self,
        center: Point3D = ORIGIN,
        radius: float = 0.14,
        orientation: str = "horizontal",
        stroke_color: ManimColor | None = None,
        stroke_width: float = 3.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        c = np.array(center, dtype=float)
        col = stroke_color or color_for_state(LogicState.LOW)
        self.set_stroke(color=col, width=stroke_width)

        # Semicircle arc jump
        r = radius
        if orientation == "horizontal":
            self.start_new_path(c + np.array([-r, 0.0, 0.0]))
            self.add_cubic_bezier_curve_to(
                c + np.array([-r, r * 1.33, 0.0]),
                c + np.array([r, r * 1.33, 0.0]),
                c + np.array([r, 0.0, 0.0]),
            )
        else:
            self.start_new_path(c + np.array([0.0, -r, 0.0]))
            self.add_cubic_bezier_curve_to(
                c + np.array([r * 1.33, -r, 0.0]),
                c + np.array([r * 1.33, r, 0.0]),
                c + np.array([0.0, r, 0.0]),
            )
