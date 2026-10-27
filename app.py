from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd
import streamlit as st


JAVA_SOLVER = Path(__file__).parent / "java" / "SudokuSolver.java"
JAVA_TIMEOUT_SECONDS = 30

EXAMPLE_BOARDS = {
    4: [
        [1, 0, 0, 4],
        [0, 4, 1, 0],
        [0, 1, 4, 0],
        [4, 0, 0, 1],
    ],
    9: [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ],
}


def solve_with_java(grid: list[list[int]]) -> list[list[int]]:
    """Run the Java backtracking solver and return its solved grid."""
    size = len(grid)
    input_text = "\n".join(",".join(map(str, row)) for row in grid)

    try:
        result = subprocess.run(
            ["java", str(JAVA_SOLVER), str(size)],
            input=input_text,
            capture_output=True,
            text=True,
            check=False,
            timeout=JAVA_TIMEOUT_SECONDS,
        )
    except FileNotFoundError as error:
        raise RuntimeError(
            "Java was not found. Install JDK 11 or newer and ensure `java` is on PATH."
        ) from error
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("The Java solver timed out while solving this puzzle.") from error

    if result.returncode != 0:
        message = result.stderr.strip() or "The Java solver could not process this puzzle."
        raise ValueError(message)

    try:
        solution = [
            [int(value) for value in line.split(",")]
            for line in result.stdout.strip().splitlines()
        ]
    except ValueError as error:
        raise RuntimeError("The Java solver returned an invalid response.") from error

    if len(solution) != size or any(len(row) != size for row in solution):
        raise RuntimeError("The Java solver returned a grid with an unexpected size.")
    return solution


def read_grid(data: pd.DataFrame, size: int) -> list[list[int]]:
    grid: list[list[int]] = []
    for row_index in range(size):
        row: list[int] = []
        for column_index in range(size):
            value = data.iat[row_index, column_index]
            if pd.isna(value) or isinstance(value, bool):
                raise ValueError("Every cell must contain a whole number from 0 to the grid size.")
            try:
                integer_value = int(value)
            except (TypeError, ValueError, OverflowError) as error:
                raise ValueError(
                    "Every cell must contain a whole number from 0 to the grid size."
                ) from error
            if integer_value != value or not 0 <= integer_value <= size:
                raise ValueError(f"Cell values must be whole numbers from 0 to {size}.")
            row.append(integer_value)
        grid.append(row)
    return grid


st.set_page_config(page_title="Mini Sudoku Solver", page_icon="🧩", layout="centered")
st.title("Mini Sudoku Solver")
st.caption("Fill in a 4×4 or 9×9 puzzle and let the Java backtracking solver complete it.")

if "board_size" not in st.session_state:
    st.session_state.board_size = 9

size = st.selectbox("Grid size", options=[4, 9], format_func=lambda value: f"{value}×{value}", key="board_size")
grid_key = f"grid-{size}"

if st.session_state.get("active_grid_size") != size:
    st.session_state.grid_values = [row.copy() for row in EXAMPLE_BOARDS[size]]
    st.session_state.active_grid_size = size
    st.session_state.pop("solved_input", None)
    st.session_state.pop("solution", None)

if st.button("Load example puzzle"):
    st.session_state.grid_values = [row.copy() for row in EXAMPLE_BOARDS[size]]
    st.session_state.pop(grid_key, None)
    st.session_state.pop("solved_input", None)
    st.session_state.pop("solution", None)

st.write("Enter **0** for an empty cell.")
editor_data = st.data_editor(
    pd.DataFrame(st.session_state.grid_values),
    key=grid_key,
    hide_index=True,
    use_container_width=True,
    num_rows="fixed",
    column_config={
        column: st.column_config.NumberColumn(
            f"Column {column + 1}",
            min_value=0,
            max_value=size,
            step=1,
            format="%d",
        )
        for column in range(size)
    },
)

if st.button("Solve", type="primary", use_container_width=True):
    try:
        puzzle = read_grid(editor_data, size)
        solution = solve_with_java(puzzle)
        st.session_state.solved_input = puzzle
        st.session_state.solution = solution
        st.success("Puzzle solved.")
    except ValueError as error:
        st.session_state.pop("solution", None)
        st.error(str(error))
    except RuntimeError as error:
        st.session_state.pop("solution", None)
        st.error(str(error))

current_grid = None
try:
    current_grid = read_grid(editor_data, size)
except ValueError:
    pass

if (
    current_grid is not None
    and current_grid == st.session_state.get("solved_input")
    and st.session_state.get("solution") is not None
):
    st.subheader("Solved grid")
    st.dataframe(
        pd.DataFrame(st.session_state.solution),
        hide_index=True,
        use_container_width=True,
        column_config={
            column: st.column_config.NumberColumn(f"Column {column + 1}", format="%d")
            for column in range(size)
        },
    )
