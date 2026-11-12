"""CLI tool for digital circuit simulation, truth table generation, and scene scaffolding."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import click
import cloup
from rich.table import Table as RichTable

from manim._config import console
from manim.circuit.core.state import (
    LogicState,
    logic_and,
    logic_nand,
    logic_nor,
    logic_not,
    logic_or,
    logic_xnor,
    logic_xor,
)
from manim.constants import CONTEXT_SETTINGS, EPILOG

__all__ = ["circuit"]

GATES_MAP: dict[str, tuple[str, Callable[..., LogicState], int]] = {
    "and": ("AND Gate", logic_and, 2),
    "or": ("OR Gate", logic_or, 2),
    "xor": ("XOR Gate", logic_xor, 2),
    "nand": ("NAND Gate", logic_nand, 2),
    "nor": ("NOR Gate", logic_nor, 2),
    "xnor": ("XNOR Gate", logic_xnor, 2),
    "not": ("NOT Inverter", lambda a: logic_not(a), 1),
}


@cloup.group(
    context_settings=CONTEXT_SETTINGS,
    no_args_is_help=True,
    epilog=EPILOG,
    help="Digital logic circuits, simulation, and timing tools.",
)
def circuit() -> None:
    """Digital logic circuits, simulation, and timing tools."""


@circuit.command(
    context_settings=CONTEXT_SETTINGS,
    epilog=EPILOG,
    help="Print the truth table for a logic gate or boolean function.",
)
@cloup.argument(
    "gate",
    type=cloup.Choice(list(GATES_MAP.keys()), case_sensitive=False),
    default="and",
    required=False,
)
@cloup.option(
    "-n",
    "--inputs",
    "num_inputs",
    type=int,
    default=2,
    help="Number of inputs (for multi-input gates).",
)
def table(gate: str, num_inputs: int) -> None:
    """Generate and display a formatted truth table in the console."""
    gate_key = gate.lower()
    title, func, default_n = GATES_MAP[gate_key]
    n = 1 if gate_key == "not" else max(2, num_inputs)

    rich_table = RichTable(
        title=f"Truth Table: {title} ({n} Inputs)",
        title_style="bold green",
        header_style="bold cyan",
    )

    in_labels = [chr(ord("A") + i) for i in range(n)]
    for lbl in in_labels:
        rich_table.add_column(lbl, justify="center")
    rich_table.add_column("Output (Q)", justify="center", style="bold magenta")

    import itertools

    for combination in itertools.product((0, 1), repeat=n):
        states = [LogicState.parse(b) for b in combination]
        res = func(*states) if n > 1 else func(states[0])
        row = [
            f"[green]{b}[/green]" if b == 1 else f"[dim]{b}[/dim]" for b in combination
        ]
        res_val = res.to_int()
        res_style = "[bold green]1[/bold green]" if res_val == 1 else "[dim]0[/dim]"
        row.append(res_style)
        rich_table.add_row(*row)

    console.print(rich_table)


@circuit.command(
    context_settings=CONTEXT_SETTINGS,
    epilog=EPILOG,
    help="Simulate a logic gate with specified binary inputs.",
)
@cloup.argument(
    "gate",
    type=cloup.Choice(list(GATES_MAP.keys()), case_sensitive=False),
)
@cloup.argument("input_bits", nargs=-1, required=True)
def sim(gate: str, input_bits: tuple[str, ...]) -> None:
    """Simulate gate output for a specific input bit sequence."""
    gate_key = gate.lower()
    title, func, _ = GATES_MAP[gate_key]

    states = [LogicState.parse(b) for b in input_bits]
    if gate_key == "not" and len(states) != 1:
        console.print("[red]Error: NOT gate requires exactly 1 input bit.[/red]")
        return
    if gate_key != "not" and len(states) < 2:
        console.print("[red]Error: Gate requires at least 2 input bits.[/red]")
        return

    res = func(*states) if len(states) > 1 else func(states[0])
    console.print(
        f"[cyan]{title}[/cyan] with inputs {[str(s) for s in states]} -> "
        f"Output: [bold green]{res}[/bold green]"
    )


SCENE_TEMPLATE = '''"""Animated Logic Circuit Demonstration Scene."""

from manim import *
from manim.circuit import (
    AndGate,
    NotGate,
    Circuit,
    PropagateSignal,
    GateTrigger,
    TimingDiagram,
    ClockWaveform,
    DigitalWaveform,
    InteractiveTruthTable,
    LogicState,
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
'''


@circuit.command(
    name="init-scene",
    context_settings=CONTEXT_SETTINGS,
    epilog=EPILOG,
    help="Scaffold a complete starter circuit animation scene script.",
)
@cloup.argument(
    "file_path",
    type=cloup.Path(path_type=Path),
    default=Path("circuit_demo.py"),
    required=False,
)
def init_scene(file_path: Path) -> None:
    """Generate a starter Python file with an animated logic circuit scene."""
    if file_path.suffix != ".py":
        file_path = file_path.with_suffix(".py")

    if file_path.exists() and not click.confirm(
        f"File '{file_path}' already exists. Overwrite?"
    ):
        console.print("[yellow]Aborted.[/yellow]")
        return

    file_path.write_text(SCENE_TEMPLATE)
    console.print(
        f"[green]Successfully generated circuit scene template:[/green] [bold]{file_path}[/bold]"
    )
    console.print(f"Run it with: [cyan]manim -pql {file_path} CircuitDemoScene[/cyan]")
