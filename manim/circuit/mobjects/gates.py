"""Vector mobjects for standard digital logic gates (ANSI/IEEE Std 91/91a)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from manim.mobject.geometry.arc import Circle
from manim.mobject.geometry.line import Line
from manim.mobject.text.text_mobject import Text
from manim.mobject.types.vectorized_mobject import VGroup, VMobject
from manim.utils.color import BLACK, WHITE, ManimColor

from ..core.pin import LogicPin, PinDirection
from ..core.state import (
    LogicState,
    logic_and,
    logic_nand,
    logic_nor,
    logic_not,
    logic_or,
    logic_xnor,
    logic_xor,
)

if TYPE_CHECKING:
    from manim.typing import Point3D

__all__ = [
    "LogicGate",
    "AndGate",
    "OrGate",
    "NotGate",
    "NandGate",
    "NorGate",
    "XorGate",
    "XnorGate",
    "BufferGate",
]


class LogicGate(VGroup):
    """Base class for all digital logic gate vector mobjects.

    Parameters
    ----------
    num_inputs
        Number of input pins (default 2).
    size
        Uniform scale factor for the gate symbol.
    label
        Optional text or symbol displayed at the center or top of the gate.
    stroke_color
        Color of the gate outline and pin leads.
    stroke_width
        Width of the gate outline stroke.
    fill_color
        Interior fill color of the gate.
    fill_opacity
        Fill opacity (0.0 to 1.0).
    inverted
        Whether the primary output is negated with an inversion bubble.
    lead_length
        Length of the input and output pin wire leads.
    """

    def __init__(
        self,
        num_inputs: int = 2,
        size: float = 1.0,
        label: str | None = None,
        stroke_color: ManimColor = WHITE,
        stroke_width: float = 3.0,
        fill_color: ManimColor = BLACK,
        fill_opacity: float = 0.85,
        inverted: bool = False,
        lead_length: float = 0.35,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.num_inputs = max(1, num_inputs)
        self.gate_size = size
        self.label_text = label
        self.inverted = inverted
        self.lead_length = lead_length
        self._custom_stroke_color = stroke_color
        self._custom_stroke_width = stroke_width
        self._custom_fill_color = fill_color
        self._custom_fill_opacity = fill_opacity

        self.pins: list[LogicPin] = []
        self.input_pins: list[LogicPin] = []
        self.output_pins: list[LogicPin] = []

        self.body: VMobject = VMobject()
        self.bubble: Circle | None = None
        self.input_leads: list[Line] = []
        self.output_lead: Line | None = None
        self.label_mobject: Text | None = None

        self._build_gate()
        self.scale(self.gate_size)

    def _build_gate(self) -> None:
        """Construct the visual components, pins, and leads."""
        self.body = self._create_body()
        self.body.set_stroke(
            color=self._custom_stroke_color, width=self._custom_stroke_width
        )
        self.body.set_fill(
            color=self._custom_fill_color, opacity=self._custom_fill_opacity
        )
        self.add(self.body)

        body_right_x = self._get_body_tip_x()
        output_start_x = body_right_x

        if self.inverted:
            bubble_radius = 0.09
            self.bubble = Circle(
                radius=bubble_radius,
                color=self._custom_stroke_color,
                stroke_width=self._custom_stroke_width,
                fill_color=self._custom_fill_color,
                fill_opacity=1.0,
            )
            self.bubble.move_to(np.array([body_right_x + bubble_radius, 0.0, 0.0]))
            self.add(self.bubble)
            output_start_x = body_right_x + (bubble_radius * 2.0)

        # Output pin lead
        output_end_x = output_start_x + self.lead_length
        self.output_lead = Line(
            start=np.array([output_start_x, 0.0, 0.0]),
            end=np.array([output_end_x, 0.0, 0.0]),
            stroke_color=self._custom_stroke_color,
            stroke_width=self._custom_stroke_width,
        )
        self.add(self.output_lead)

        # Output pin model
        out_lead = self.output_lead
        out_pin = LogicPin(
            name="Q",
            direction=PinDirection.OUTPUT,
            component=self,
            inverted=self.inverted,
        )
        out_pin.set_point_getter(lambda: out_lead.get_end())
        self.pins.append(out_pin)
        self.output_pins.append(out_pin)

        # Input pins and leads
        y_positions = self._get_input_y_positions()
        for idx, y_pos in enumerate(y_positions):
            body_left_x = self._get_body_input_x(y_pos)
            lead_start_x = body_left_x - self.lead_length
            lead = Line(
                start=np.array([lead_start_x, y_pos, 0.0]),
                end=np.array([body_left_x, y_pos, 0.0]),
                stroke_color=self._custom_stroke_color,
                stroke_width=self._custom_stroke_width,
            )
            self.input_leads.append(lead)
            self.add(lead)

            pin_name = chr(ord("A") + idx)
            in_pin = LogicPin(
                name=pin_name,
                direction=PinDirection.INPUT,
                component=self,
            )
            # Capture current lead in closure
            in_pin.set_point_getter(
                lambda ld=lead: ld.get_start()  # type: ignore[misc]
            )
            self.pins.append(in_pin)
            self.input_pins.append(in_pin)

        # Optional label
        if self.label_text:
            self.label_mobject = Text(self.label_text, font_size=18, color=WHITE)
            self.label_mobject.move_to(self.body.get_center())
            self.add(self.label_mobject)

    def _get_input_y_positions(self) -> list[float]:
        """Compute the vertical distribution of input pins."""
        if self.num_inputs == 1:
            return [0.0]
        span = 0.7
        return list(np.linspace(span / 2, -span / 2, self.num_inputs, dtype=float))

    def _get_body_tip_x(self) -> float:
        return 0.7

    def _get_body_input_x(self, y: float) -> float:
        return -0.7

    def _create_body(self) -> VMobject:
        raise NotImplementedError

    def evaluate(self) -> LogicState:
        """Compute gate output from current input states."""
        raise NotImplementedError

    def get_input_pin(self, index: int = 0) -> LogicPin:
        """Return input pin at given index."""
        return self.input_pins[index]

    def get_output_pin(self, index: int = 0) -> LogicPin:
        """Return output pin at given index."""
        return self.output_pins[index]

    def get_input_point(self, index: int = 0) -> Point3D:
        """Return coordinates of the specified input lead terminal."""
        return self.input_pins[index].get_point()

    def get_output_point(self, index: int = 0) -> Point3D:
        """Return coordinates of the output lead terminal."""
        return self.output_pins[index].get_point()

    @property
    def in1(self) -> LogicPin:
        """Shortcut for first input pin."""
        return self.input_pins[0]

    @property
    def in2(self) -> LogicPin:
        """Shortcut for second input pin."""
        return self.input_pins[1]

    @property
    def out(self) -> LogicPin:
        """Shortcut for main output pin."""
        return self.output_pins[0]


class AndGate(LogicGate):
    """Standard ANSI/IEEE AND logic gate."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def _create_body(self) -> VMobject:
        body = VMobject()
        w, h = 0.7, 0.55
        h_bezier = h * 0.55228

        # Left back line
        body.start_new_path(np.array([-w, h, 0.0]))
        body.add_line_to(np.array([-w, -h, 0.0]))
        # Bottom horizontal segment
        body.add_line_to(np.array([0.0, -h, 0.0]))
        # Right semicircular front
        body.add_cubic_bezier_curve_to(
            np.array([h_bezier, -h, 0.0]),
            np.array([w, -h_bezier, 0.0]),
            np.array([w, 0.0, 0.0]),
        )
        body.add_cubic_bezier_curve_to(
            np.array([w, h_bezier, 0.0]),
            np.array([h_bezier, h, 0.0]),
            np.array([0.0, h, 0.0]),
        )
        # Top horizontal segment
        body.add_line_to(np.array([-w, h, 0.0]))
        body.close_path()
        return body

    def evaluate(self) -> LogicState:
        res = logic_and(*(p.state for p in self.input_pins))
        if self.inverted:
            res = logic_not(res)
        self.output_pins[0].state = res
        return res


class OrGate(LogicGate):
    """Standard ANSI/IEEE OR logic gate."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def _get_body_input_x(self, y: float) -> float:
        # Account for concave curved back
        w, h = 0.7, 0.55
        rel_y = y / h if h != 0 else 0
        depth = 0.22 * (1.0 - (rel_y**2))
        return -w + depth

    def _create_body(self) -> VMobject:
        body = VMobject()
        w, h = 0.7, 0.55

        # Top-left start
        body.start_new_path(np.array([-w, h, 0.0]))
        # Inward curved back
        body.add_cubic_bezier_curve_to(
            np.array([-w + 0.22, h * 0.5, 0.0]),
            np.array([-w + 0.22, -h * 0.5, 0.0]),
            np.array([-w, -h, 0.0]),
        )
        # Bottom curve to pointed tip
        body.add_cubic_bezier_curve_to(
            np.array([-0.1, -h, 0.0]),
            np.array([0.35, -h * 0.6, 0.0]),
            np.array([w, 0.0, 0.0]),
        )
        # Top curve from pointed tip to top-left
        body.add_cubic_bezier_curve_to(
            np.array([0.35, h * 0.6, 0.0]),
            np.array([-0.1, h, 0.0]),
            np.array([-w, h, 0.0]),
        )
        body.close_path()
        return body

    def evaluate(self) -> LogicState:
        res = logic_or(*(p.state for p in self.input_pins))
        if self.inverted:
            res = logic_not(res)
        self.output_pins[0].state = res
        return res


class NotGate(LogicGate):
    """Standard ANSI/IEEE NOT logic gate (Inverter)."""

    def __init__(self, **kwargs: Any) -> None:
        kwargs["num_inputs"] = 1
        kwargs["inverted"] = True
        super().__init__(**kwargs)

    def _get_body_tip_x(self) -> float:
        return 0.5

    def _create_body(self) -> VMobject:
        body = VMobject()
        w, h = 0.5, 0.45
        body.start_new_path(np.array([-w, h, 0.0]))
        body.add_line_to(np.array([-w, -h, 0.0]))
        body.add_line_to(np.array([w, 0.0, 0.0]))
        body.add_line_to(np.array([-w, h, 0.0]))
        body.close_path()
        return body

    def evaluate(self) -> LogicState:
        res = logic_not(self.input_pins[0].state)
        self.output_pins[0].state = res
        return res


class BufferGate(LogicGate):
    """Non-inverting digital logic buffer."""

    def __init__(self, **kwargs: Any) -> None:
        kwargs["num_inputs"] = 1
        kwargs["inverted"] = False
        super().__init__(**kwargs)

    def _create_body(self) -> VMobject:
        body = VMobject()
        w, h = 0.6, 0.45
        body.start_new_path(np.array([-w, h, 0.0]))
        body.add_line_to(np.array([-w, -h, 0.0]))
        body.add_line_to(np.array([w, 0.0, 0.0]))
        body.add_line_to(np.array([-w, h, 0.0]))
        body.close_path()
        return body

    def evaluate(self) -> LogicState:
        res = self.input_pins[0].state
        self.output_pins[0].state = res
        return res


class NandGate(AndGate):
    """Standard ANSI/IEEE NAND logic gate."""

    def __init__(self, **kwargs: Any) -> None:
        kwargs["inverted"] = True
        super().__init__(**kwargs)

    def evaluate(self) -> LogicState:
        res = logic_nand(*(p.state for p in self.input_pins))
        self.output_pins[0].state = res
        return res


class NorGate(OrGate):
    """Standard ANSI/IEEE NOR logic gate."""

    def __init__(self, **kwargs: Any) -> None:
        kwargs["inverted"] = True
        super().__init__(**kwargs)

    def evaluate(self) -> LogicState:
        res = logic_nor(*(p.state for p in self.input_pins))
        self.output_pins[0].state = res
        return res


class XorGate(OrGate):
    """Standard ANSI/IEEE XOR logic gate."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._add_xor_input_arc()

    def _add_xor_input_arc(self) -> None:
        w, h = 0.7, 0.55
        x_offset = 0.16
        arc = VMobject()
        arc.start_new_path(np.array([-w - x_offset, h, 0.0]))
        arc.add_cubic_bezier_curve_to(
            np.array([-w - x_offset + 0.22, h * 0.5, 0.0]),
            np.array([-w - x_offset + 0.22, -h * 0.5, 0.0]),
            np.array([-w - x_offset, -h, 0.0]),
        )
        arc.set_stroke(color=self._custom_stroke_color, width=self._custom_stroke_width)
        self.add(arc)

    def _get_body_input_x(self, y: float) -> float:
        # Extend inputs to outer arc
        w, h = 0.7, 0.55
        rel_y = y / h if h != 0 else 0
        depth = 0.22 * (1.0 - (rel_y**2))
        return -w - 0.16 + depth

    def evaluate(self) -> LogicState:
        res = logic_xor(*(p.state for p in self.input_pins))
        if self.inverted:
            res = logic_not(res)
        self.output_pins[0].state = res
        return res


class XnorGate(XorGate):
    """Standard ANSI/IEEE XNOR logic gate."""

    def __init__(self, **kwargs: Any) -> None:
        kwargs["inverted"] = True
        super().__init__(**kwargs)

    def evaluate(self) -> LogicState:
        res = logic_xnor(*(p.state for p in self.input_pins))
        self.output_pins[0].state = res
        return res
