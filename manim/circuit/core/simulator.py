"""Discrete logic simulation and event-driven timing engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .pin import LogicPin, Net, PinDirection
from .state import LogicState

if TYPE_CHECKING:
    pass

__all__ = [
    "SimulationTrace",
    "LogicSimulator",
]


@dataclass
class SimulationTrace:
    """Stores the chronological logic transitions of all circuit nets and pins.

    Useful for driving timing diagrams and synchronized playhead cursors.
    """

    # Map of signal_name -> list of (time, state)
    signals: dict[str, list[tuple[float, LogicState]]] = field(default_factory=dict)
    duration: float = 0.0

    def record_transition(self, signal: str, time: float, state: LogicState) -> None:
        """Record a state transition at a given simulation timestamp."""
        if signal not in self.signals:
            self.signals[signal] = []
        transitions = self.signals[signal]
        if transitions and transitions[-1][0] == time:
            # Overwrite same-timestamp transition
            transitions[-1] = (time, state)
        else:
            transitions.append((time, state))
        if time > self.duration:
            self.duration = time

    def get_state_at(self, signal: str, time: float) -> LogicState:
        """Retrieve the logic state of a signal at an arbitrary timestamp."""
        transitions = self.signals.get(signal, [])
        if not transitions:
            return LogicState.UNDEFINED
        last_state = transitions[0][1]
        for t, s in transitions:
            if t <= time:
                last_state = s
            else:
                break
        return last_state


class LogicSimulator:
    """Event-driven and cycle-based simulator for digital circuit networks.

    Supports topological evaluation for combinational paths and relaxation
    for feedback loops (latches/flip-flops).
    """

    def __init__(self) -> None:
        self.components: list[Any] = []
        self.nets: list[Net] = []
        self.primary_inputs: list[LogicPin] = []
        self.primary_outputs: list[LogicPin] = []

    def add_component(self, component: Any) -> None:
        """Register a logic component (gate, latch, mux) with the simulator."""
        if component not in self.components:
            self.components.append(component)

    def add_net(self, net: Net) -> None:
        """Register an interconnect net."""
        if net not in self.nets:
            self.nets.append(net)

    def register_primary_input(self, pin: LogicPin) -> None:
        """Designate a pin as an external circuit stimulus input."""
        if pin not in self.primary_inputs:
            self.primary_inputs.append(pin)

    def register_primary_output(self, pin: LogicPin) -> None:
        """Designate a pin as an external circuit observed output."""
        if pin not in self.primary_outputs:
            self.primary_outputs.append(pin)

    def evaluate_combinational(self, max_iterations: int = 50) -> bool:
        """Evaluate all components iteratively until steady state is reached.

        Returns True if converged, False if oscillation or circular hazard detected.
        """
        for _ in range(max_iterations):
            changed = False
            for comp in self.components:
                if hasattr(comp, "evaluate"):
                    old_outputs = [
                        p.state for p in comp.pins if p.direction == PinDirection.OUTPUT
                    ]
                    comp.evaluate()
                    new_outputs = [
                        p.state for p in comp.pins if p.direction == PinDirection.OUTPUT
                    ]
                    if old_outputs != new_outputs:
                        changed = True

            # Synchronize net states
            for net in self.nets:
                drivers = net.get_driver_pins()
                if drivers:
                    # Single driver model (or dominant contention)
                    net.set_state(drivers[0].state)

            if not changed:
                return True
        return False

    def simulate_vector(
        self, input_values: dict[str | LogicPin, LogicState | Any]
    ) -> dict[str, LogicState]:
        """Apply an input stimulus vector and return resulting pin states."""
        # Apply inputs
        for pin_or_name, val in input_values.items():
            state = LogicState.parse(val)
            if isinstance(pin_or_name, str):
                for p in self.primary_inputs:
                    if p.name == pin_or_name:
                        p.state = state
                        if p.net:
                            p.net.set_state(state)
            elif isinstance(pin_or_name, LogicPin):
                pin_or_name.state = state
                if pin_or_name.net:
                    pin_or_name.net.set_state(state)

        self.evaluate_combinational()

        results: dict[str, LogicState] = {}
        for p in self.primary_inputs:
            results[p.name] = p.state
        for p in self.primary_outputs:
            results[p.name] = p.state
        for comp in self.components:
            for p in getattr(comp, "pins", []):
                results[
                    f"{getattr(comp, 'label_text', comp.__class__.__name__)}.{p.name}"
                ] = p.state

        return results

    def run_trace(
        self,
        timeline: list[tuple[float, dict[str | LogicPin, LogicState | Any]]],
        gate_delay: float = 0.2,
    ) -> SimulationTrace:
        """Run an event-driven timeline simulation with gate delays.

        Parameters
        ----------
        timeline
            List of (time_offset, input_dict) events.
        gate_delay
            Time delta added for gate output propagation.

        Returns
        -------
        SimulationTrace
            Complete record of signal waveforms over time.
        """
        trace = SimulationTrace()
        current_time = 0.0

        for t_event, inputs in timeline:
            current_time = max(current_time, t_event)
            # Record input changes
            for pin_key, val in inputs.items():
                name = pin_key if isinstance(pin_key, str) else pin_key.name
                state = LogicState.parse(val)
                trace.record_transition(name, current_time, state)

            # Apply and simulate
            self.simulate_vector(inputs)
            sim_time = current_time + gate_delay

            # Record internal and output states
            for comp in self.components:
                c_name = getattr(comp, "label_text", comp.__class__.__name__)
                for p in getattr(comp, "pins", []):
                    trace.record_transition(f"{c_name}.{p.name}", sim_time, p.state)
            for p in self.primary_outputs:
                trace.record_transition(p.name, sim_time, p.state)

        return trace
