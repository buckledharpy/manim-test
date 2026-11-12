"""Terminal pins and interconnect nets for digital logic circuits."""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from typing import TYPE_CHECKING, Any

import numpy as np

from manim.constants import ORIGIN
from manim.typing import Point3D

from .state import LogicState

if TYPE_CHECKING:
    from manim.mobject.mobject import Mobject

__all__ = [
    "PinDirection",
    "LogicPin",
    "Net",
]


class PinDirection(Enum):
    """Directionality of a logic terminal pin."""

    INPUT = "input"
    OUTPUT = "output"
    BIDIRECTIONAL = "bidirectional"
    CLOCK = "clock"
    ENABLE = "enable"


class LogicPin:
    """Represents a connection pin on a logic gate or circuit component.

    Parameters
    ----------
    name
        Name or identifier of the pin (e.g. 'A', 'B', 'Q', 'CLK').
    direction
        Signal direction: INPUT, OUTPUT, CLOCK, etc.
    component
        The parent Mobject or gate owning this pin.
    offset
        3D vector offset from the component's center where the pin terminates.
    inverted
        Whether this is an active-low inverted pin (renders with a bubble).
    clock
        Whether this is an edge-triggered clock input.
    initial_state
        Initial LogicState of this pin.
    """

    def __init__(
        self,
        name: str = "PIN",
        direction: PinDirection = PinDirection.INPUT,
        component: Mobject | None = None,
        offset: Point3D = ORIGIN,
        inverted: bool = False,
        clock: bool = False,
        initial_state: LogicState = LogicState.LOW,
    ) -> None:
        self.name = name
        self.direction = direction
        self.component = component
        self.offset = np.array(offset, dtype=float)
        self.inverted = inverted
        self.clock = clock
        self._state = LogicState.parse(initial_state)
        self.net: Net | None = None
        self._point_getter: Callable[[], Point3D] | None = None

    def __repr__(self) -> str:
        comp_name = self.component.__class__.__name__ if self.component else "None"
        return f"<LogicPin {self.name} ({self.direction.value}) of {comp_name} = {self._state}>"

    @property
    def state(self) -> LogicState:
        """Return the current logical state of this pin."""
        return self._state

    @state.setter
    def state(self, value: LogicState | Any) -> None:
        """Set state and notify net if this is an output pin."""
        new_state = LogicState.parse(value)
        self._state = new_state
        if self.direction == PinDirection.OUTPUT and self.net is not None:
            self.net.set_state(new_state, source_pin=self)

    def set_point_getter(self, getter: Callable[[], Point3D]) -> None:
        """Assign a dynamic callable that returns the current 3D position."""
        self._point_getter = getter

    def get_point(self) -> Point3D:
        """Return the absolute coordinates of the pin in scene space."""
        if self._point_getter is not None:
            return np.array(self._point_getter(), dtype=float)
        if self.component is not None:
            return self.component.get_center() + self.offset
        return self.offset

    def connect_to(self, other_pin: LogicPin) -> Net:
        """Connect this pin to another pin via a shared Net."""
        if self.net is not None and other_pin.net is not None:
            if self.net is not other_pin.net:
                # Merge two nets
                self.net.merge(other_pin.net)
            return self.net
        if self.net is not None:
            self.net.add_pin(other_pin)
            return self.net
        if other_pin.net is not None:
            other_pin.net.add_pin(self)
            return other_pin.net

        # If one of the pins is an output driver with an established state, inherit it
        init_state = LogicState.LOW
        if self.direction in (PinDirection.OUTPUT, PinDirection.BIDIRECTIONAL):
            init_state = self.state
        elif other_pin.direction in (PinDirection.OUTPUT, PinDirection.BIDIRECTIONAL):
            init_state = other_pin.state

        net_name = f"NET_{self.name}_{other_pin.name}"
        new_net = Net(name=net_name, initial_state=init_state)
        new_net.add_pin(self)
        new_net.add_pin(other_pin)
        return new_net


class Net:
    """An equipotential electrical node connecting driver and sink pins.

    Parameters
    ----------
    name
        Descriptive label for this net.
    initial_state
        Initial LogicState of the net.
    """

    def __init__(
        self,
        name: str = "NET",
        initial_state: LogicState = LogicState.LOW,
    ) -> None:
        self.name = name
        self._state = LogicState.parse(initial_state)
        self.pins: list[LogicPin] = []
        self.wires: list[Any] = []

    def __repr__(self) -> str:
        return f"<Net {self.name}: {len(self.pins)} pins, state={self._state}>"

    @property
    def state(self) -> LogicState:
        return self._state

    def add_pin(self, pin: LogicPin) -> None:
        """Add a pin to this net."""
        if pin not in self.pins:
            self.pins.append(pin)
            pin.net = self
            pin._state = self._state

    def add_wire(self, wire: Any) -> None:
        """Associate a visual wire Mobject with this net."""
        if wire not in self.wires:
            self.wires.append(wire)

    def set_state(
        self,
        new_state: LogicState | Any,
        source_pin: LogicPin | None = None,
    ) -> None:
        """Broadcast new logic state across all connected sink pins and wires."""
        self._state = LogicState.parse(new_state)
        for pin in self.pins:
            if pin is not source_pin:
                pin._state = self._state
        for wire in self.wires:
            if hasattr(wire, "update_state_color"):
                wire.update_state_color(self._state)

    def get_driver_pins(self) -> list[LogicPin]:
        """Return all pins driving this net (typically outputs)."""
        return [
            p
            for p in self.pins
            if p.direction in (PinDirection.OUTPUT, PinDirection.BIDIRECTIONAL)
        ]

    def get_sink_pins(self) -> list[LogicPin]:
        """Return all load pins receiving from this net (inputs)."""
        return [
            p
            for p in self.pins
            if p.direction
            in (PinDirection.INPUT, PinDirection.CLOCK, PinDirection.ENABLE)
        ]

    def merge(self, other: Net) -> None:
        """Merge another net into this net."""
        for p in other.pins:
            self.add_pin(p)
        for w in other.wires:
            self.add_wire(w)
        other.pins.clear()
        other.wires.clear()
