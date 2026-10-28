#cmd 
#pip install pygame
import sys
import math
import array
import random
import pygame

WIDTH, HEIGHT = 800, 600
FPS = 60

PADDLE_W, PADDLE_H = 330, 14
BALL_R = 8
BLOCK_ROWS, BLOCK_COLS = 6, 10
BLOCK_W, BLOCK_H = 70, 24
BLOCK_GAP = 6
TOP_OFFSET = 70

def rainbow(hue):
    color = pygame.Color(0)
    color.hsva = (hue % 360, 90, 100, 100)
    return (color.r, color.g, color.b)


ITEM_CHANCE = 0.3
ITEM_SPEED = 3
AMMO_PER_ITEM = 15
BULLET_SPEED = 12
BULLET_W, BULLET_H = 4, 14


def make_sound(freqs, duration=0.12, volume=0.4, rate=22050):
    """주파수 목록을 이어붙인 간단한 효과음을 합성한다."""
    samples = array.array("h")
    n = int(rate * duration / len(freqs))
    for f in freqs:
        for i in range(n):
            fade = 1 - i / n
            v = math.sin(2 * math.pi * f * i / rate) * fade * volume
            samples.append(int(v * 32767))
    return pygame.mixer.Sound(buffer=samples.tobytes())


def build_sounds():
    try:
        pygame.mixer.init(frequency=22050, size=-16, channels=1)
        return {
            "paddle": make_sound([440], 0.08),
            "wall": make_sound([300], 0.06),
            "block": make_sound([660, 880], 0.1),
            "item": make_sound([523, 659, 784, 1047], 0.25),
            "shoot": make_sound([1200, 600], 0.08, 0.3),
            "life": make_sound([300, 200, 120], 0.35),
            "win": make_sound([523, 659, 784, 1047, 1319], 0.6),
            "over": make_sound([400, 300, 200, 100], 0.6),
        }
    except pygame.error:
        return {}


def build_blocks():
    total_w = BLOCK_COLS * BLOCK_W + (BLOCK_COLS - 1) * BLOCK_GAP
    left = (WIDTH - total_w) // 2
    blocks = []
    for r in range(BLOCK_ROWS):
        for c in range(BLOCK_COLS):
            rect = pygame.Rect(left + c * (BLOCK_W + BLOCK_GAP),
                               TOP_OFFSET + r * (BLOCK_H + BLOCK_GAP),
                               BLOCK_W, BLOCK_H)
            hue = (r * 40 + c * 36) % 360
            blocks.append((rect, rainbow(hue)))
    return blocks


def reset_ball(paddle):
    ball = pygame.Rect(0, 0, BALL_R * 2, BALL_R * 2)
    ball.midbottom = (paddle.centerx, paddle.top - 2)
    return ball


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("블럭깨기 - DemoBlock")
    clock = pygame.time.Clock()

    fonts = ["malgungothic", "applegothic", "nanumgothic", "arial"]
    font = pygame.font.SysFont(fonts, 24)
    big = pygame.font.SysFont(fonts, 48, bold=True)

    def new_game():
        paddle = pygame.Rect((WIDTH - PADDLE_W) // 2, HEIGHT - 40, PADDLE_W, PADDLE_H)
        return paddle, reset_ball(paddle), build_blocks(), 0, 3

    sounds = build_sounds()

    def play(name):
        if name in sounds:
            sounds[name].play()

    paddle, ball, blocks, score, lives = new_game()
    speed = 6.0
    items = []
    bullets = []
    ammo = 0

    def break_block(i):
        nonlocal score, speed
        rect = blocks[i][0]
        del blocks[i]
        score += 10
        speed = min(speed + 0.05, 11)
        play("block")
        if random.random() < ITEM_CHANCE:
            items.append(pygame.Rect(rect.centerx - 14, rect.centery - 10, 28, 20))

    vx = vy = 0.0
    bx, by = float(ball.x), float(ball.y)
    launched = False
    state = "play"  # play / win / over

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                if state != "play":
                    paddle, ball, blocks, score, lives = new_game()
                    speed, launched, state = 6.0, False, "play"
                    items.clear()
                    bullets.clear()
                    ammo = 0
                elif not launched:
                    launched = True
                    vx = random.choice([-1, 1]) * speed * 0.6
                    vy = -speed * 0.8
                    bx, by = float(ball.x), float(ball.y)
                elif ammo > 0:
                    ammo -= 1
                    for x in (paddle.left + 12, paddle.right - 12):
                        bullets.append(pygame.Rect(x - BULLET_W // 2, paddle.top - BULLET_H,
                                                   BULLET_W, BULLET_H))
                    play("shoot")

        if state == "play":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                paddle.x -= 9
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                paddle.x += 9
            paddle.clamp_ip(screen.get_rect())

            if not launched:
                ball = reset_ball(paddle)
                bx, by = float(ball.x), float(ball.y)
            else:
                bx += vx
                by += vy
                ball.x, ball.y = round(bx), round(by)

                if ball.left <= 0:
                    ball.left, bx, vx = 0, 0.0, abs(vx)
                    play("wall")
                elif ball.right >= WIDTH:
                    ball.right = WIDTH
                    bx, vx = float(ball.x), -abs(vx)
                    play("wall")
                if ball.top <= 0:
                    ball.top, by, vy = 0, 0.0, abs(vy)
                    play("wall")

                if ball.colliderect(paddle) and vy > 0:
                    play("paddle")
                    offset = (ball.centerx - paddle.centerx) / (PADDLE_W / 2)
                    offset = max(-0.9, min(0.9, offset))
                    vx = speed * offset * 1.1
                    vy = -(max(speed ** 2 - vx ** 2, 4)) ** 0.5
                    ball.bottom = paddle.top
                    by = float(ball.y)

                for i, (rect, _) in enumerate(blocks):
                    if ball.colliderect(rect):
                        ox = min(ball.right - rect.left, rect.right - ball.left)
                        oy = min(ball.bottom - rect.top, rect.bottom - ball.top)
                        if ox < oy:
                            vx = -vx
                        else:
                            vy = -vy
                        break_block(i)
                        break

                if ball.top > HEIGHT:
                    lives -= 1
                    launched = False
                    play("life")
                    if lives <= 0:
                        state = "over"
                        play("over")

            for item in items[:]:
                item.y += ITEM_SPEED
                if item.colliderect(paddle):
                    items.remove(item)
                    ammo += AMMO_PER_ITEM
                    score += 5
                    play("item")
                elif item.top > HEIGHT:
                    items.remove(item)

            for bullet in bullets[:]:
                bullet.y -= BULLET_SPEED
                hit = bullet.collidelist([b[0] for b in blocks])
                if hit != -1:
                    bullets.remove(bullet)
                    break_block(hit)
                elif bullet.bottom < 0:
                    bullets.remove(bullet)

            if not blocks and state == "play":
                state = "win"
                play("win")

        screen.fill((20, 22, 35))
        for rect, color in blocks:
            pygame.draw.rect(screen, color, rect, border_radius=4)
            shine = pygame.Rect(rect.x + 3, rect.y + 2, rect.w - 6, rect.h // 3)
            light = tuple(min(255, v + 90) for v in color)
            pygame.draw.rect(screen, light, shine, border_radius=3)
            pygame.draw.rect(screen, (255, 255, 255), rect, 1, border_radius=4)
        pygame.draw.rect(screen, (236, 240, 241), paddle, border_radius=6)
        pygame.draw.circle(screen, (255, 255, 255), ball.center, BALL_R)
        for item in items:
            pygame.draw.rect(screen, (255, 215, 0), item, border_radius=8)
            pygame.draw.rect(screen, (255, 255, 255), item, 2, border_radius=8)
            tag = font.render("G", True, (120, 40, 0))
            screen.blit(tag, tag.get_rect(center=item.center))
        for bullet in bullets:
            pygame.draw.rect(screen, (255, 80, 80), bullet, border_radius=2)
        screen.blit(font.render(f"Score: {score}   Ammo: {ammo}", True, (255, 255, 255)), (15, 15))
        lt = font.render(f"Lives: {lives}", True, (255, 255, 255))
        screen.blit(lt, (WIDTH - lt.get_width() - 15, 15))

        if state == "play" and not launched:
            msg = font.render("SPACE: 발사  |  ←/→: 이동", True, (200, 200, 200))
            screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60)))
        elif state != "play":
            title = "YOU WIN!" if state == "win" else "GAME OVER"
            t = big.render(title, True, (241, 196, 15))
            screen.blit(t, t.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            m = font.render("SPACE: 다시 시작  |  ESC: 종료", True, (200, 200, 200))
            screen.blit(m, m.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
