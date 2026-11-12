"""Animated Logic Circuit Demonstration Scene."""

from manim import *
from manim.circuit import (
    AndGate,
    Circuit,
    ClockWaveform,
    DigitalWaveform,
    GateTrigger,
    InteractiveTruthTable,
    LogicState,
    NotGate,
    PropagateSignal,
    TimingDiagram,
)


class CircuitDemoScene(Scene):
    def construct(self):
        # 1. Create Circuit container and gates
        circuit = Circuit()
        g_and = circuit.add_gate(AndGate(), name="AND1")
        g_not = circuit.add_gate(NotGate(), name="NOT1")

        g_and.shift(LEFT * 2.5)
        g_not.next_to(g_and, RIGHT, buff=1.8)

        # 2. Connect gates with orthogonal wire
        wire = circuit.connect(g_and.out, g_not.in1)

        # 3. Create interactive Truth Table
        table = InteractiveTruthTable.from_gate(g_and).scale(0.7).to_corner(UR)

        # 4. Create Timing Diagram
        timing = TimingDiagram(duration=4.0, time_scale=0.8).scale(0.7).to_edge(DOWN)
        clk = ClockWaveform(num_cycles=4, period=1.0)
        q_wave = DigitalWaveform(
            [(0.0, LogicState.LOW), (2.0, LogicState.HIGH), (4.0, LogicState.LOW)],
            duration=4.0,
            label="OUT",
        )
        timing.add_channel(clk)
        timing.add_channel(q_wave)

        # Animations
        self.play(Create(circuit), Create(table), Create(timing))
        self.wait(0.5)

        # Stimulate inputs: A=1, B=1
        g_and.in1.state = LogicState.HIGH
        g_and.in2.state = LogicState.HIGH
        highlight = table.highlight_state(A=1, B=1)

        self.play(Create(highlight), GateTrigger(g_and))
        self.play(PropagateSignal(wire, state=LogicState.HIGH))
        self.play(GateTrigger(g_not))
        self.wait(1.0)
