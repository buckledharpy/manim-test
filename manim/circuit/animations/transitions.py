"""Gate evaluation trigger and pin toggle visual animations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from manim.animation.animation import Animation
from manim.utils.color import YELLOW, ManimColor

from ..core.pin import LogicPin
from ..core.state import LogicState

if TYPE_CHECKING:
    from ..mobjects.gates import LogicGate

__all__ = [
    "GateTrigger",
    "PinToggle",
]


class GateTrigger(Animation):
    """Flashes the gate outline and body when the gate evaluates and switches state.

    Parameters
    ----------
    gate
        The LogicGate triggering.
    flash_color
        Glow highlight color (default bright YELLOW).
    """

    def __init__(
        self,
        gate: LogicGate,
        flash_color: ManimColor = YELLOW,
        run_time: float = 0.5,
        **kwargs: Any,
    ) -> None:
        self.gate = gate
        self.flash_color = flash_color
        self.original_stroke_color = gate.body.get_stroke_color()
        self.original_stroke_width = gate.body.get_stroke_width()
        self.original_fill_opacity = gate.body.get_fill_opacity()
        super().__init__(gate, run_time=run_time, **kwargs)

    def finish(self) -> None:
        super().finish()
        self.gate.body.set_stroke(
            color=self.original_stroke_color, width=self.original_stroke_width
        )
        self.gate.body.set_fill(opacity=self.original_fill_opacity)

    def interpolate_mobject(self, alpha: float) -> None:
        # Sine pulse
        pulse = np.sin(np.pi * alpha)
        extra_w = 4.0 * pulse
        self.gate.body.set_stroke(
            color=self.flash_color if pulse > 0.1 else self.original_stroke_color,
            width=self.original_stroke_width + extra_w,
        )
        self.gate.body.set_fill(
            opacity=min(1.0, self.original_fill_opacity + (0.35 * pulse))
        )


class PinToggle(Animation):
    """Animates a logic pin toggling between 0 and 1."""

    def __init__(
        self,
        pin: LogicPin,
        new_state: LogicState | Any,
        run_time: float = 0.4,
        **kwargs: Any,
    ) -> None:
        self.pin = pin
        self.target_state = LogicState.parse(new_state)
        # Target representation is the component owning this pin or fallback
        comp = pin.component
        super().__init__(comp, run_time=run_time, **kwargs)

    def finish(self) -> None:
        super().finish()
        self.pin.state = self.target_state

    def interpolate_mobject(self, alpha: float) -> None:
        pass
