"""Digital waveforms, timing diagrams, clock tracks, and bus representations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from manim.constants import DOWN, LEFT, UP
from manim.mobject.geometry.line import DashedLine, DoubleArrow
from manim.mobject.geometry.polygram import Polygon
from manim.mobject.text.text_mobject import Text
from manim.mobject.types.vectorized_mobject import VGroup, VMobject
from manim.utils.color import (
    BLUE,
    GRAY,
    GREEN,
    WHITE,
    YELLOW,
    ManimColor,
)

from ..core.simulator import SimulationTrace
from ..core.state import LogicState

if TYPE_CHECKING:
    pass

__all__ = [
    "DigitalWaveform",
    "ClockWaveform",
    "BusWaveform",
    "TimingDiagram",
]


class DigitalWaveform(VGroup):
    """A single digital waveform channel showing logic level transitions over time.

    Parameters
    ----------
    transitions
        List of (time, state) tuples defining the timeline.
    duration
        Total time duration (width).
    height
        Vertical height of the waveform channel.
    time_scale
        Length per time unit in Manim coordinate units.
    label
        Label displayed on the left of the channel.
    rise_time
        Duration of rising/falling edge slope (0.0 for pure vertical step).
    stroke_color
        Waveform trace color.
    stroke_width
        Waveform stroke width.
    """

    def __init__(
        self,
        transitions: list[tuple[float, LogicState | Any]] | None = None,
        duration: float = 8.0,
        height: float = 0.6,
        time_scale: float = 1.0,
        label: str | None = None,
        rise_time: float = 0.05,
        stroke_color: ManimColor = GREEN,
        stroke_width: float = 2.5,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.transitions = [
            (t, LogicState.parse(s))
            for t, s in (transitions or [(0.0, LogicState.LOW)])
        ]
        self.duration = duration
        self.channel_height = height
        self.time_scale = time_scale
        self.rise_time = rise_time
        self.trace_color = stroke_color
        self.trace_width = stroke_width
        self.label_str = label

        self.path: VMobject = VMobject()
        self.label_mobject: Text | None = None
        self._build_waveform()

    def _build_waveform(self) -> None:
        self.path = VMobject(
            stroke_color=self.trace_color, stroke_width=self.trace_width
        )

        h = self.channel_height
        events = sorted(self.transitions, key=lambda x: x[0])
        if not events:
            events = [(0.0, LogicState.LOW)]

        # Ensure t=0 is covered
        if events[0][0] > 0.0:
            events.insert(0, (0.0, events[0][1]))

        # Helper to convert logic state to local y coordinate
        def y_for_state(state: LogicState) -> float:
            if state == LogicState.HIGH:
                return h
            if state == LogicState.LOW:
                return 0.0
            return h / 2.0  # Tri-state or Undefined centered

        points: list[np.ndarray] = []
        current_y = y_for_state(events[0][1])
        points.append(np.array([0.0, current_y, 0.0]))

        for i in range(len(events)):
            t_curr, state_curr = events[i]
            target_y = y_for_state(state_curr)

            x_curr = t_curr * self.time_scale

            # Draw flat horizontal segment up to transition
            if x_curr > points[-1][0]:
                points.append(np.array([x_curr, current_y, 0.0]))

            # Draw edge slope to target_y
            if not np.isclose(current_y, target_y):
                x_edge = min(
                    x_curr + (self.rise_time * self.time_scale),
                    self.duration * self.time_scale,
                )
                points.append(np.array([x_edge, target_y, 0.0]))
                current_y = target_y

        # Extend to end of duration
        x_end = self.duration * self.time_scale
        if x_end > points[-1][0]:
            points.append(np.array([x_end, current_y, 0.0]))

        self.path.set_points_as_corners(points)
        self.add(self.path)

        if self.label_str:
            self.label_mobject = Text(self.label_str, font_size=16, color=WHITE)
            self.label_mobject.next_to(self.path, LEFT, buff=0.25)
            self.add(self.label_mobject)

    def time_to_x(self, t: float) -> float:
        """Calculate the absolute x coordinate corresponding to time t."""
        return float(self.path.get_left()[0] + (t * self.time_scale))


class ClockWaveform(DigitalWaveform):
    """A regular periodic digital clock signal."""

    def __init__(
        self,
        num_cycles: int = 6,
        period: float = 1.0,
        duty_cycle: float = 0.5,
        label: str = "CLK",
        stroke_color: ManimColor = YELLOW,
        **kwargs: Any,
    ) -> None:
        transitions: list[tuple[float, LogicState]] = []
        duration = num_cycles * period

        for cycle in range(num_cycles):
            t_start = cycle * period
            t_mid = t_start + (period * duty_cycle)
            transitions.append((t_start, LogicState.HIGH))
            transitions.append((t_mid, LogicState.LOW))

        super().__init__(
            transitions=transitions,
            duration=duration,
            label=label,
            stroke_color=stroke_color,
            **kwargs,
        )


class BusWaveform(VGroup):
    """Multi-bit bus waveform channel rendering standard hexagonal envelopes."""

    def __init__(
        self,
        intervals: list[tuple[float, float, str]],
        duration: float = 6.0,
        height: float = 0.6,
        time_scale: float = 1.0,
        label: str = "BUS[7:0]",
        stroke_color: ManimColor = BLUE,
        stroke_width: float = 2.5,
        fill_opacity: float = 0.15,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.intervals = intervals
        self.duration = duration
        self.channel_height = height
        self.time_scale = time_scale
        self.bus_color = stroke_color
        self.bus_stroke_width = stroke_width
        self.fill_op = fill_opacity

        self._build_bus(label)

    def _build_bus(self, label_str: str) -> None:
        h = self.channel_height
        half_h = h / 2.0
        crossover_dt = 0.08 * self.time_scale

        for t_start, t_end, val_text in self.intervals:
            x_s = t_start * self.time_scale
            x_e = t_end * self.time_scale

            # Hexagonal polygon points
            p_left = np.array([x_s, half_h, 0.0])
            p_top_l = np.array([x_s + crossover_dt, h, 0.0])
            p_top_r = np.array([x_e - crossover_dt, h, 0.0])
            p_right = np.array([x_e, half_h, 0.0])
            p_bot_r = np.array([x_e - crossover_dt, 0.0, 0.0])
            p_bot_l = np.array([x_s + crossover_dt, 0.0, 0.0])

            poly = Polygon(
                p_left,
                p_top_l,
                p_top_r,
                p_right,
                p_bot_r,
                p_bot_l,
                stroke_color=self.bus_color,
                stroke_width=self.bus_stroke_width,
                fill_color=self.bus_color,
                fill_opacity=self.fill_op,
            )
            self.add(poly)

            # Center text inside bus packet
            txt = Text(val_text, font_size=14, color=WHITE).move_to(
                np.array([(x_s + x_e) / 2.0, half_h, 0.0])
            )
            self.add(txt)

        if label_str:
            lbl = Text(label_str, font_size=16, color=WHITE)
            lbl.next_to(self, LEFT, buff=0.25)
            self.add(lbl)


class TimingDiagram(VGroup):
    """Multi-channel digital timing diagram with aligned timebase and grid lines."""

    def __init__(
        self,
        duration: float = 6.0,
        time_scale: float = 1.0,
        channel_spacing: float = 1.0,
        show_time_axis: bool = True,
        show_grid: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.duration = duration
        self.time_scale = time_scale
        self.channel_spacing = channel_spacing
        self.show_axis = show_time_axis
        self.show_grid = show_grid

        self.channels: list[VGroup] = []
        self.grid_lines = VGroup()
        self.axis_group = VGroup()

    def add_channel(self, waveform: DigitalWaveform | BusWaveform) -> None:
        """Add a waveform track stacked vertically."""
        if self.channels:
            waveform.next_to(
                self.channels[-1],
                DOWN,
                buff=self.channel_spacing - waveform.channel_height,
            )
            # Align left edges
            x_ref = self.channels[0].submobjects[0].get_left()[0]
            x_curr = waveform.submobjects[0].get_left()[0]
            waveform.shift(np.array([x_ref - x_curr, 0.0, 0.0]))

        self.channels.append(waveform)
        self.add(waveform)
        self._rebuild_decorations()

    def from_trace(
        self,
        trace: SimulationTrace,
        signals: list[str] | None = None,
        channel_colors: dict[str, ManimColor] | None = None,
    ) -> None:
        """Populate timing diagram directly from a SimulationTrace."""
        keys = signals or list(trace.signals.keys())
        colors = channel_colors or {}

        for sig in keys:
            events = trace.signals.get(sig, [(0.0, LogicState.LOW)])
            col = colors.get(sig, GREEN)
            wf = DigitalWaveform(
                transitions=events,
                duration=self.duration,
                time_scale=self.time_scale,
                label=sig,
                stroke_color=col,
            )
            self.add_channel(wf)

    def _rebuild_decorations(self) -> None:
        self.remove(self.grid_lines)
        self.remove(self.axis_group)
        self.grid_lines = VGroup()
        self.axis_group = VGroup()

        if not self.channels:
            return

        top_y = self.channels[0].get_top()[1] + 0.2
        bot_y = self.channels[-1].get_bottom()[1] - 0.2
        x_start = self.channels[0].submobjects[0].get_left()[0]

        # Time divisions and vertical grid lines
        t_ticks = int(self.duration) + 1
        for t in range(t_ticks):
            x_t = x_start + (t * self.time_scale)
            if self.show_grid:
                grid_line = DashedLine(
                    start=np.array([x_t, top_y, 0.0]),
                    end=np.array([x_t, bot_y, 0.0]),
                    stroke_color=GRAY,
                    stroke_width=1.0,
                    dash_length=0.08,
                )
                self.grid_lines.add(grid_line)

            if self.show_axis:
                tick_lbl = Text(str(t), font_size=12, color=GRAY)
                tick_lbl.move_to(np.array([x_t, bot_y - 0.2, 0.0]))
                self.axis_group.add(tick_lbl)

        self.add_to_back(self.grid_lines)
        self.add(self.axis_group)

    def add_timing_interval(
        self,
        t1: float,
        t2: float,
        label: str = "t_pd",
        y_level: float = 0.0,
    ) -> VGroup:
        """Add a dimension arrow measuring time between t1 and t2."""
        x_start = self.channels[0].submobjects[0].get_left()[0]
        x1 = x_start + (t1 * self.time_scale)
        x2 = x_start + (t2 * self.time_scale)

        arrow = DoubleArrow(
            start=np.array([x1, y_level, 0.0]),
            end=np.array([x2, y_level, 0.0]),
            buff=0.0,
            stroke_width=2.0,
            color=YELLOW,
        )
        lbl = Text(label, font_size=13, color=YELLOW).next_to(arrow, UP, buff=0.06)
        grp = VGroup(arrow, lbl)
        self.add(grp)
        return grp
