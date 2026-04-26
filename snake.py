import pygame
import random

pygame.init()

# === Constants ===
CELL  = 20
COLS  = 30
ROWS  = 25
HUD_H = 40

WIN_W = COLS * CELL
WIN_H = ROWS * CELL + HUD_H

screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Snake")
clock  = pygame.time.Clock()
font   = pygame.font.SysFont("Arial", 22, bold=True)

# === Directions ===
UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)

# === Colors ===
BLACK      = (0,   0,   0)
DARK_BG    = (20,  20,  20)
WALL_COLOR = (80,  80,  80)
SNAKE_HEAD = (0,   230,  0)
SNAKE_BODY = (0,   170,  0)
FOOD_COLOR = (220,  0,   0)
WHITE      = (255, 255, 255)
BLUE_LIGHT = (100, 200, 255)
GRAY_LIGHT = (200, 200, 200)


def draw_cell(col, row, color):
    """Draw one grid cell, accounting for HUD offset at the top."""
    pygame.draw.rect(screen, color,
                     (col * CELL, row * CELL + HUD_H, CELL - 2, CELL - 2),
                     border_radius=3)


def draw_walls():
    """Draw walls around the edges of the playing field."""
    for col in range(COLS):
        draw_cell(col, 0,        WALL_COLOR)
        draw_cell(col, ROWS - 1, WALL_COLOR)
    for row in range(ROWS):
        draw_cell(0,        row, WALL_COLOR)
        draw_cell(COLS - 1, row, WALL_COLOR)


def hits_wall(col, row):
    """Return True if the cell is on the wall (edge of field)."""
    return col <= 0 or col >= COLS - 1 or row <= 0 or row >= ROWS - 1


def spawn_food(snake):
    """
    Find a random free cell for food.
    Food cannot appear on a wall or on the snake body.
    """
    while True:
        col = random.randint(1, COLS - 2)
        row = random.randint(1, ROWS - 2)
        if (col, row) not in snake:
            return (col, row)


def draw_hud(score, level, foods_eaten, foods_per_level):
    """Draw the top info panel with score and level."""
    pygame.draw.rect(screen, DARK_BG, (0, 0, WIN_W, HUD_H))
    screen.blit(font.render(f"Score: {score}",  True, WHITE),      (10, 10))
    screen.blit(font.render(f"Level: {level}",  True, BLUE_LIGHT), (WIN_W // 2 - 50, 10))
    screen.blit(
        font.render(f"Next lvl: {foods_eaten}/{foods_per_level}", True, GRAY_LIGHT),
        (WIN_W - 160, 10)
    )


# === Initial game state ===
snake     = [(10, 12), (9, 12), (8, 12)]
direction = RIGHT
food      = spawn_food(snake)

score           = 0
level           = 1
foods_eaten     = 0
FOODS_PER_LEVEL = 4
BASE_SPEED      = 6
SPEED_INCREASE  = 2
current_speed   = BASE_SPEED

running   = True
game_over = False

# === Main loop ===
while running:
    clock.tick(current_speed)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Change direction, but don't allow 180 degree turn
            if event.key == pygame.K_UP    and direction != DOWN:
                direction = UP
            if event.key == pygame.K_DOWN  and direction != UP:
                direction = DOWN
            if event.key == pygame.K_LEFT  and direction != RIGHT:
                direction = LEFT
            if event.key == pygame.K_RIGHT and direction != LEFT:
                direction = RIGHT

            # Restart on game over
            if event.key == pygame.K_r and game_over:
                snake         = [(10, 12), (9, 12), (8, 12)]
                direction     = RIGHT
                food          = spawn_food(snake)
                score         = 0
                level         = 1
                foods_eaten   = 0
                current_speed = BASE_SPEED
                game_over     = False

    if game_over:
        # Game over screen
        screen.fill(BLACK)
        big_font = pygame.font.SysFont("Arial", 48, bold=True)
        go_surf  = big_font.render("GAME OVER", True, (200, 0, 0))
        screen.blit(go_surf, (WIN_W // 2 - go_surf.get_width() // 2, 180))
        screen.blit(font.render(f"Score: {score}   Level: {level}", True, WHITE),
                    (WIN_W // 2 - 90, 260))
        screen.blit(font.render("Press R to restart", True, GRAY_LIGHT),
                    (WIN_W // 2 - 90, 300))
        pygame.display.flip()
        continue

    # Calculate new head position
    head     = snake[0]
    new_head = (head[0] + direction[0], head[1] + direction[1])

    # Check wall and self collision
    if hits_wall(new_head[0], new_head[1]) or new_head in snake:
        game_over = True
        continue

    # Eat food
    if new_head == food:
        snake.insert(0, new_head)      # head added, tail stays
        food         = spawn_food(snake)  # new food not on snake
        score       += 1
        foods_eaten += 1

        # Level up
        if foods_eaten >= FOODS_PER_LEVEL:
            level        += 1
            foods_eaten   = 0
            current_speed += SPEED_INCREASE
    else:
        # Normal move: add head, remove tail
        snake = [new_head] + snake[:-1]

    # Draw
    screen.fill(BLACK)
    draw_walls()

    # Draw snake: head brighter than body
    for i, segment in enumerate(snake):
        color = SNAKE_HEAD if i == 0 else SNAKE_BODY
        draw_cell(segment[0], segment[1], color)

    # Draw food
    draw_cell(food[0], food[1], FOOD_COLOR)

    # Draw HUD
    draw_hud(score, level, foods_eaten, FOODS_PER_LEVEL)

    pygame.display.flip()

pygame.quit()