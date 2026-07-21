import random
import tkinter as tk


class BreakoutGame:
    def __init__(self, root):
        self.root = root
        self.root.title("블록 깨기")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=480, height=620, bg="#111111", highlightthickness=0)
        self.canvas.pack()

        self.canvas.create_text(240, 20, text="블록 깨기", fill="white", font=("Arial", 16, "bold"))
        self.score_text = self.canvas.create_text(80, 20, text="점수: 0", fill="#ffd54f", font=("Arial", 12, "bold"))
        self.life_text = self.canvas.create_text(400, 20, text="생명: 3", fill="#ff8a80", font=("Arial", 12, "bold"))
        self.message_text = self.canvas.create_text(240, 300, text="", fill="#ffffff", font=("Arial", 18, "bold"))

        self.paddle_width = 180
        self.paddle = self.canvas.create_rectangle(150, 560, 330, 580, fill="#ffffff", outline="")
        self.ball = self.canvas.create_oval(230, 300, 250, 320, fill="#ffd54f", outline="")

        self.bricks = []
        self.items = []
        self.bullets = []
        self.create_bricks()

        self.score = 0
        self.lives = 3
        self.ball_speed_x = 9
        self.ball_speed_y = -9
        self.running = True
        self.can_shoot = False

        self.canvas.focus_set()
        self.canvas.bind("<Left>", lambda event: self.move_paddle(-20))
        self.canvas.bind("<Right>", lambda event: self.move_paddle(20))
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<KeyPress-space>", lambda event: self.shoot() if self.running and self.can_shoot else self.restart_game())

        self.update_status()
        self.game_loop()

    def create_bricks(self):
        colors = ["#ff6f61", "#ffb74d", "#ffee58", "#81c784", "#64b5f6"]
        for row in range(5):
            for col in range(8):
                x1 = 20 + col * 55
                y1 = 80 + row * 25
                x2 = x1 + 45
                y2 = y1 + 18
                brick = self.canvas.create_rectangle(x1, y1, x2, y2, fill=colors[row % len(colors)], outline="")
                self.bricks.append(brick)

    def update_status(self):
        self.canvas.itemconfig(self.score_text, text=f"점수: {self.score}")
        self.canvas.itemconfig(self.life_text, text=f"생명: {self.lives}")

    def move_paddle(self, delta):
        x1, y1, x2, y2 = self.canvas.coords(self.paddle)
        paddle_width = x2 - x1
        new_x1 = max(0, min(480 - paddle_width, x1 + delta))
        self.canvas.coords(self.paddle, new_x1, y1, new_x1 + paddle_width, y2)

    def on_mouse_move(self, event):
        if event.x < 40:
            self.move_paddle(-20)
        elif event.x > 440:
            self.move_paddle(20)
        else:
            paddle_width = self.paddle_width
            x1 = event.x - paddle_width // 2
            x2 = x1 + paddle_width
            if x1 < 0:
                x1 = 0
                x2 = paddle_width
            if x2 > 480:
                x2 = 480
                x1 = 480 - paddle_width
            self.canvas.coords(self.paddle, x1, 560, x2, 580)

    def create_item(self, x, y):
        if random.random() < 0.25:
            item_id = self.canvas.create_rectangle(x - 8, y - 8, x + 8, y + 8, fill="#76ff03", outline="")
            self.items.append((item_id, "shoot"))

    def shoot(self):
        if not self.running or not self.can_shoot:
            return
        paddle_x1, paddle_y1, paddle_x2, paddle_y2 = self.canvas.coords(self.paddle)
        center_x = (paddle_x1 + paddle_x2) / 2
        bullet_id = self.canvas.create_oval(center_x - 3, paddle_y1 - 8, center_x + 3, paddle_y1 - 2, fill="#ffeb3b", outline="")
        self.bullets.append(bullet_id)

    def move_items(self):
        for item_data in list(self.items):
            item_id, _ = item_data
            x1, y1, x2, y2 = self.canvas.coords(item_id)
            y1 += 3
            y2 += 3
            self.canvas.coords(item_id, x1, y1, x2, y2)

            paddle_x1, paddle_y1, paddle_x2, paddle_y2 = self.canvas.coords(self.paddle)
            if x2 >= paddle_x1 and x1 <= paddle_x2 and y2 >= paddle_y1 and y1 <= paddle_y2:
                self.canvas.delete(item_id)
                self.items.remove(item_data)
                self.can_shoot = True
            elif y2 > 620:
                self.canvas.delete(item_id)
                self.items.remove(item_data)

    def move_bullets(self):
        for bullet_id in list(self.bullets):
            x1, y1, x2, y2 = self.canvas.coords(bullet_id)
            y1 -= 8
            y2 -= 8
            self.canvas.coords(bullet_id, x1, y1, x2, y2)

            if y2 < 0:
                self.canvas.delete(bullet_id)
                self.bullets.remove(bullet_id)
                continue

            for brick in list(self.bricks):
                bx1, by1, bx2, by2 = self.canvas.coords(brick)
                if x2 >= bx1 and x1 <= bx2 and y2 >= by1 and y1 <= by2:
                    self.canvas.delete(brick)
                    self.bricks.remove(brick)
                    self.score += 10
                    self.update_status()
                    self.canvas.delete(bullet_id)
                    self.bullets.remove(bullet_id)
                    break

    def restart_game(self):
        if self.running:
            return
        self.score = 0
        self.lives = 3
        self.ball_speed_x = 9
        self.ball_speed_y = -9
        self.can_shoot = False
        self.items = []
        self.bullets = []
        self.canvas.delete("all")
        self.canvas.create_text(240, 20, text="블록 깨기", fill="white", font=("Arial", 16, "bold"))
        self.score_text = self.canvas.create_text(80, 20, text="점수: 0", fill="#ffd54f", font=("Arial", 12, "bold"))
        self.life_text = self.canvas.create_text(400, 20, text="생명: 3", fill="#ff8a80", font=("Arial", 12, "bold"))
        self.message_text = self.canvas.create_text(240, 300, text="", fill="#ffffff", font=("Arial", 18, "bold"))
        self.paddle_width = 180
        self.paddle = self.canvas.create_rectangle(150, 560, 330, 580, fill="#ffffff", outline="")
        self.ball = self.canvas.create_oval(230, 300, 250, 320, fill="#ffd54f", outline="")
        self.bricks = []
        self.create_bricks()
        self.update_status()
        self.running = True
        self.game_loop()

    def game_loop(self):
        if not self.running:
            return

        self.move_ball()
        self.move_items()
        self.move_bullets()
        self.root.after(16, self.game_loop)

    def move_ball(self):
        x1, y1, x2, y2 = self.canvas.coords(self.ball)
        x1 += self.ball_speed_x
        y1 += self.ball_speed_y
        x2 += self.ball_speed_x
        y2 += self.ball_speed_y

        if x1 <= 0 or x2 >= 480:
            self.ball_speed_x *= -1
            x1 = max(0, x1)
            x2 = min(480, x2)

        if y1 <= 0:
            self.ball_speed_y *= -1
            y1 = max(0, y1)
            y2 = max(0, y2)

        paddle_x1, paddle_y1, paddle_x2, paddle_y2 = self.canvas.coords(self.paddle)
        if y2 >= paddle_y1 and y1 <= paddle_y2 and x2 >= paddle_x1 and x1 <= paddle_x2:
            self.ball_speed_y *= -1
            self.ball_speed_x += (x1 + (x2 - x1) / 2 - (paddle_x1 + (paddle_x2 - paddle_x1) / 2)) / 80
            y2 = paddle_y1
            y1 = y2 - (y2 - y1)

        self.canvas.coords(self.ball, x1, y1, x2, y2)

        for brick in list(self.bricks):
            bx1, by1, bx2, by2 = self.canvas.coords(brick)
            if x2 >= bx1 and x1 <= bx2 and y2 >= by1 and y1 <= by2:
                self.canvas.delete(brick)
                self.bricks.remove(brick)
                self.score += 10
                self.update_status()
                self.create_item((bx1 + bx2) / 2, (by1 + by2) / 2)
                self.ball_speed_y *= -1
                break

        if y2 > 620:
            self.lives -= 1
            self.update_status()
            if self.lives <= 0:
                self.game_over("게임 오버! 스페이스로 다시 시작")
            else:
                self.reset_ball()

        if not self.bricks:
            self.game_over("축하합니다! 모든 블록을 깨셨습니다!")

    def reset_ball(self):
        self.canvas.coords(self.ball, 230, 300, 250, 320)
        self.ball_speed_x = 9
        self.ball_speed_y = -9

    def game_over(self, message):
        self.running = False
        self.canvas.itemconfig(self.message_text, text=message)


if __name__ == "__main__":
    root = tk.Tk()
    game = BreakoutGame(root)
    root.mainloop()
