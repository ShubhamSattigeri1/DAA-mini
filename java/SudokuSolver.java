import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

public class SudokuSolver {
    public static void main(String[] args) throws Exception {
        if (args.length != 1) {
            fail("Invalid request: provide the grid size (4 or 9).");
            return;
        }

        int size;
        try {
            size = Integer.parseInt(args[0]);
        } catch (NumberFormatException exception) {
            fail("Invalid request: grid size must be 4 or 9.");
            return;
        }
        int boxSize = (int) Math.sqrt(size);
        if ((size != 4 && size != 9) || boxSize * boxSize != size) {
            fail("Invalid request: grid size must be 4 or 9.");
            return;
        }

        int[][] grid = readGrid(size);
        if (grid == null) {
            return;
        }

        boolean[][] rows = new boolean[size][size + 1];
        boolean[][] columns = new boolean[size][size + 1];
        boolean[][] boxes = new boolean[size][size + 1];
        if (!validateGrid(grid, size, boxSize, rows, columns, boxes)) {
            return;
        }

        if (!solve(grid, size, boxSize, rows, columns, boxes)) {
            fail("Unsolvable puzzle: no solution exists for this board.");
            return;
        }

        for (int[] row : grid) {
            for (int column = 0; column < size; column++) {
                if (column > 0) {
                    System.out.print(",");
                }
                System.out.print(row[column]);
            }
            System.out.println();
        }
    }

    private static int[][] readGrid(int size) throws Exception {
        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
        int[][] grid = new int[size][size];
        for (int row = 0; row < size; row++) {
            String line = reader.readLine();
            if (line == null) {
                fail("Invalid puzzle: expected " + size + " rows.");
                return null;
            }
            String[] values = line.split(",", -1);
            if (values.length != size) {
                fail("Invalid puzzle: each row must contain " + size + " values.");
                return null;
            }
            for (int column = 0; column < size; column++) {
                try {
                    grid[row][column] = Integer.parseInt(values[column].trim());
                } catch (NumberFormatException exception) {
                    fail("Invalid puzzle: every cell must be an integer.");
                    return null;
                }
                if (grid[row][column] < 0 || grid[row][column] > size) {
                    fail("Invalid puzzle: cell values must be from 0 to " + size + ".");
                    return null;
                }
            }
        }
        return grid;
    }

    private static boolean validateGrid(
            int[][] grid,
            int size,
            int boxSize,
            boolean[][] rows,
            boolean[][] columns,
            boolean[][] boxes) {
        for (int row = 0; row < size; row++) {
            for (int column = 0; column < size; column++) {
                int value = grid[row][column];
                if (value == 0) {
                    continue;
                }
                int box = boxIndex(row, column, boxSize);
                if (rows[row][value] || columns[column][value] || boxes[box][value]) {
                    fail("Invalid puzzle: a value is repeated in a row, column, or box.");
                    return false;
                }
                rows[row][value] = true;
                columns[column][value] = true;
                boxes[box][value] = true;
            }
        }
        return true;
    }

    private static boolean solve(
            int[][] grid,
            int size,
            int boxSize,
            boolean[][] rows,
            boolean[][] columns,
            boolean[][] boxes) {
        int bestRow = -1;
        int bestColumn = -1;
        List<Integer> bestCandidates = null;

        for (int row = 0; row < size; row++) {
            for (int column = 0; column < size; column++) {
                if (grid[row][column] != 0) {
                    continue;
                }
                List<Integer> candidates = candidates(
                        row, column, size, boxSize, rows, columns, boxes);
                if (bestCandidates == null || candidates.size() < bestCandidates.size()) {
                    bestRow = row;
                    bestColumn = column;
                    bestCandidates = candidates;
                }
                if (bestCandidates.isEmpty()) {
                    return false;
                }
            }
        }

        if (bestCandidates == null) {
            return true;
        }

        int box = boxIndex(bestRow, bestColumn, boxSize);
        for (int value : bestCandidates) {
            grid[bestRow][bestColumn] = value;
            rows[bestRow][value] = true;
            columns[bestColumn][value] = true;
            boxes[box][value] = true;
            if (solve(grid, size, boxSize, rows, columns, boxes)) {
                return true;
            }
            grid[bestRow][bestColumn] = 0;
            rows[bestRow][value] = false;
            columns[bestColumn][value] = false;
            boxes[box][value] = false;
        }
        return false;
    }

    private static List<Integer> candidates(
            int row,
            int column,
            int size,
            int boxSize,
            boolean[][] rows,
            boolean[][] columns,
            boolean[][] boxes) {
        List<Integer> values = new ArrayList<>();
        int box = boxIndex(row, column, boxSize);
        for (int value = 1; value <= size; value++) {
            if (!rows[row][value] && !columns[column][value] && !boxes[box][value]) {
                values.add(value);
            }
        }
        return values;
    }

    private static int boxIndex(int row, int column, int boxSize) {
        return (row / boxSize) * boxSize + column / boxSize;
    }

    private static void fail(String message) {
        System.err.println(message);
        System.exit(2);
    }
}
