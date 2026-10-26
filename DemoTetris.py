import tkinter as tk
import random

COLS, ROWS, CELL = 10, 20, 30

SHAPES = {
    "I": [[1, 1, 1, 1]],
    "O": [[1, 1], [1, 1]],
    "T": [[0, 1, 0], [1, 1, 1]],
    "S": [[0, 1, 1], [1, 1, 0]],
    "Z": [[1, 1, 0], [0, 1, 1]],
    "J": [[1, 0, 0], [1, 1, 1]],
    "L": [[0, 0, 1], [1, 1, 1]],
}
COLORS = {
    "I": "cyan", "O": "yellow", "T": "purple",
    "S": "green", "Z": "red", "J": "blue", "L": "orange",
}


def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]


class Tetris:
    def __init__(self, root):
        self.root = root
        root.title("테트리스")
        root.resizable(False, False)

        self.info = tk.Label(root, font=("맑은 고딕", 12))
        self.info.pack()
        self.canvas = tk.Canvas(root, width=COLS * CELL, height=ROWS * CELL, bg="black")
        self.canvas.pack()

        root.bind("<Left>", lambda e: self.move(-1, 0))
        root.bind("<Right>", lambda e: self.move(1, 0))
        root.bind("<Down>", lambda e: self.move(0, 1))
        root.bind("<Up>", lambda e: self.rotate_piece())
        root.bind("<space>", lambda e: self.hard_drop())
        root.bind("<r>", lambda e: self.reset())
        root.bind("<p>", lambda e: self.toggle_pause())

        self.reset()

    def reset(self):
        self.board = [[None] * COLS for _ in range(ROWS)]
        self.score = 0
        self.lines = 0
        self.game_over = False
        self.paused = False
        self.spawn()
        if getattr(self, "job", None):
            self.root.after_cancel(self.job)
        self.tick()

    def spawn(self):
        self.kind = random.choice(list(SHAPES))
        self.shape = [row[:] for row in SHAPES[self.kind]]
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0
        if self.collides(self.shape, self.x, self.y):
            self.game_over = True

    def collides(self, shape, x, y):
        for r, row in enumerate(shape):
            for c, v in enumerate(row):
                if not v:
                    continue
                nx, ny = x + c, y + r
                if nx < 0 or nx >= COLS or ny >= ROWS:
                    return True
                if ny >= 0 and self.board[ny][nx]:
                    return True
        return False

    def move(self, dx, dy):
        if self.game_over or self.paused:
            return False
        if not self.collides(self.shape, self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
            self.draw()
            return True
        return False

    def rotate_piece(self):
        if self.game_over or self.paused:
            return
        new = rotate(self.shape)
        for kick in (0, -1, 1, -2, 2):
            if not self.collides(new, self.x + kick, self.y):
                self.shape = new
                self.x += kick
                break
        self.draw()

    def hard_drop(self):
        if self.game_over or self.paused:
            return
        while self.move(0, 1):
            pass
        self.lock()

    def toggle_pause(self):
        if not self.game_over:
            self.paused = not self.paused
            self.draw()

    def lock(self):
        for r, row in enumerate(self.shape):
            for c, v in enumerate(row):
                if v and self.y + r >= 0:
                    self.board[self.y + r][self.x + c] = COLORS[self.kind]
        self.clear_lines()
        self.spawn()
        self.draw()

    def clear_lines(self):
        remain = [row for row in self.board if not all(row)]
        cleared = ROWS - len(remain)
        if cleared:
            self.board = [[None] * COLS for _ in range(cleared)] + remain
            self.lines += cleared
            self.score += {1: 100, 2: 300, 3: 500, 4: 800}[cleared]

    def tick(self):
        if not self.game_over and not self.paused:
            if not self.move(0, 1):
                self.lock()
        self.draw()
        delay = max(100, 500 - (self.lines // 10) * 40)
        self.job = self.root.after(delay, self.tick)

    def cell(self, c, r, color):
        self.canvas.create_rectangle(
            c * CELL, r * CELL, (c + 1) * CELL, (r + 1) * CELL,
            fill=color, outline="gray20")

    def draw(self):
        self.canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                if self.board[r][c]:
                    self.cell(c, r, self.board[r][c])
        if not self.game_over:
            for r, row in enumerate(self.shape):
                for c, v in enumerate(row):
                    if v:
                        self.cell(self.x + c, self.y + r, COLORS[self.kind])
        self.info.config(text=f"점수: {self.score}   라인: {self.lines}")
        if self.game_over or self.paused:
            msg = "GAME OVER\n(R: 재시작)" if self.game_over else "일시정지"
            self.canvas.create_text(COLS * CELL // 2, ROWS * CELL // 2, text=msg,
                                    fill="white", font=("맑은 고딕", 20, "bold"),
                                    justify="center")


if __name__ == "__main__":
    root = tk.Tk()
    Tetris(root)
    root.mainloop()
