"""Digital logic gates, schematic circuit networks, waveforms, and timing diagrams for Manim."""

from __future__ import annotations

from .animations import (
    GateTrigger,
    PinToggle,
    PropagateSignal,
    PulseWire,
)
from .core import (
    LogicPin,
    LogicSimulator,
    LogicState,
    Net,
    PinDirection,
    SimulationTrace,
    color_for_state,
    logic_and,
    logic_nand,
    logic_nor,
    logic_not,
    logic_or,
    logic_xnor,
    logic_xor,
)
from .mobjects import (
    AndGate,
    BufferGate,
    Circuit,
    DFlipFlop,
    JunctionDot,
    LogicGate,
    Multiplexer,
    NandGate,
    NorGate,
    NotGate,
    OrGate,
    OrthogonalWire,
    SRLatch,
    WireBridge,
    XnorGate,
    XorGate,
)
from .tables import InteractiveTruthTable
from .waveforms import (
    BusWaveform,
    ClockWaveform,
    DigitalWaveform,
    TimeCursor,
    TimingDiagram,
)

__all__ = [
    # Core
    "LogicState",
    "color_for_state",
    "logic_and",
    "logic_or",
    "logic_not",
    "logic_xor",
    "logic_nand",
    "logic_nor",
    "logic_xnor",
    "PinDirection",
    "LogicPin",
    "Net",
    "LogicSimulator",
    "SimulationTrace",
    # Mobjects
    "LogicGate",
    "AndGate",
    "OrGate",
    "NotGate",
    "NandGate",
    "NorGate",
    "XorGate",
    "XnorGate",
    "BufferGate",
    "DFlipFlop",
    "SRLatch",
    "Multiplexer",
    "OrthogonalWire",
    "JunctionDot",
    "WireBridge",
    "Circuit",
    # Waveforms
    "DigitalWaveform",
    "ClockWaveform",
    "BusWaveform",
    "TimingDiagram",
    "TimeCursor",
    # Animations
    "PropagateSignal",
    "PulseWire",
    "GateTrigger",
    "PinToggle",
    # Tables
    "InteractiveTruthTable",
]
