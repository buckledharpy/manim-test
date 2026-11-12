"""Sequential circuits, flip-flops, latches, and multiplexers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from manim.mobject.geometry.arc import Circle
from manim.mobject.geometry.line import Line
from manim.mobject.geometry.polygram import Polygon, Rectangle
from manim.mobject.text.text_mobject import Text
from manim.mobject.types.vectorized_mobject import VGroup, VMobject
from manim.utils.color import BLACK, WHITE, ManimColor

from ..core.pin import LogicPin, PinDirection
from ..core.state import LogicState, logic_not

if TYPE_CHECKING:
    pass

__all__ = [
    "DFlipFlop",
    "SRLatch",
    "Multiplexer",
]


class DFlipFlop(VGroup):
    """Positive edge-triggered D Flip-Flop with complementary outputs (Q and Q_bar).

    Parameters
    ----------
    size
        Scale factor for the IC body.
    label
        Label displayed inside the body (default 'D-FF').
    stroke_color
        Stroke color of the IC outline.
    fill_color
        Fill color of the IC body.
    lead_length
        Length of connection leads extending from the body.
    """

    def __init__(
        self,
        size: float = 1.0,
        label: str = "D-FF",
        stroke_color: ManimColor = WHITE,
        fill_color: ManimColor = BLACK,
        lead_length: float = 0.35,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.ff_size = size
        self.stroke_col = stroke_color
        self.fill_col = fill_color
        self.lead_len = lead_length
        self.stored_state: LogicState = LogicState.LOW

        self.pins: list[LogicPin] = []
        self._build_flip_flop(label)
        self.scale(self.ff_size)

    def _build_flip_flop(self, label: str) -> None:
        width, height = 1.3, 1.6

        # Body rectangle
        self.body = Rectangle(
            width=width,
            height=height,
            stroke_color=self.stroke_col,
            stroke_width=3.0,
            fill_color=self.fill_col,
            fill_opacity=0.85,
        )
        self.add(self.body)

        half_w = width / 2.0
        y_d = 0.45
        y_clk = -0.45
        y_q = 0.45
        y_qbar = -0.45

        # D input lead & pin
        d_lead = Line(
            start=np.array([-half_w - self.lead_len, y_d, 0.0]),
            end=np.array([-half_w, y_d, 0.0]),
            stroke_color=self.stroke_col,
            stroke_width=3.0,
        )
        self.add(d_lead)
        self.pin_d = LogicPin(name="D", direction=PinDirection.INPUT, component=self)
        self.pin_d.set_point_getter(lambda: d_lead.get_start())
        self.pins.append(self.pin_d)

        # Clock input lead & edge-trigger chevron (triangle)
        clk_lead = Line(
            start=np.array([-half_w - self.lead_len, y_clk, 0.0]),
            end=np.array([-half_w, y_clk, 0.0]),
            stroke_color=self.stroke_col,
            stroke_width=3.0,
        )
        self.add(clk_lead)
        self.pin_clk = LogicPin(
            name="CLK",
            direction=PinDirection.CLOCK,
            component=self,
            clock=True,
        )
        self.pin_clk.set_point_getter(lambda: clk_lead.get_start())
        self.pins.append(self.pin_clk)

        # Chevron '>' at clock input
        chev_size = 0.12
        chevron = VMobject(stroke_color=self.stroke_col, stroke_width=2.5)
        chevron.start_new_path(np.array([-half_w, y_clk + chev_size, 0.0]))
        chevron.add_line_to(np.array([-half_w + chev_size, y_clk, 0.0]))
        chevron.add_line_to(np.array([-half_w, y_clk - chev_size, 0.0]))
        self.add(chevron)

        # Q output lead & pin
        q_lead = Line(
            start=np.array([half_w, y_q, 0.0]),
            end=np.array([half_w + self.lead_len, y_q, 0.0]),
            stroke_color=self.stroke_col,
            stroke_width=3.0,
        )
        self.add(q_lead)
        self.pin_q = LogicPin(
            name="Q",
            direction=PinDirection.OUTPUT,
            component=self,
            initial_state=self.stored_state,
        )
        self.pin_q.set_point_getter(lambda: q_lead.get_end())
        self.pins.append(self.pin_q)

        # Q_bar output lead, inversion bubble & pin
        bubble_r = 0.08
        self.bubble = Circle(
            radius=bubble_r,
            stroke_color=self.stroke_col,
            stroke_width=3.0,
            fill_color=self.fill_col,
            fill_opacity=1.0,
        )
        self.bubble.move_to(np.array([half_w + bubble_r, y_qbar, 0.0]))
        self.add(self.bubble)

        qbar_lead = Line(
            start=np.array([half_w + (bubble_r * 2.0), y_qbar, 0.0]),
            end=np.array([half_w + (bubble_r * 2.0) + self.lead_len, y_qbar, 0.0]),
            stroke_color=self.stroke_col,
            stroke_width=3.0,
        )
        self.add(qbar_lead)
        self.pin_qbar = LogicPin(
            name="Q_BAR",
            direction=PinDirection.OUTPUT,
            component=self,
            inverted=True,
            initial_state=logic_not(self.stored_state),
        )
        self.pin_qbar.set_point_getter(lambda: qbar_lead.get_end())
        self.pins.append(self.pin_qbar)

        # Text annotations
        lbl_d = Text("D", font_size=15, color=WHITE).next_to(
            d_lead.get_end(), [1, 0, 0], buff=0.08
        )
        lbl_q = Text("Q", font_size=15, color=WHITE).next_to(
            q_lead.get_start(), [-1, 0, 0], buff=0.08
        )
        lbl_title = Text(label, font_size=14, color=WHITE).move_to(
            self.body.get_center()
        )
        self.add(lbl_d, lbl_q, lbl_title)

    def trigger_clock(self, edge: str = "rising") -> LogicState:
        """Evaluate positive clock edge: latch D into Q."""
        if edge == "rising":
            self.stored_state = self.pin_d.state
            self.pin_q.state = self.stored_state
            self.pin_qbar.state = logic_not(self.stored_state)
        return self.stored_state


class SRLatch(VGroup):
    """Set-Reset (SR) latch with active-high inputs."""

    def __init__(
        self,
        size: float = 1.0,
        stroke_color: ManimColor = WHITE,
        fill_color: ManimColor = BLACK,
        lead_length: float = 0.35,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        width, height = 1.3, 1.5
        self.stored_state = LogicState.LOW

        self.body = Rectangle(
            width=width,
            height=height,
            stroke_color=stroke_color,
            stroke_width=3.0,
            fill_color=fill_color,
            fill_opacity=0.85,
        )
        self.add(self.body)

        half_w = width / 2.0
        s_lead = Line(
            start=np.array([-half_w - lead_length, 0.4, 0.0]),
            end=np.array([-half_w, 0.4, 0.0]),
            stroke_color=stroke_color,
            stroke_width=3.0,
        )
        r_lead = Line(
            start=np.array([-half_w - lead_length, -0.4, 0.0]),
            end=np.array([-half_w, -0.4, 0.0]),
            stroke_color=stroke_color,
            stroke_width=3.0,
        )
        q_lead = Line(
            start=np.array([half_w, 0.4, 0.0]),
            end=np.array([half_w + lead_length, 0.4, 0.0]),
            stroke_color=stroke_color,
            stroke_width=3.0,
        )
        qbar_lead = Line(
            start=np.array([half_w, -0.4, 0.0]),
            end=np.array([half_w + lead_length, -0.4, 0.0]),
            stroke_color=stroke_color,
            stroke_width=3.0,
        )
        self.add(s_lead, r_lead, q_lead, qbar_lead)

        self.pin_s = LogicPin("S", PinDirection.INPUT, component=self)
        self.pin_s.set_point_getter(lambda: s_lead.get_start())

        self.pin_r = LogicPin("R", PinDirection.INPUT, component=self)
        self.pin_r.set_point_getter(lambda: r_lead.get_start())

        self.pin_q = LogicPin("Q", PinDirection.OUTPUT, component=self)
        self.pin_q.set_point_getter(lambda: q_lead.get_end())

        self.pin_qbar = LogicPin("Q_BAR", PinDirection.OUTPUT, component=self)
        self.pin_qbar.set_point_getter(lambda: qbar_lead.get_end())

        self.pins = [self.pin_s, self.pin_r, self.pin_q, self.pin_qbar]

        lbl_s = Text("S", font_size=15, color=WHITE).next_to(
            s_lead.get_end(), [1, 0, 0], buff=0.08
        )
        lbl_r = Text("R", font_size=15, color=WHITE).next_to(
            r_lead.get_end(), [1, 0, 0], buff=0.08
        )
        lbl_q = Text("Q", font_size=15, color=WHITE).next_to(
            q_lead.get_start(), [-1, 0, 0], buff=0.08
        )
        lbl_title = Text("SR-Latch", font_size=13, color=WHITE).move_to(
            self.body.get_center()
        )
        self.add(lbl_s, lbl_r, lbl_q, lbl_title)
        self.scale(size)

    def evaluate(self) -> LogicState:
        s = self.pin_s.state
        r = self.pin_r.state

        if s == LogicState.HIGH and r == LogicState.HIGH:
            self.stored_state = LogicState.UNDEFINED
        elif s == LogicState.HIGH:
            self.stored_state = LogicState.HIGH
        elif r == LogicState.HIGH:
            self.stored_state = LogicState.LOW

        self.pin_q.state = self.stored_state
        self.pin_qbar.state = logic_not(self.stored_state)
        return self.stored_state


class Multiplexer(VGroup):
    """2-to-1 or 4-to-1 multiplexer with trapezoidal schematic symbol.

    Parameters
    ----------
    num_data_inputs
        Number of data inputs (e.g. 2, 4, 8).
    size
        Uniform scale factor.
    """

    def __init__(
        self,
        num_data_inputs: int = 2,
        size: float = 1.0,
        stroke_color: ManimColor = WHITE,
        fill_color: ManimColor = BLACK,
        lead_length: float = 0.35,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.num_inputs = num_data_inputs
        self.lead_len = lead_length

        # Trapezoid body: taller on left, narrower on right
        w = 0.9
        h_left = 0.5 * max(2, self.num_inputs)
        h_right = h_left * 0.6

        p_tl = np.array([-w / 2, h_left / 2, 0.0])
        p_bl = np.array([-w / 2, -h_left / 2, 0.0])
        p_br = np.array([w / 2, -h_right / 2, 0.0])
        p_tr = np.array([w / 2, h_right / 2, 0.0])

        self.body = Polygon(
            p_tl,
            p_bl,
            p_br,
            p_tr,
            stroke_color=stroke_color,
            stroke_width=3.0,
            fill_color=fill_color,
            fill_opacity=0.85,
        )
        self.add(self.body)

        self.data_pins: list[LogicPin] = []
        self.pins: list[LogicPin] = []

        # Data inputs on left
        y_positions = np.linspace(h_left * 0.35, -h_left * 0.35, self.num_inputs)
        for i, y_val in enumerate(y_positions):
            lead = Line(
                start=np.array([-w / 2 - self.lead_len, y_val, 0.0]),
                end=np.array([-w / 2, y_val, 0.0]),
                stroke_color=stroke_color,
                stroke_width=3.0,
            )
            self.add(lead)
            p = LogicPin(name=f"D{i}", direction=PinDirection.INPUT, component=self)
            p.set_point_getter(
                lambda ld=lead: ld.get_start()  # type: ignore[misc]
            )
            self.data_pins.append(p)
            self.pins.append(p)

        # Select pin on bottom
        sel_lead = Line(
            start=np.array([0.0, -h_left / 2 - self.lead_len, 0.0]),
            end=np.array([0.0, -(h_left + h_right) / 4, 0.0]),
            stroke_color=stroke_color,
            stroke_width=3.0,
        )
        self.add(sel_lead)
        self.select_pin = LogicPin(
            name="SEL", direction=PinDirection.INPUT, component=self
        )
        self.select_pin.set_point_getter(lambda: sel_lead.get_start())
        self.pins.append(self.select_pin)

        # Output pin on right
        out_lead = Line(
            start=np.array([w / 2, 0.0, 0.0]),
            end=np.array([w / 2 + self.lead_len, 0.0, 0.0]),
            stroke_color=stroke_color,
            stroke_width=3.0,
        )
        self.add(out_lead)
        self.output_pin = LogicPin(
            name="Y", direction=PinDirection.OUTPUT, component=self
        )
        self.output_pin.set_point_getter(lambda: out_lead.get_end())
        self.pins.append(self.output_pin)

        title = Text("MUX", font_size=14, color=WHITE).move_to(self.body.get_center())
        self.add(title)
        self.scale(size)

    def evaluate(self) -> LogicState:
        sel_val = 1 if self.select_pin.state == LogicState.HIGH else 0
        if sel_val < len(self.data_pins):
            out_state = self.data_pins[sel_val].state
        else:
            out_state = LogicState.UNDEFINED
        self.output_pin.state = out_state
        return out_state
