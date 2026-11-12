"""A simple script demonstrating digital logic gate animation in Manim."""

from manim import *
from manim.circuit import (
    AndGate,
    Circuit,
    GateTrigger,
    InteractiveTruthTable,
    LogicState,
    PropagateSignal,
)


class SimpleGateAnimation(Scene):
    """Animate an AND gate evaluation with signal propagation and truth table synchronization."""

    def construct(self):
        # 1. Title
        title = Text("Logic Gate Simulation: AND Gate", font_size=28).to_edge(UP)
        self.add(title)

        # 2. Build the circuit schematic
        circuit = Circuit()
        and_gate = circuit.add_gate(AndGate(size=1.3), name="AND1")
        and_gate.shift(LEFT * 1.5)

        # Input terminals & output terminal
        in_a_pt = and_gate.get_input_point(0) + LEFT * 2.0
        in_b_pt = and_gate.get_input_point(1) + LEFT * 2.0
        out_pt = and_gate.get_output_point(0) + RIGHT * 2.0

        # Route wires to the gate (OrthogonalWire directly connects points to pins)
        wire_a = OrthogonalWire(in_a_pt, and_gate.in1)
        wire_b = OrthogonalWire(in_b_pt, and_gate.in2)
        wire_out = OrthogonalWire(and_gate.out, out_pt)
        circuit.add(wire_a, wire_b, wire_out)

        # Terminal labels
        lbl_a = Text("A = 0", font_size=20).next_to(in_a_pt, LEFT)
        lbl_b = Text("B = 0", font_size=20).next_to(in_b_pt, LEFT)
        lbl_out = Text("Q = 0", font_size=20).next_to(out_pt, RIGHT)

        # 3. Synchronized Truth Table (top right)
        truth_table = InteractiveTruthTable.from_gate(and_gate, font_size=16)
        truth_table.scale(0.75).to_corner(UR, buff=0.8)

        # Initial display
        self.play(
            Create(circuit),
            Create(truth_table),
            FadeIn(lbl_a, lbl_b, lbl_out),
        )
        self.wait(0.5)

        # --- Transition 1: Set A = 1, B = 0 -> Q remains 0 ---
        hl_1 = truth_table.highlight_state(A=1, B=0)
        lbl_a_high = Text("A = 1", font_size=20, color=GREEN).next_to(in_a_pt, LEFT)

        self.play(
            Transform(lbl_a, lbl_a_high),
            Create(hl_1),
        )
        self.play(PropagateSignal(wire_a, state=LogicState.HIGH))
        self.play(GateTrigger(and_gate))
        self.wait(0.5)

        # --- Transition 2: Set B = 1 -> Q switches to 1! ---
        hl_2 = truth_table.highlight_state(A=1, B=1)
        lbl_b_high = Text("B = 1", font_size=20, color=GREEN).next_to(in_b_pt, LEFT)
        lbl_out_high = Text("Q = 1", font_size=20, color=GREEN).next_to(out_pt, RIGHT)

        self.play(
            Transform(lbl_b, lbl_b_high),
            Transform(hl_1, hl_2),
        )
        self.play(PropagateSignal(wire_b, state=LogicState.HIGH))
        self.play(GateTrigger(and_gate))
        self.play(
            PropagateSignal(wire_out, state=LogicState.HIGH),
            Transform(lbl_out, lbl_out_high),
        )
        self.wait(1.5)


if __name__ == "__main__":
    import os

    os.system("manim -pql simple_gate_animation.py SimpleGateAnimation")
