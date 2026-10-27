from __future__ import annotations

import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


PROJECT_DIR = Path(__file__).parent
JAVA_SOLVER = PROJECT_DIR / "java" / "SudokuSolver.java"
JAVA_TIMEOUT_SECONDS = 30
MAX_REQUEST_BYTES = 16_384


def read_grid(value: Any, size: Any) -> list[list[int]]:
    if isinstance(size, bool) or not isinstance(size, int) or size not in (4, 9):
        raise ValueError("Grid size must be 4 or 9.")
    if not isinstance(value, list) or len(value) != size:
        raise ValueError(f"The grid must contain exactly {size} rows.")

    grid: list[list[int]] = []
    for row in value:
        if not isinstance(row, list) or len(row) != size:
            raise ValueError(f"Every row must contain exactly {size} cells.")
        parsed_row: list[int] = []
        for cell in row:
            if isinstance(cell, bool) or not isinstance(cell, int):
                raise ValueError(
                    "Every cell must contain a whole number from 0 to the grid size."
                )
            if not 0 <= cell <= size:
                raise ValueError(f"Cell values must be whole numbers from 0 to {size}.")
            parsed_row.append(cell)
        grid.append(parsed_row)
    return grid


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


class SudokuHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        assets = {
            "/": ("index.html", "text/html; charset=utf-8"),
            "/styles.css": ("styles.css", "text/css; charset=utf-8"),
            "/script.js": ("script.js", "text/javascript; charset=utf-8"),
        }
        asset = assets.get(self.path)
        if asset is None:
            self.send_error(404, "Not found")
            return

        filename, content_type = asset
        content = (PROJECT_DIR / filename).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self) -> None:
        if self.path != "/api/solve":
            self.send_error(404, "Not found")
            return
        if self.headers.get_content_type() != "application/json":
            self._send_json(415, {"error": "Content-Type must be application/json."})
            return

        content_length = self.headers.get("Content-Length")
        try:
            request_size = int(content_length) if content_length is not None else -1
        except ValueError:
            request_size = -1
        if request_size < 0:
            self._send_json(400, {"error": "A valid Content-Length is required."})
            return
        if request_size > MAX_REQUEST_BYTES:
            self._send_json(413, {"error": "The request is too large."})
            return

        try:
            payload = json.loads(self.rfile.read(request_size))
            if not isinstance(payload, dict):
                raise ValueError("The request must be a JSON object.")
            grid = read_grid(payload.get("grid"), payload.get("size"))
            solution = solve_with_java(grid)
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json(400, {"error": "The request body must contain valid JSON."})
            return
        except ValueError as error:
            self._send_json(400, {"error": str(error)})
            return
        except RuntimeError as error:
            self._send_json(500, {"error": str(error)})
            return

        self._send_json(200, {"solution": solution})

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        content = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("127.0.0.1", port), SudokuHandler)
    print(f"Mini Sudoku Solver is running at http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Mini Sudoku Solver.")
    finally:
        server.server_close()
