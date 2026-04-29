import sys
import random
import pygame

# --- Config ---
WIDTH, HEIGHT = 960, 540
FPS = 60
GRAVITY = 0.8
PLAYER_SPEED = 5
JUMP_VELOCITY = -15

SKY_BLUE = (107, 182, 255)
GROUND_BROWN = (110, 76, 48)
GREEN = (80, 200, 120)
RED = (220, 60, 60)
YELLOW = (255, 220, 50)
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)


class Platform:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, screen, camera_x):
        pygame.draw.rect(screen, GROUND_BROWN, (self.rect.x - camera_x, self.rect.y, self.rect.w, self.rect.h), border_radius=4)
        pygame.draw.rect(screen, GREEN, (self.rect.x - camera_x, self.rect.y, self.rect.w, 8), border_radius=4)


class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.collected = False

    def draw(self, screen, camera_x):
        if not self.collected:
            pygame.draw.ellipse(screen, YELLOW, (self.rect.x - camera_x, self.rect.y, self.rect.w, self.rect.h))
            pygame.draw.ellipse(screen, BLACK, (self.rect.x - camera_x, self.rect.y, self.rect.w, self.rect.h), 2)


class Enemy:
    def __init__(self, x, y, left_bound, right_bound):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.vx = 2
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.alive = True

    def update(self):
        if not self.alive:
            return
        self.rect.x += self.vx
        if self.rect.left <= self.left_bound or self.rect.right >= self.right_bound:
            self.vx *= -1

    def draw(self, screen, camera_x):
        if self.alive:
            pygame.draw.rect(screen, RED, (self.rect.x - camera_x, self.rect.y, self.rect.w, self.rect.h), border_radius=6)
            pygame.draw.circle(screen, BLACK, (self.rect.x - camera_x + 9, self.rect.y + 12), 3)
            pygame.draw.circle(screen, BLACK, (self.rect.x - camera_x + 23, self.rect.y + 12), 3)


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 34, 48)
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.facing_right = True
        self.score = 0
        self.lives = 3

    def handle_input(self, keys):
        self.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -PLAYER_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = PLAYER_SPEED
            self.facing_right = True

    def jump(self):
        if self.on_ground:
            self.vy = JUMP_VELOCITY
            self.on_ground = False

    def apply_gravity(self):
        self.vy += GRAVITY
        if self.vy > 20:
            self.vy = 20

    def move_and_collide(self, platforms):
        # Horizontal
        self.rect.x += self.vx
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vx > 0:
                    self.rect.right = p.rect.left
                elif self.vx < 0:
                    self.rect.left = p.rect.right

        # Vertical
        self.rect.y += int(self.vy)
        self.on_ground = False
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vy > 0:
                    self.rect.bottom = p.rect.top
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.rect.top = p.rect.bottom
                    self.vy = 0

    def draw(self, screen, camera_x):
        pygame.draw.rect(screen, WHITE, (self.rect.x - camera_x, self.rect.y, self.rect.w, self.rect.h), border_radius=6)
        eye_x = self.rect.x - camera_x + (24 if self.facing_right else 10)
        pygame.draw.circle(screen, BLACK, (eye_x, self.rect.y + 14), 3)


def build_level():
    platforms = [
        Platform(-200, HEIGHT - 40, 3600, 80),
        Platform(250, 430, 160, 24),
        Platform(520, 360, 180, 24),
        Platform(820, 300, 140, 24),
        Platform(1100, 390, 200, 24),
        Platform(1450, 330, 160, 24),
        Platform(1750, 270, 160, 24),
        Platform(2050, 350, 220, 24),
        Platform(2400, 300, 180, 24),
        Platform(2750, 240, 220, 24),
    ]

    coins = []
    for p in platforms[1:]:
        coins.append(Coin(p.rect.centerx - 10, p.rect.y - 28))
        if random.random() > 0.5:
            coins.append(Coin(p.rect.centerx + 30, p.rect.y - 28))

    enemies = [
        Enemy(620, HEIGHT - 72, 500, 760),
        Enemy(1180, 358, 1100, 1290),
        Enemy(2110, 318, 2050, 2260),
    ]

    goal_rect = pygame.Rect(3050, HEIGHT - 120, 30, 80)
    return platforms, coins, enemies, goal_rect


def draw_hud(screen, font, player, time_left):
    hud = f"Score: {player.score}    Lives: {player.lives}    Time: {int(time_left)}"
    txt = font.render(hud, True, BLACK)
    screen.blit(txt, (14, 12))


def draw_goal(screen, goal_rect, camera_x):
    pygame.draw.rect(screen, (240, 240, 240), (goal_rect.x - camera_x, goal_rect.y, goal_rect.w, goal_rect.h))
    pygame.draw.polygon(
        screen,
        (255, 70, 120),
        [
            (goal_rect.x - camera_x + goal_rect.w, goal_rect.y + 8),
            (goal_rect.x - camera_x + goal_rect.w + 42, goal_rect.y + 22),
            (goal_rect.x - camera_x + goal_rect.w, goal_rect.y + 36),
        ],
    )


def reset_player(player):
    player.rect.x = 50
    player.rect.y = HEIGHT - 200
    player.vx = 0
    player.vy = 0


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mario-like 2D Platformer")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 26)
    big_font = pygame.font.SysFont("consolas", 48, bold=True)

    player = Player(50, HEIGHT - 200)
    platforms, coins, enemies, goal_rect = build_level()
    level_end_x = 3200
    time_limit = 180
    start_ticks = pygame.time.get_ticks()

    state = "playing"  # playing, won, lost

    while True:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                    player.jump()
                if event.key == pygame.K_r and state in ("won", "lost"):
                    player = Player(50, HEIGHT - 200)
                    platforms, coins, enemies, goal_rect = build_level()
                    start_ticks = pygame.time.get_ticks()
                    state = "playing"

        screen.fill(SKY_BLUE)

        elapsed = (pygame.time.get_ticks() - start_ticks) / 1000.0
        time_left = max(0, time_limit - elapsed)

        if state == "playing":
            keys = pygame.key.get_pressed()
            player.handle_input(keys)
            player.apply_gravity()
            player.move_and_collide(platforms)

            for enemy in enemies:
                enemy.update()

            # Coin collection
            for coin in coins:
                if not coin.collected and player.rect.colliderect(coin.rect):
                    coin.collected = True
                    player.score += 10

            # Enemy collisions: stomp from above defeats enemy; side hit loses life
            for enemy in enemies:
                if enemy.alive and player.rect.colliderect(enemy.rect):
                    if player.vy > 0 and player.rect.bottom - enemy.rect.top < 18:
                        enemy.alive = False
                        player.vy = -10
                        player.score += 50
                    else:
                        player.lives -= 1
                        if player.lives <= 0:
                            state = "lost"
                        else:
                            reset_player(player)

            # Falling off map
            if player.rect.top > HEIGHT + 100:
                player.lives -= 1
                if player.lives <= 0:
                    state = "lost"
                else:
                    reset_player(player)

            # Time out
            if time_left <= 0:
                state = "lost"

            # Goal reached
            if player.rect.colliderect(goal_rect):
                state = "won"

        camera_x = max(0, min(player.rect.centerx - WIDTH // 2, level_end_x - WIDTH))

        for p in platforms:
            p.draw(screen, camera_x)
        for coin in coins:
            coin.draw(screen, camera_x)
        for enemy in enemies:
            enemy.draw(screen, camera_x)
        draw_goal(screen, goal_rect, camera_x)
        player.draw(screen, camera_x)
        draw_hud(screen, font, player, time_left)

        if state in ("won", "lost"):
            msg = "YOU WIN!" if state == "won" else "GAME OVER"
            sub = "Press R to restart"
            msg_surface = big_font.render(msg, True, BLACK)
            sub_surface = font.render(sub, True, BLACK)
            screen.blit(msg_surface, (WIDTH // 2 - msg_surface.get_width() // 2, HEIGHT // 2 - 60))
            screen.blit(sub_surface, (WIDTH // 2 - sub_surface.get_width() // 2, HEIGHT // 2 + 5))

        pygame.display.flip()


if __name__ == "__main__":
    main()
