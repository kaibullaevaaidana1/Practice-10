import pygame
import random

pygame.init()

# === Constants ===
SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600
FPS           = 60
ROAD_LEFT     = 60
ROAD_RIGHT    = 340

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer")
clock = pygame.time.Clock()

# Colors
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
RED    = (200, 0, 0)
GREEN  = (0, 180, 0)
GRAY   = (100, 100, 100)
GOLD   = (255, 215, 0)

font = pygame.font.SysFont("Arial", 24, bold=True)


# === Player car class ===
class PlayerCar(pygame.sprite.Sprite):
    """Player car controlled by arrow keys."""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 70))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)
        self.speed = 5

    def update(self):
        """Move left/right and stay within road boundaries."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        self.rect.left  = max(self.rect.left,  ROAD_LEFT)
        self.rect.right = min(self.rect.right, ROAD_RIGHT)


# === Enemy car class ===
class EnemyCar(pygame.sprite.Sprite):
    """Obstacle car moving from top to bottom."""
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((40, 70))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(ROAD_LEFT, ROAD_RIGHT - 40)
        self.rect.y = -80
        self.speed  = speed

    def update(self):
        """Move down. Remove sprite when off screen."""
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# === Coin class ===
class Coin(pygame.sprite.Sprite):
    """Collectible coin. Gives +1 to coin counter when picked up."""
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GOLD,           (12, 12), 12)
        pygame.draw.circle(self.image, (200, 160, 0),  (12, 12), 12, 2)
        self.rect   = self.image.get_rect()
        self.rect.x = random.randint(ROAD_LEFT, ROAD_RIGHT - 24)
        self.rect.y = -30
        self.speed  = speed

    def update(self):
        """Move down with the road. Remove when off screen."""
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# === Sprite groups ===
all_sprites   = pygame.sprite.Group()
enemy_sprites = pygame.sprite.Group()
coin_sprites  = pygame.sprite.Group()

player = PlayerCar()
all_sprites.add(player)

# === Game variables ===
score           = 0
coins_collected = 0
level           = 1
enemy_speed     = 4

enemy_timer    = 0
coin_timer     = 0
ENEMY_INTERVAL = 60
COIN_INTERVAL  = 150

running = True

# === Main game loop ===
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Spawn enemies
    enemy_timer += 1
    if enemy_timer >= ENEMY_INTERVAL:
        enemy = EnemyCar(enemy_speed)
        all_sprites.add(enemy)
        enemy_sprites.add(enemy)
        enemy_timer = 0

    # Spawn coins
    coin_timer += 1
    if coin_timer >= COIN_INTERVAL:
        coin = Coin(enemy_speed)
        all_sprites.add(coin)
        coin_sprites.add(coin)
        coin_timer = 0

    # Update all sprites
    all_sprites.update()

    # Player hits enemy = game over
    if pygame.sprite.spritecollideany(player, enemy_sprites):
        running = False

    # Player picks up coin
    collected = pygame.sprite.spritecollide(player, coin_sprites, True)
    coins_collected += len(collected)

    # Score for dodging enemies
    for enemy in list(enemy_sprites):
        if enemy.rect.top > SCREEN_HEIGHT:
            score += 1

    # Level up every 10 points
    new_level = score // 10 + 1
    if new_level > level:
        level       = new_level
        enemy_speed += 1

    # Draw
    screen.fill(GRAY)
    pygame.draw.line(screen, WHITE, (ROAD_LEFT,  0), (ROAD_LEFT,  SCREEN_HEIGHT), 3)
    pygame.draw.line(screen, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, SCREEN_HEIGHT), 3)

    all_sprites.draw(screen)

    # HUD top-left
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Level: {level}", True, WHITE), (10, 38))

    # HUD top-right: coin counter
    coin_text = f"Coins: {coins_collected}"
    coin_surf = font.render(coin_text, True, GOLD)
    screen.blit(coin_surf, (SCREEN_WIDTH - coin_surf.get_width() - 10, 10))

    pygame.display.flip()

pygame.quit()
