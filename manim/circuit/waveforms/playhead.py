"""Synchronized time cursor / playhead for timing diagrams."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from manim.constants import UP
from manim.mobject.geometry.line import Line
from manim.mobject.geometry.polygram import Triangle
from manim.mobject.text.text_mobject import Text
from manim.mobject.types.vectorized_mobject import VGroup
from manim.mobject.value_tracker import ValueTracker
from manim.utils.color import RED, WHITE, ManimColor

if TYPE_CHECKING:
    from .timing import TimingDiagram

__all__ = ["TimeCursor"]


class TimeCursor(VGroup):
    """Vertical scanning cursor / playhead line synchronized with circuit simulation time.

    Parameters
    ----------
    timing_diagram
        The parent TimingDiagram this cursor traverses.
    initial_time
        Starting time in seconds / arbitrary units.
    color
        Cursor stroke color (default bright RED).
    show_time_tag
        Whether to display a floating time value badge above the cursor.
    """

    def __init__(
        self,
        timing_diagram: TimingDiagram,
        initial_time: float = 0.0,
        color: ManimColor = RED,
        show_time_tag: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.diagram = timing_diagram
        self.cursor_color = color
        self.show_tag = show_time_tag
        self.time_tracker = ValueTracker(initial_time)

        top_y = timing_diagram.get_top()[1] + 0.3
        bot_y = timing_diagram.get_bottom()[1] - 0.3

        self.line = Line(
            start=np.array([0.0, top_y, 0.0]),
            end=np.array([0.0, bot_y, 0.0]),
            stroke_color=self.cursor_color,
            stroke_width=2.5,
        )
        self.add(self.line)

        # Triangular pointer at top
        pointer = Triangle(
            stroke_color=self.cursor_color,
            fill_color=self.cursor_color,
            fill_opacity=1.0,
        )
        pointer.scale(0.1).rotate(np.pi).move_to(np.array([0.0, top_y, 0.0]))
        self.add(pointer)

        self.tag: Text | None = None
        if self.show_tag:
            self.tag = Text(f"t={initial_time:.1f}", font_size=12, color=WHITE)
            self.tag.next_to(pointer, UP, buff=0.08)
            self.add(self.tag)

        self._update_position(initial_time)

        # Reactive updater linking ValueTracker to spatial position
        self.add_updater(lambda m: m._update_position(self.time_tracker.get_value()))

    def _update_position(self, current_time: float) -> None:
        if not self.diagram.channels:
            return
        x_origin = self.diagram.channels[0].submobjects[0].get_left()[0]
        target_x = x_origin + (current_time * self.diagram.time_scale)
        current_x = self.line.get_center()[0]
        delta_x = target_x - current_x
        self.shift(np.array([delta_x, 0.0, 0.0]))

        if self.tag is not None:
            self.tag.become(
                Text(f"t={current_time:.1f}", font_size=12, color=WHITE).move_to(
                    self.tag.get_center()
                )
            )

    def set_time(self, t: float) -> None:
        """Explicitly set current cursor time."""
        self.time_tracker.set_value(t)
