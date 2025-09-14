import sys
import random
import math
import pygame

# =========================
# Arcade: Atari, Snake, Tic Tac Toe
# =========================

# ------------- Init -------------
pygame.init()
pygame.display.set_caption("Arcade: Atari, Snake, Tic Tac Toe")

# Window + fullscreen toggle
DEFAULT_SIZE = (1000, 700)
screen_flags = pygame.HWSURFACE | pygame.DOUBLEBUF
screen = pygame.display.set_mode(DEFAULT_SIZE, screen_flags)
clock = pygame.time.Clock()

# Fonts
font_title = pygame.font.SysFont("arial", 64, bold=True)
font_big = pygame.font.SysFont("arial", 40, bold=True)
font_med = pygame.font.SysFont("arial", 28, bold=True)
font_small = pygame.font.SysFont("consolas", 20)

# Colors
WHITE = (255, 255, 255)
BLACK = (10, 10, 12)
GRAY = (40, 44, 52)
DEEP = (22, 26, 34)
UI = (230, 235, 245)
ACCENT = (90, 170, 255)
ACCENT2 = (255, 100, 130)
GREEN = (0, 200, 0)
RED = (220, 70, 70)
BLUE = (80, 140, 255)
YELLOW = (240, 200, 80)

# ------------- Helpers -------------
def draw_text(surface, text, font, color, center=None, topleft=None):
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center is not None:
        rect.center = center
    elif topleft is not None:
        rect.topleft = topleft
    surface.blit(img, rect)
    return rect

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def toggle_fullscreen():
    global screen, screen_flags
    if screen.get_flags() & pygame.FULLSCREEN:
        screen_flags = pygame.HWSURFACE | pygame.DOUBLEBUF
        screen = pygame.display.set_mode(DEFAULT_SIZE, screen_flags)
    else:
        info = pygame.display.Info()
        screen_flags = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
        screen = pygame.display.set_mode((info.current_w, info.current_h), screen_flags)

# Simple starfield background for style
class Starfield:
    def __init__(self, count=180):
        w, h = screen.get_width(), screen.get_height()
        self.w, self.h = w, h
        self.stars = []
        for _ in range(count):
            x = random.uniform(0, w)
            y = random.uniform(0, h)
            speed = random.uniform(20, 120)
            size = random.randint(1, 2)
            self.stars.append([x, y, speed, size])

    def update(self, dt, speed_scale=1.0):
        w, h = screen.get_width(), screen.get_height()
        # Adapt to new size if changed
        if (self.w, self.h) != (w, h):
            self.w, self.h = w, h
        for s in self.stars:
            s[1] += s[2] * dt * speed_scale
            if s[1] > self.h + 5:
                s[0] = random.uniform(0, self.w)
                s[1] = -5

    def draw(self, surf):
        for x, y, _, size in self.stars:
            pygame.draw.rect(surf, (170, 185, 220), (int(x), int(y), size, size))

# ------------- Menu -------------
def draw_menu(starfield, t):
    screen.fill(BLACK)
    starfield.draw(screen)

    w, h = screen.get_width(), screen.get_height()
    draw_text(screen, "Anish Ka Arcade", font_title, UI, center=(w // 2, int(h * 0.20)))

    # Panel
    panel = pygame.Rect(w//2 - 420, int(h*0.30), 840, int(h*0.48))
    pygame.draw.rect(screen, DEEP, panel, border_radius=20)
    pygame.draw.rect(screen, (70, 80, 100), panel, width=2, border_radius=20)

    y = panel.y + 60
    draw_text(screen, "A - Atari Shooter", font_big, ACCENT, topleft=(panel.x + 60, y)); y += 70
    draw_text(screen, "S - Snake (1 grows, wall = death)", font_big, GREEN, topleft=(panel.x + 60, y)); y += 70
    draw_text(screen, "T - Tic Tac Toe (local 2P)", font_big, YELLOW, topleft=(panel.x + 60, y)); y += 70
    draw_text(screen, "Q - Quit", font_big, ACCENT2, topleft=(panel.x + 60, y))

    help1 = "F11: Fullscreen  •  M: Menu from any game  •  R: Restart (in game)"
    draw_text(screen, help1, font_small, UI, center=(w // 2, panel.bottom + 40))

# ------------- Atari shooter -------------
class AS_Player:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = screen.get_width() // 2
        self.y = screen.get_height() - 70
        self.speed = 620.0   # px/s
        self.cooldown = 0.0
        self.fire_cd = 0.18
        self.lives = 69
        self.score = 0
        self.invuln = 0.0

    def update(self, dt, keys):
        move = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move += 1
        self.x += move * self.speed * dt
        self.x = clamp(self.x, 30, screen.get_width() - 30)
        self.cooldown = max(0.0, self.cooldown - dt)
        self.invuln = max(0.0, self.invuln - dt)

    def can_fire(self):
        return self.cooldown <= 0.0

    def fire(self):
        self.cooldown = self.fire_cd
        return AS_Bullet(self.x, self.y - 22)

    def hit(self):
        if self.invuln > 0:
            return
        self.lives -= 1
        self.invuln = 1.0

    def draw(self, t):
        flick = 0.6 + 0.4 * math.sin(t * 7)
        col = (int(200*flick), int(230*flick), int(255*flick))
        pts = [
            (int(self.x), int(self.y - 18)),
            (int(self.x - 18), int(self.y + 18)),
            (int(self.x + 18), int(self.y + 18)),
        ]
        if self.invuln > 0 and int(t * 12) % 2 == 0:
            pygame.draw.polygon(screen, WHITE, pts, width=2)
        else:
            pygame.draw.polygon(screen, col, pts)

class AS_Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 900.0
        self.r = 4
        self.alive = True

    def update(self, dt):
        self.y -= self.speed * dt
        if self.y < -20:
            self.alive = False

    def draw(self):
        pygame.draw.circle(screen, ACCENT, (int(self.x), int(self.y)), self.r)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.r, 1)

class AS_Enemy:
    def __init__(self):
        self.x = random.uniform(40, screen.get_width() - 40)
        self.y = -30
        self.r = random.randint(12, 20)
        self.speed = random.uniform(150.0, 240.0)
        self.alive = True
        self.color = ACCENT2 if random.random() < 0.4 else YELLOW

    def update(self, dt):
        self.y += self.speed * dt
        self.x += math.sin(self.y * 0.02) * 50 * dt
        if self.y > screen.get_height() + 40:
            self.alive = False

    def draw(self, t):
        rect = pygame.Rect(int(self.x - self.r), int(self.y - self.r/2), int(self.r*2), int(self.r))
        dome = pygame.Rect(int(self.x - self.r/1.6), int(self.y - self.r), int(self.r*1.25), int(self.r))
        glow = (self.color[0], int(self.color[1]*0.7), int(self.color[2]*0.7))
        pygame.draw.ellipse(screen, glow, rect.inflate(10, 8), width=4)
        pygame.draw.ellipse(screen, self.color, rect)
        pygame.draw.ellipse(screen, (240, 240, 240), dome)
        if int(t*8) % 2 == 0:
            pygame.draw.ellipse(screen, WHITE, dome, 1)

def run_atari():
    star = Starfield(200)
    player = AS_Player()
    bullets = []
    enemies = []
    spawn_accum = 0.0
    score = 0
    paused = False
    t_global = 0.0

    while True:
        dt = clock.tick(60) / 1000.0
        t_global += dt
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_F11:
                    toggle_fullscreen()
                elif e.key == pygame.K_m:
                    return
                elif e.key in (pygame.K_ESCAPE, pygame.K_p):
                    paused = not paused
                elif e.key == pygame.K_r and not paused:
                    # quick restart
                    player = AS_Player()
                    bullets.clear()
                    enemies.clear()
                    score = 0

        if paused:
            # Draw paused overlay
            screen.fill(BLACK)
            star.draw(screen)
            draw_text(screen, "Paused", font_big, UI, center=(screen.get_width()//2, screen.get_height()//2 - 20))
            draw_text(screen, "P/Esc: Resume  •  M: Menu", font_med, UI, center=(screen.get_width()//2, screen.get_height()//2 + 30))
            pygame.display.flip()
            continue

        keys = pygame.key.get_pressed()

        # Update world
        star.update(dt, 1.0)
        player.update(dt, keys)

        if (keys[pygame.K_SPACE]) and player.can_fire():
            bullets.append(player.fire())

        for b in bullets:
            b.update(dt)
        bullets = [b for b in bullets if b.alive]

        spawn_accum += dt
        # Spawn approx every 0.7s scaled with time
        while spawn_accum >= 0.7:
            enemies.append(AS_Enemy())
            spawn_accum -= 0.7

        for en in enemies:
            en.update(dt)
        enemies = [e for e in enemies if e.alive]

        # Collisions: bullets vs enemies
        for en in enemies[:]:
            for b in bullets[:]:
                dx = en.x - b.x
                dy = en.y - b.y
                if dx*dx + dy*dy <= (en.r + b.r + 2)**2:
                    enemies.remove(en)
                    b.alive = False
                    score += 10
                    break

        # Collisions: enemies vs player
        for en in enemies[:]:
            dx = en.x - player.x
            dy = en.y - player.y
            if dx*dx + dy*dy <= (en.r + 18)**2:
                enemies.remove(en)
                player.hit()
                if player.lives <= 0:
                    # Game over screen
                    while True:
                        dt_go = clock.tick(60) / 1000.0
                        for e in pygame.event.get():
                            if e.type == pygame.QUIT:
                                pygame.quit(); sys.exit()
                            if e.type == pygame.KEYDOWN:
                                if e.key == pygame.K_m:
                                    return
                                if e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_r):
                                    player = AS_Player()
                                    bullets.clear()
                                    enemies.clear()
                                    score = 0
                                    break
                                if e.key == pygame.K_F11:
                                    toggle_fullscreen()
                        else:
                            # Draw game over
                            screen.fill(BLACK)
                            star.draw(screen)
                            draw_text(screen, "Game Over", font_title, ACCENT2, center=(screen.get_width()//2, int(screen.get_height()*0.35)))
                            draw_text(screen, f"Score: {score}", font_big, UI, center=(screen.get_width()//2, int(screen.get_height()*0.48)))
                            draw_text(screen, "Enter/Space/R: Restart   •   M: Menu", font_med, UI, center=(screen.get_width()//2, int(screen.get_height()*0.60)))
                            pygame.display.flip()
                            continue
                        break

        # Draw
        screen.fill(BLACK)
        star.draw(screen)
        # HUD bar
        pygame.draw.rect(screen, DEEP, (0, 0, screen.get_width(), 60))
        pygame.draw.line(screen, (70, 80, 100), (0, 60), (screen.get_width(), 60), 2)
        draw_text(screen, f"Score: {score}", font_med, UI, topleft=(16, 16))
        draw_text(screen, f"Lives: {player.lives}", font_med, UI, topleft=(180, 16))
        draw_text(screen, "M: Menu  •  Space: Shoot", font_small, UI, topleft=(screen.get_width() - 260, 20))

        for b in bullets: b.draw()
        for en in enemies: en.draw(t_global)
        player.draw(t_global)

        pygame.display.flip()

# ------------- Snake -------------
class SnakeGame:
    def __init__(self):
        self.cell = 25  # cell size
        self.reset()

    def grid_size(self):
        cols = screen.get_width() // self.cell
        rows = (screen.get_height() - 60) // self.cell  # reserve top HUD
        return cols, rows

    def reset(self):
        cols, rows = self.grid_size()
        self.snake = [(cols // 2, rows // 2)]
        self.dir = (1, 0)
        self.grow = 0
        self.alive = True
        self.spawn_food()
        self.score = 0

    def spawn_food(self):
        cols, rows = self.grid_size()
        while True:
            pos = (random.randint(0, cols - 1), random.randint(0, rows - 1))
            if pos not in self.snake:
                self.food = pos
                break

    def handle_key(self, key):
        if key == pygame.K_UP and self.dir != (0, 1): self.dir = (0, -1)
        elif key == pygame.K_DOWN and self.dir != (0, -1): self.dir = (0, 1)
        elif key == pygame.K_LEFT and self.dir != (1, 0): self.dir = (-1, 0)
        elif key == pygame.K_RIGHT and self.dir != (-1, 0): self.dir = (1, 0)
        elif key == pygame.K_1: self.grow += 1
        elif key == pygame.K_r and not self.alive: self.reset()

    def step(self):
        if not self.alive: return
        cols, rows = self.grid_size()
        hx, hy = self.snake[0]
        nx, ny = hx + self.dir[0], hy + self.dir[1]

        # Wall death
        if nx < 0 or nx >= cols or ny < 0 or ny >= rows:
            self.alive = False
            return

        if (nx, ny) in self.snake:
            self.alive = False
            return

        self.snake.insert(0, (nx, ny))

        if (nx, ny) == self.food:
            self.grow += 1
            self.score += 10
            self.spawn_food()

        if self.grow > 0:
            self.grow -= 1
        else:
            self.snake.pop()

    def draw(self):
        w = screen.get_width()
        h = screen.get_height()
        # HUD
        pygame.draw.rect(screen, DEEP, (0, 0, w, 60))
        pygame.draw.line(screen, (70, 80, 100), (0, 60), (w, 60), 2)
        draw_text(screen, f"Score: {self.score}", font_med, UI, topleft=(16, 16))
        draw_text(screen, "1: Grow  •  R: Restart  •  M: Menu", font_small, UI, topleft=(w - 300, 20))

        # Field
        field_rect = pygame.Rect(0, 60, w, h - 60)
        pygame.draw.rect(screen, (14, 16, 22), field_rect)

        # Grid (subtle)
        cols, rows = self.grid_size()
        for c in range(cols):
            x = c * self.cell
            pygame.draw.line(screen, (24, 28, 36), (x, 60), (x, h), 1)
        for r in range(rows + 1):
            y = 60 + r * self.cell
            pygame.draw.line(screen, (24, 28, 36), (0, y), (w, y), 1)

        # Food
        fx, fy = self.food
        pygame.draw.rect(screen, RED, (fx * self.cell, 60 + fy * self.cell, self.cell, self.cell))

        # Snake
        for i, (x, y) in enumerate(self.snake):
            col = GREEN if i == 0 else (0, 160, 0)
            rect = pygame.Rect(x * self.cell + 2, 60 + y * self.cell + 2, self.cell - 4, self.cell - 4)
            pygame.draw.rect(screen, col, rect, border_radius=6)

        if not self.alive:
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((10, 12, 18, 200))
            screen.blit(overlay, (0, 0))
            draw_text(screen, "Game Over!", font_big, UI, center=(w // 2, h // 2 - 20))
            draw_text(screen, "Press R to Restart or M for Menu", font_med, UI, center=(w // 2, h // 2 + 30))

def run_snake():
    game = SnakeGame()
    step_timer = 0.0
    step_interval = 0.11  # movement speed

    while True:
        dt = clock.tick(60) / 1000.0
        step_timer += dt

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_F11: toggle_fullscreen()
                elif e.key == pygame.K_m: return
                else: game.handle_key(e.key)

        if step_timer >= step_interval:
            game.step()
            step_timer = 0.0

        screen.fill(BLACK)
        game.draw()
        pygame.display.flip()

# ------------- Tic Tac Toe -------------        
class TicTacToe:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.turn = "X"
        self.winner = None
        self.moves = 0

    def handle_mouse(self, pos):
        if self.winner: return
        w, h = screen.get_width(), screen.get_height()
        cell_w = w // 3
        cell_h = (h - 60) // 3
        if pos[1] < 60:  # ignore HUD area
            return
        c = clamp(pos[0] // cell_w, 0, 2)
        r = clamp((pos[1] - 60) // cell_h, 0, 2)
        if self.board[r][c] == "":
            self.board[r][c] = self.turn
            self.moves += 1
            if self.check_win():
                self.winner = self.turn
            elif self.moves == 9:
                self.winner = "Draw"
            else:
                self.turn = "O" if self.turn == "X" else "X"

    def check_win(self):
        b = self.board
        lines = []
        for i in range(3):
            lines.append(b[i])
            lines.append([b[0][i], b[1][i], b[2][i]])
        lines.append([b[0][0], b[1][1], b[2][2]])
        lines.append([b[0][2], b[1][1], b[2][0]])
        for line in lines:
            if line[0] != "" and line[0] == line[1] == line[2]:
                return True
        return False

    def draw(self):
        w, h = screen.get_width(), screen.get_height()
        # HUD
        pygame.draw.rect(screen, DEEP, (0, 0, w, 60))
        pygame.draw.line(screen, (70, 80, 100), (0, 60), (w, 60), 2)
        status = f"Turn: {self.turn}" if not self.winner else (f"Winner: {self.winner}" if self.winner != "Draw" else "Draw!")
        draw_text(screen, status, font_med, UI, topleft=(16, 16))
        draw_text(screen, "Click to play  •  R: Restart  •  M: Menu", font_small, UI, topleft=(w - 320, 20))

        # Board
        cell_w = w // 3
        cell_h = (h - 60) // 3

        screen.fill((240, 242, 247), rect=pygame.Rect(0, 60, w, h - 60))

        # Grid lines
        for i in range(1, 3):
            pygame.draw.line(screen, BLACK, (i * cell_w, 60), (i * cell_w, h), 6)
            pygame.draw.line(screen, BLACK, (0, 60 + i * cell_h), (w, 60 + i * cell_h), 6)

        # Marks
        for r in range(3):
            for c in range(3):
                mark = self.board[r][c]
                if mark != "":
                    cx = c * cell_w + cell_w // 2
                    cy = 60 + r * cell_h + cell_h // 2
                    color = BLUE if mark == "X" else ACCENT2
                    draw_text(screen, mark, font_title, color, center=(cx, cy))

def run_tictactoe():
    game = TicTacToe()
    while True:
        dt = clock.tick(60) / 1000.0
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_F11: toggle_fullscreen()
                elif e.key == pygame.K_m: return
                elif e.key == pygame.K_r: game.reset()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                game.handle_mouse(pygame.mouse.get_pos())

        screen.fill(BLACK)
        game.draw()
        pygame.display.flip()

# ------------- Main -------------
def main():
    state = "menu"
    starfield = Starfield(220)
    t = 0.0

    while True:
        dt = clock.tick(60) / 1000.0
        t += dt

        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_F11:
                toggle_fullscreen()

        if state == "menu":
            for e in events:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_a:
                        run_atari()
                    elif e.key == pygame.K_s:
                        run_snake()
                    elif e.key == pygame.K_t:
                        run_tictactoe()
                    elif e.key == pygame.K_q:
                        pygame.quit(); sys.exit()

            starfield.update(dt, 0.7)
            draw_menu(starfield, t)
            pygame.display.flip()
        else:
            state = "menu"

if __name__ == "__main__":
    main()  
