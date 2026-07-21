import random
import tkinter as tk

COLS = 10
ROWS = 20
CELL = 28
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL
INITIAL_DELAY = 600

SHAPES = {
    "I": [[0, 0], [1, 0], [2, 0], [3, 0]],
    "O": [[0, 0], [1, 0], [0, 1], [1, 1]],
    "T": [[1, 0], [0, 1], [1, 1], [2, 1]],
    "S": [[1, 0], [2, 0], [0, 1], [1, 1]],
    "Z": [[0, 0], [1, 0], [1, 1], [2, 1]],
    "J": [[0, 0], [0, 1], [1, 1], [2, 1]],
    "L": [[2, 0], [0, 1], [1, 1], [2, 1]],
}

COLORS = {
    "I": "#00E5FF",
    "O": "#FFD700",
    "T": "#A855F7",
    "S": "#22C55E",
    "Z": "#EF4444",
    "J": "#3B82F6",
    "L": "#F59E0B",
}


class TetrisGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Tetris")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=WIDTH + 180, height=HEIGHT, bg="#111111", highlightthickness=0)
        self.canvas.pack()

        self.board = [[0] * COLS for _ in range(ROWS)]
        self.score = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        self.current_shape = None
        self.current_color = None
        self.piece = []
        self.piece_x = 0
        self.piece_y = 0
        self.drop_delay = INITIAL_DELAY

        self.bind_controls()
        self.spawn_piece()
        self.draw_all()
        self.root.after(self.drop_delay, self.tick)

    def bind_controls(self):
        self.root.bind("<Left>", lambda event: self.move_piece(-1))
        self.root.bind("<Right>", lambda event: self.move_piece(1))
        self.root.bind("<Down>", lambda event: self.soft_drop())
        self.root.bind("<Up>", lambda event: self.rotate_piece())
        self.root.bind("<space>", lambda event: self.hard_drop())
        self.root.bind("<p>", lambda event: self.toggle_pause())
        self.root.bind("<q>", lambda event: self.root.destroy())

    def spawn_piece(self):
        shape = random.choice(list(SHAPES.keys()))
        self.current_shape = shape
        self.current_color = COLORS[shape]
        self.piece = [list(cell) for cell in SHAPES[shape]]
        self.piece_x = COLS // 2 - 2
        self.piece_y = 0

        if self.is_collision(self.piece_x, self.piece_y, self.piece):
            self.game_over = True

    def move_piece(self, dx):
        if self.game_over or self.paused:
            return
        if not self.is_collision(self.piece_x + dx, self.piece_y, self.piece):
            self.piece_x += dx
            self.draw_all()

    def soft_drop(self):
        if self.game_over or self.paused:
            return
        if self.is_collision(self.piece_x, self.piece_y + 1, self.piece):
            self.lock_piece()
        else:
            self.piece_y += 1
            self.draw_all()

    def hard_drop(self):
        if self.game_over or self.paused:
            return
        while not self.is_collision(self.piece_x, self.piece_y + 1, self.piece):
            self.piece_y += 1
        self.lock_piece()

    def rotate_piece(self):
        if self.game_over or self.paused or self.current_shape == "O":
            return

        rotated = [[y, -x] for x, y in self.piece]
        min_x = min(x for x, _ in rotated)
        min_y = min(y for _, y in rotated)
        rotated = [[x - min_x, y - min_y] for x, y in rotated]

        for offset in (0, -1, 1, -2, 2):
            if not self.is_collision(self.piece_x + offset, self.piece_y, rotated):
                self.piece_x += offset
                self.piece = rotated
                self.draw_all()
                return

    def tick(self):
        if not self.game_over and not self.paused:
            if self.is_collision(self.piece_x, self.piece_y + 1, self.piece):
                self.lock_piece()
            else:
                self.piece_y += 1
                self.draw_all()
        self.root.after(self.drop_delay, self.tick)

    def lock_piece(self):
        for x, y in self.piece:
            nx = self.piece_x + x
            ny = self.piece_y + y
            if 0 <= ny < ROWS and 0 <= nx < COLS:
                self.board[ny][nx] = self.current_color

        self.clear_lines()
        self.spawn_piece()
        if self.is_collision(self.piece_x, self.piece_y, self.piece):
            self.game_over = True
        self.draw_all()

    def clear_lines(self):
        full_rows = [r for r, row in enumerate(self.board) if all(cell for cell in row)]
        if not full_rows:
            return

        for row in full_rows:
            del self.board[row]
            self.board.insert(0, [0] * COLS)

        self.score += len(full_rows) * 100
        self.level = 1 + self.score // 500
        self.drop_delay = max(120, INITIAL_DELAY - (self.level - 1) * 50)

    def is_collision(self, x, y, coords):
        for dx, dy in coords:
            nx = x + dx
            ny = y + dy
            if nx < 0 or nx >= COLS or ny >= ROWS:
                return True
            if 0 <= ny < ROWS and 0 <= nx < COLS and self.board[ny][nx] != 0:
                return True
        return False

    def toggle_pause(self):
        if self.game_over:
            return
        self.paused = not self.paused
        self.draw_all()

    def draw_all(self):
        self.canvas.delete("all")

        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#111111", outline="#222222")

        for row in range(ROWS):
            for col in range(COLS):
                x1 = col * CELL
                y1 = row * CELL
                x2 = x1 + CELL
                y2 = y1 + CELL
                if self.board[row][col] != 0:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.board[row][col], outline="#222222")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#1F1F1F", outline="#2A2A2A")

        for x, y in self.piece:
            tx = (self.piece_x + x) * CELL
            ty = (self.piece_y + y) * CELL
            self.canvas.create_rectangle(tx, ty, tx + CELL, ty + CELL, fill=self.current_color, outline="#222222")

        self.canvas.create_rectangle(WIDTH + 20, 20, WIDTH + 160, 160, fill="#181818", outline="#333333")
        self.canvas.create_text(WIDTH + 90, 45, text="Score", fill="white", font=("Arial", 12, "bold"))
        self.canvas.create_text(WIDTH + 90, 70, text=str(self.score), fill="white", font=("Arial", 16, "bold"))
        self.canvas.create_text(WIDTH + 90, 110, text="Level", fill="white", font=("Arial", 12, "bold"))
        self.canvas.create_text(WIDTH + 90, 135, text=str(self.level), fill="white", font=("Arial", 16, "bold"))

        if self.paused:
            self.canvas.create_text(WIDTH // 2, HEIGHT // 2, text="Paused", fill="white", font=("Arial", 24, "bold"))
        elif self.game_over:
            self.canvas.create_text(WIDTH // 2, HEIGHT // 2, text="Game Over", fill="#EF4444", font=("Arial", 24, "bold"))


if __name__ == "__main__":
    root = tk.Tk()
    game = TetrisGame(root)
    root.mainloop()
