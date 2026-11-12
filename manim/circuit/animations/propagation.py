"""Signal propagation animations along orthogonal circuit wires."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from manim.animation.animation import Animation
from manim.mobject.geometry.arc import Dot
from manim.utils.color import YELLOW, ManimColor

from ..core.pin import LogicPin
from ..core.state import LogicState, color_for_state
from ..mobjects.wires import OrthogonalWire

if TYPE_CHECKING:
    pass

__all__ = [
    "PropagateSignal",
    "PulseWire",
]


class PropagateSignal(Animation):
    """Animates a signal packet pulse traveling along an orthogonal circuit wire.

    Upon reaching the destination pin, the wire and sink pin update their state color.

    Parameters
    ----------
    wire
        The OrthogonalWire being traversed.
    state
        The LogicState being propagated (defaults to wire's driver pin state).
    pulse_color
        Color of the traveling packet dot (defaults to state color or bright YELLOW).
    pulse_radius
        Radius of the traveling packet dot.
    """

    def __init__(
        self,
        wire: OrthogonalWire,
        state: LogicState | Any | None = None,
        pulse_color: ManimColor | None = None,
        pulse_radius: float = 0.08,
        run_time: float = 0.8,
        **kwargs: Any,
    ) -> None:
        self.wire = wire
        if state is not None:
            self.signal_state = LogicState.parse(state)
        elif isinstance(wire.start_target, LogicPin):
            self.signal_state = wire.start_target.state
        else:
            self.signal_state = wire.current_state

        col = pulse_color or (
            YELLOW
            if self.signal_state == LogicState.HIGH
            else color_for_state(self.signal_state)
        )
        self.packet = Dot(
            point=wire.get_start(),
            radius=pulse_radius,
            color=col,
            fill_opacity=1.0,
        )
        super().__init__(wire, run_time=run_time, **kwargs)

    def begin(self) -> None:
        super().begin()
        # Attach traveling packet to wire's scene presentation
        self.wire.add(self.packet)

    def finish(self) -> None:
        super().finish()
        if self.packet in self.wire.submobjects:
            self.wire.remove(self.packet)
        # Update wire to final state color
        self.wire.update_state_color(self.signal_state)
        if isinstance(self.wire.end_target, LogicPin):
            self.wire.end_target.state = self.signal_state

    def interpolate_mobject(self, alpha: float) -> None:
        clamped_alpha = min(1.0, max(0.0, float(alpha)))
        point = self.wire.point_from_proportion(clamped_alpha)
        self.packet.move_to(point)


class PulseWire(Animation):
    """Animates a wire progressively lighting up from driver terminal to load."""

    def __init__(
        self,
        wire: OrthogonalWire,
        state: LogicState | Any = LogicState.HIGH,
        run_time: float = 0.7,
        **kwargs: Any,
    ) -> None:
        self.wire = wire
        self.target_state = LogicState.parse(state)
        self.target_color = color_for_state(self.target_state)
        super().__init__(wire, run_time=run_time, **kwargs)

    def finish(self) -> None:
        super().finish()
        self.wire.update_state_color(self.target_state)

    def interpolate_mobject(self, alpha: float) -> None:
        # Interpolate stroke width and color glow
        glow_width = 3.0 + (3.0 * np.sin(np.pi * alpha))
        self.wire.set_stroke(width=glow_width)
