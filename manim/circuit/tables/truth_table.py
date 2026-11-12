"""Truth tables with dynamic row highlighting and automated Boolean evaluation."""

from __future__ import annotations

import itertools
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from manim.mobject.geometry.shape_matchers import SurroundingRectangle
from manim.mobject.table import Table
from manim.mobject.text.text_mobject import Text
from manim.utils.color import WHITE, YELLOW, ManimColor

from ..core.state import LogicState

if TYPE_CHECKING:
    from ..mobjects.circuit import Circuit
    from ..mobjects.gates import LogicGate

__all__ = ["InteractiveTruthTable"]


class InteractiveTruthTable(Table):
    """An interactive truth table with automated evaluation and active-row highlighting.

    Parameters
    ----------
    input_names
        List of input variable labels (e.g. ['A', 'B']).
    output_names
        List of output variable labels (e.g. ['Q']).
    evaluator
        Callable that receives a dict of input {name: LogicState} and returns
        either a dict of {output_name: LogicState} or a single LogicState.
    """

    def __init__(
        self,
        input_names: list[str],
        output_names: list[str],
        evaluator: Callable[..., Any],
        font_size: int = 18,
        **kwargs: Any,
    ) -> None:
        self.input_names = input_names
        self.output_names = output_names
        self.evaluator = evaluator
        self.row_map: dict[tuple[int, ...], int] = {}
        self.active_highlight: SurroundingRectangle | None = None

        matrix = self._generate_table_data()
        col_labels = [
            Text(col, font_size=font_size, color=WHITE)
            for col in (input_names + output_names)
        ]

        super().__init__(
            matrix,
            col_labels=col_labels,
            **kwargs,
        )

    def _generate_table_data(self) -> list[list[str]]:
        matrix: list[list[str]] = []
        n = len(self.input_names)

        # Generate all 2^n binary combinations
        for idx, combination in enumerate(itertools.product((0, 1), repeat=n)):
            self.row_map[combination] = idx + 1  # 1-indexed to account for header

            in_dict = {
                name: LogicState.parse(val)
                for name, val in zip(self.input_names, combination, strict=False)
            }
            res = self.evaluator(in_dict)

            row: list[str] = [str(val) for val in combination]
            if isinstance(res, dict):
                row.extend(
                    str(res.get(out_name, LogicState.UNDEFINED))
                    for out_name in self.output_names
                )
            else:
                row.append(str(LogicState.parse(res)))

            matrix.append(row)

        return matrix

    @classmethod
    def from_gate(
        cls,
        gate: LogicGate,
        font_size: int = 18,
        **kwargs: Any,
    ) -> InteractiveTruthTable:
        """Construct a truth table automatically from a LogicGate instance."""
        in_names = [p.name for p in gate.input_pins]
        out_names = [p.name for p in gate.output_pins]

        def gate_eval(inputs: dict[str, LogicState]) -> LogicState:
            for p in gate.input_pins:
                if p.name in inputs:
                    p.state = inputs[p.name]
            return gate.evaluate()

        return cls(
            input_names=in_names,
            output_names=out_names,
            evaluator=gate_eval,
            font_size=font_size,
            **kwargs,
        )

    @classmethod
    def from_circuit(
        cls,
        circuit: Circuit,
        input_names: list[str],
        output_names: list[str],
        font_size: int = 18,
        **kwargs: Any,
    ) -> InteractiveTruthTable:
        """Construct a truth table automatically from an assembled Circuit."""

        def circuit_eval(inputs: dict[str, LogicState]) -> dict[str, LogicState]:
            for k, v in inputs.items():
                circuit.set_input(k, v)
            return circuit.simulate()

        return cls(
            input_names=input_names,
            output_names=output_names,
            evaluator=circuit_eval,
            font_size=font_size,
            **kwargs,
        )

    def get_row_highlight(
        self, row_index: int, color: ManimColor = YELLOW, buff: float = 0.08
    ) -> SurroundingRectangle:
        """Return a SurroundingRectangle around the specified row."""
        row_mobject = self.get_rows()[row_index]
        return SurroundingRectangle(
            row_mobject, color=color, stroke_width=2.5, buff=buff
        )

    def highlight_state(
        self,
        color: ManimColor = YELLOW,
        **input_values: Any,
    ) -> SurroundingRectangle:
        """Find the row matching the input values and return its highlight box."""
        key = tuple(
            1 if LogicState.parse(input_values[name]) == LogicState.HIGH else 0
            for name in self.input_names
        )
        row_idx = self.row_map.get(key, 1)
        rect = self.get_row_highlight(row_idx, color=color)
        self.active_highlight = rect
        return rect
