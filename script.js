const EXAMPLE_BOARDS = {
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
};

const puzzleBoard = document.querySelector("#puzzle-board");
const solutionBoard = document.querySelector("#solution-board");
const solutionSection = document.querySelector("#solution-section");
const solverAnimation = document.querySelector("#solver-animation");
const boardWrap = document.querySelector("#puzzle-board").parentElement;
const solveButton = document.querySelector("#solve-button");
const gridSizeSelect = document.querySelector("#grid-size");
const loadExampleButton = document.querySelector("#load-example");
const statusMessage = document.querySelector("#status-message");

function clearResult() {
  solverAnimation.hidden = true;
  boardWrap.removeAttribute("aria-busy");
  solutionSection.hidden = true;
  solutionBoard.replaceChildren();
  statusMessage.textContent = "";
  statusMessage.className = "status-message";
}

function renderBoard(container, grid, readOnly = false) {
  const size = grid.length;
  const boxSize = Math.sqrt(size);
  container.replaceChildren();
  container.style.setProperty("--size", size);

  grid.forEach((row, rowIndex) => {
    row.forEach((value, columnIndex) => {
      const input = document.createElement("input");
      input.className = "cell";
      input.type = "number";
      input.min = "0";
      input.max = String(size);
      input.step = "1";
      input.value = String(value);
      input.inputMode = "numeric";
      input.setAttribute(
        "aria-label",
        `Row ${rowIndex + 1}, column ${columnIndex + 1}`,
      );
      if (columnIndex < size - 1 && (columnIndex + 1) % boxSize === 0) {
        input.classList.add("box-right");
      }
      if (rowIndex < size - 1 && (rowIndex + 1) % boxSize === 0) {
        input.classList.add("box-bottom");
      }
      if (readOnly) {
        input.readOnly = true;
        input.tabIndex = -1;
      } else {
        input.required = true;
        input.addEventListener("input", clearResult);
      }
      container.append(input);
    });
  });
}

function loadExample() {
  const size = Number(gridSizeSelect.value);
  renderBoard(puzzleBoard, EXAMPLE_BOARDS[size]);
  clearResult();
}

function readPuzzle() {
  const size = Number(gridSizeSelect.value);
  const inputs = [...puzzleBoard.querySelectorAll("input")];
  const values = inputs.map((input) => {
    if (input.value.trim() === "") {
      throw new Error("Every cell must contain a whole number from 0 to the grid size.");
    }
    const value = Number(input.value);
    if (!Number.isInteger(value)) {
      throw new Error("Every cell must contain a whole number from 0 to the grid size.");
    }
    if (value < 0 || value > size) {
      throw new Error(`Cell values must be whole numbers from 0 to ${size}.`);
    }
    return value;
  });

  return Array.from({ length: size }, (_, row) =>
    values.slice(row * size, (row + 1) * size),
  );
}

function showStatus(message, isError = false) {
  statusMessage.textContent = message;
  statusMessage.className = isError
    ? "status-message status-error"
    : "status-message status-success";
}

async function solvePuzzle() {
  clearResult();
  let grid;
  try {
    grid = readPuzzle();
  } catch (error) {
    showStatus(error.message, true);
    return;
  }

  solveButton.disabled = true;
  gridSizeSelect.disabled = true;
  loadExampleButton.disabled = true;
  puzzleBoard.querySelectorAll("input").forEach((input) => {
    input.disabled = true;
  });
  solverAnimation.hidden = false;
  boardWrap.setAttribute("aria-busy", "true");
  solveButton.textContent = "Solving…";
  try {
    const response = await fetch("/api/solve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ size: grid.length, grid }),
    });
    const result = await response.json();
    if (!response.ok) {
      showStatus(result.error || "The puzzle could not be solved.", true);
      return;
    }
    renderBoard(solutionBoard, result.solution, true);
    solutionSection.hidden = false;
    showStatus("Puzzle solved.");
  } catch (error) {
    showStatus(
      error instanceof TypeError
        ? "Could not reach the local solver. Make sure the Python server is running."
        : error.message || "The local solver returned an invalid response.",
      true,
    );
  } finally {
    solveButton.disabled = false;
    gridSizeSelect.disabled = false;
    loadExampleButton.disabled = false;
    puzzleBoard.querySelectorAll("input").forEach((input) => {
      input.disabled = false;
    });
    solverAnimation.hidden = true;
    boardWrap.removeAttribute("aria-busy");
    solveButton.textContent = "Solve puzzle";
  }
}

function selectTab(activeTab, activePanel, inactiveTab, inactivePanel) {
  activeTab.setAttribute("aria-selected", "true");
  inactiveTab.setAttribute("aria-selected", "false");
  activePanel.hidden = false;
  inactivePanel.hidden = true;
}

gridSizeSelect.addEventListener("change", loadExample);
document.querySelector("#load-example").addEventListener("click", loadExample);
solveButton.addEventListener("click", solvePuzzle);
document.querySelector("#solver-tab").addEventListener("click", () => {
  selectTab(
    document.querySelector("#solver-tab"),
    document.querySelector("#solver-panel"),
    document.querySelector("#details-tab"),
    document.querySelector("#details-panel"),
  );
});
document.querySelector("#details-tab").addEventListener("click", () => {
  selectTab(
    document.querySelector("#details-tab"),
    document.querySelector("#details-panel"),
    document.querySelector("#solver-tab"),
    document.querySelector("#solver-panel"),
  );
});

loadExample();
