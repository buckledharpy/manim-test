"""Unit tests for digital logic gates, circuits, waveforms, and timing diagrams."""

from __future__ import annotations

import numpy as np

from manim.circuit import (
    AndGate,
    BufferGate,
    BusWaveform,
    Circuit,
    ClockWaveform,
    DFlipFlop,
    DigitalWaveform,
    GateTrigger,
    InteractiveTruthTable,
    LogicPin,
    LogicState,
    Multiplexer,
    NandGate,
    NorGate,
    NotGate,
    OrGate,
    OrthogonalWire,
    PinDirection,
    PinToggle,
    PropagateSignal,
    PulseWire,
    SRLatch,
    TimeCursor,
    TimingDiagram,
    XnorGate,
    XorGate,
    logic_and,
    logic_nand,
    logic_nor,
    logic_not,
    logic_or,
    logic_xnor,
    logic_xor,
)


def test_logic_state_operations():
    assert logic_not(LogicState.LOW) == LogicState.HIGH
    assert logic_not(LogicState.HIGH) == LogicState.LOW
    assert logic_and(LogicState.HIGH, LogicState.HIGH) == LogicState.HIGH
    assert logic_and(LogicState.HIGH, LogicState.LOW) == LogicState.LOW
    assert logic_or(LogicState.LOW, LogicState.HIGH) == LogicState.HIGH
    assert logic_or(LogicState.LOW, LogicState.LOW) == LogicState.LOW
    assert logic_xor(LogicState.HIGH, LogicState.LOW) == LogicState.HIGH
    assert logic_xor(LogicState.HIGH, LogicState.HIGH) == LogicState.LOW
    assert logic_nand(LogicState.HIGH, LogicState.HIGH) == LogicState.LOW
    assert logic_nor(LogicState.LOW, LogicState.LOW) == LogicState.HIGH
    assert logic_xnor(LogicState.HIGH, LogicState.HIGH) == LogicState.HIGH

    # Parsing
    assert LogicState.parse(1) == LogicState.HIGH
    assert LogicState.parse(0) == LogicState.LOW
    assert LogicState.parse(True) == LogicState.HIGH
    assert LogicState.parse(False) == LogicState.LOW
    assert LogicState.parse("z") == LogicState.HIGH_Z
    assert LogicState.parse("x") == LogicState.UNDEFINED


def test_pins_and_nets():
    p1 = LogicPin("A", PinDirection.OUTPUT, initial_state=LogicState.HIGH)
    p2 = LogicPin("B", PinDirection.INPUT, initial_state=LogicState.LOW)

    net = p1.connect_to(p2)
    assert p1.net is net
    assert p2.net is net
    assert p2.state == LogicState.HIGH

    p1.state = LogicState.LOW
    assert p2.state == LogicState.LOW


def test_gate_evaluations():
    and_g = AndGate()
    and_g.in1.state = LogicState.HIGH
    and_g.in2.state = LogicState.HIGH
    assert and_g.evaluate() == LogicState.HIGH

    and_g.in2.state = LogicState.LOW
    assert and_g.evaluate() == LogicState.LOW

    or_g = OrGate()
    or_g.in1.state = LogicState.LOW
    or_g.in2.state = LogicState.HIGH
    assert or_g.evaluate() == LogicState.HIGH

    not_g = NotGate()
    not_g.in1.state = LogicState.HIGH
    assert not_g.evaluate() == LogicState.LOW

    xor_g = XorGate()
    xor_g.in1.state = LogicState.HIGH
    xor_g.in2.state = LogicState.HIGH
    assert xor_g.evaluate() == LogicState.LOW

    nand_g = NandGate()
    nand_g.in1.state = LogicState.HIGH
    nand_g.in2.state = LogicState.HIGH
    assert nand_g.evaluate() == LogicState.LOW

    nor_g = NorGate()
    nor_g.in1.state = LogicState.LOW
    nor_g.in2.state = LogicState.LOW
    assert nor_g.evaluate() == LogicState.HIGH

    xnor_g = XnorGate()
    xnor_g.in1.state = LogicState.HIGH
    xnor_g.in2.state = LogicState.HIGH
    assert xnor_g.evaluate() == LogicState.HIGH

    buf_g = BufferGate()
    buf_g.in1.state = LogicState.HIGH
    assert buf_g.evaluate() == LogicState.HIGH


def test_sequential_components():
    # D-Flip-Flop
    dff = DFlipFlop()
    dff.pin_d.state = LogicState.HIGH
    assert dff.pin_q.state == LogicState.LOW
    dff.trigger_clock("rising")
    assert dff.pin_q.state == LogicState.HIGH
    assert dff.pin_qbar.state == LogicState.LOW

    # SR-Latch
    sr = SRLatch()
    sr.pin_s.state = LogicState.HIGH
    sr.pin_r.state = LogicState.LOW
    assert sr.evaluate() == LogicState.HIGH
    assert sr.pin_q.state == LogicState.HIGH
    assert sr.pin_qbar.state == LogicState.LOW

    # Mux
    mux = Multiplexer(num_data_inputs=2)
    mux.data_pins[0].state = LogicState.LOW
    mux.data_pins[1].state = LogicState.HIGH
    mux.select_pin.state = LogicState.LOW
    assert mux.evaluate() == LogicState.LOW
    mux.select_pin.state = LogicState.HIGH
    assert mux.evaluate() == LogicState.HIGH


def test_circuit_assembly_and_simulation():
    circuit = Circuit()
    g1 = circuit.add_gate(AndGate(), name="G1")
    g2 = circuit.add_gate(NotGate(), name="G2")

    wire = circuit.connect(g1.out, g2.in1)
    assert wire is not None

    g1.in1.state = LogicState.HIGH
    g1.in2.state = LogicState.HIGH
    res = circuit.simulate()

    assert g1.out.state == LogicState.HIGH
    assert g2.out.state == LogicState.LOW
    assert wire.current_state == LogicState.HIGH


def test_waveforms_and_timing():
    td = TimingDiagram(duration=4.0)
    clk = ClockWaveform(num_cycles=4, period=1.0)
    data = DigitalWaveform(
        [(0.0, LogicState.LOW), (1.5, LogicState.HIGH), (3.0, LogicState.LOW)],
        duration=4.0,
        label="SIG",
    )
    bus = BusWaveform(
        [(0.0, 2.0, "0x01"), (2.0, 4.0, "0x02")],
        duration=4.0,
        label="BUS",
    )

    td.add_channel(clk)
    td.add_channel(data)
    td.add_channel(bus)

    cursor = TimeCursor(td, initial_time=2.0)
    cursor.set_time(3.0)
    assert len(td.channels) == 3


def test_interactive_truth_table():
    and_gate = AndGate()
    tt = InteractiveTruthTable.from_gate(and_gate)
    assert len(tt.get_rows()) == 5  # header + 4 rows

    box = tt.highlight_state(A=1, B=1)
    assert box is not None


def test_circuit_animations_creation():
    g = AndGate()
    g.in1.state = LogicState.HIGH
    g.in2.state = LogicState.HIGH
    w = OrthogonalWire(np.array([0, 0, 0]), np.array([2, 1, 0]))

    anim_prop = PropagateSignal(w, state=LogicState.HIGH)
    anim_pulse = PulseWire(w)
    anim_trig = GateTrigger(g)
    anim_toggle = PinToggle(g.in1, LogicState.LOW)

    assert anim_prop is not None
    assert anim_pulse is not None
    assert anim_trig is not None
    assert anim_toggle is not None
