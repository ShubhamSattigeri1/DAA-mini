# Mini Sudoku Solver

A Streamlit interface for 4×4 and 9×9 Sudoku puzzles, backed by a Java
backtracking solver. The frontend passes the grid to the Java program through
standard input and displays the returned solution.

## Requirements

- Python 3.9 or newer
- Java Development Kit (JDK) 11 or newer, with `java` available on `PATH`

## Setup

From the project directory, create and activate a virtual environment, then
install the Python dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Check that Java is installed:

```powershell
java -version
```

No separate Java build step is needed; Java 11+ runs `java/SudokuSolver.java`
directly.

## Run

Start the Streamlit app from the project directory:

```powershell
python -m streamlit run app.py
```

Choose a 4×4 or 9×9 grid, enter values from `1` through the selected size, and
leave empty cells as `0`. Use **Load example puzzle** to restore the example,
then select **Solve**. Duplicate values, malformed input, unsolvable puzzles,
missing Java, and solver failures are reported in the interface.

## Run the Java backend directly

The backend accepts the grid size as its argument and comma-separated rows on
standard input. For example, from PowerShell:

```powershell
@"
5,3,0,0,7,0,0,0,0
6,0,0,1,9,5,0,0,0
0,9,8,0,0,0,0,6,0
8,0,0,0,6,0,0,0,3
4,0,0,8,0,3,0,0,1
7,0,0,0,2,0,0,0,6
0,6,0,0,0,0,2,8,0
0,0,0,4,1,9,0,0,5
0,0,0,0,8,0,0,7,9
"@ | java .\java\SudokuSolver.java 9
```
