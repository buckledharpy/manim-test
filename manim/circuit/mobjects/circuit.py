"""Circuit container managing components, interconnections, and live simulation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from manim.mobject.types.vectorized_mobject import VGroup

from ..core.pin import LogicPin, Net
from ..core.simulator import LogicSimulator
from ..core.state import LogicState
from .wires import OrthogonalWire

if TYPE_CHECKING:
    from .gates import LogicGate

__all__ = ["Circuit"]


class Circuit(VGroup):
    """Container and manager for an entire digital circuit.

    Coordinates component placement, wire routing, and logic simulation.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.components: list[Any] = []
        self.wires: list[OrthogonalWire] = []
        self.nets: list[Net] = []
        self.simulator = LogicSimulator()

    def add_component(self, component: Any, name: str | None = None) -> Any:
        """Add a gate, flip-flop, or block to the circuit."""
        if name:
            setattr(self, name, component)
            component.label_text = name
        self.components.append(component)
        self.simulator.add_component(component)
        self.add(component)
        return component

    def add_gate(self, gate: LogicGate, name: str | None = None) -> LogicGate:
        """Convenience method to add a logic gate."""
        self.add_component(gate, name=name)
        return gate

    def connect(
        self,
        pin1: LogicPin,
        pin2: LogicPin,
        routing: str = "auto",
        **kwargs: Any,
    ) -> OrthogonalWire:
        """Route an orthogonal wire between two terminal pins.

        Merges their nets and establishes an electrical connection.
        """
        wire = OrthogonalWire(pin1, pin2, routing=routing, **kwargs)
        self.wires.append(wire)
        self.add(wire)

        if wire.start_target.net and wire.start_target.net not in self.nets:
            self.nets.append(wire.start_target.net)
            self.simulator.add_net(wire.start_target.net)

        return wire

    def set_input(self, pin_or_name: str | LogicPin, state: LogicState | Any) -> None:
        """Set the value of a circuit input pin and update its net."""
        val = LogicState.parse(state)
        target_pin: LogicPin | None = None
        if isinstance(pin_or_name, str):
            for comp in self.components:
                for p in getattr(comp, "pins", []):
                    if (
                        p.name == pin_or_name
                        or getattr(p, "full_name", "") == pin_or_name
                    ):
                        target_pin = p
                        break
                if target_pin:
                    break
        else:
            target_pin = pin_or_name

        if target_pin:
            target_pin.state = val
            if target_pin.net:
                target_pin.net.set_state(val, source_pin=target_pin)

    def simulate(self) -> dict[str, LogicState]:
        """Run steady-state logic simulation and update all wires and outputs."""
        self.simulator.evaluate_combinational()
        # Refresh all wire visual states
        for w in self.wires:
            if isinstance(w.start_target, LogicPin) and w.start_target.net:
                w.update_state_color(w.start_target.net.state)
        return {
            f"{getattr(c, 'label_text', c.__class__.__name__)}.{p.name}": p.state
            for c in self.components
            for p in getattr(c, "pins", [])
        }

    def update_wires(self) -> None:
        """Recompute Manhattan routing for all wires (e.g. after moving gates)."""
        for wire in self.wires:
            wire.update_routing()
