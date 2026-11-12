"""Core data structures and simulation engine for digital logic."""

from __future__ import annotations

from .pin import LogicPin, Net, PinDirection
from .simulator import LogicSimulator, SimulationTrace
from .state import (
    LogicState,
    color_for_state,
    logic_and,
    logic_nand,
    logic_nor,
    logic_not,
    logic_or,
    logic_xnor,
    logic_xor,
)

__all__ = [
    "LogicState",
    "logic_not",
    "logic_and",
    "logic_or",
    "logic_xor",
    "logic_nand",
    "logic_nor",
    "logic_xnor",
    "color_for_state",
    "PinDirection",
    "LogicPin",
    "Net",
    "LogicSimulator",
    "SimulationTrace",
]
