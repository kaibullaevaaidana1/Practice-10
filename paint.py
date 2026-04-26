import pygame
import math

pygame.init()

# === Window size ===
WIN_W   = 800
WIN_H   = 600
PANEL_H = 50

screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Paint")
clock  = pygame.time.Clock()
font   = pygame.font.SysFont("Arial", 16, bold=True)

# === Canvas (separate surface for drawing) ===
# We draw on canvas so the toolbar is never erased by the eraser
canvas = pygame.Surface((WIN_W, WIN_H - PANEL_H))
canvas.fill((255, 255, 255))

# === Color palette ===
PALETTE = [
    (0,   0,   0),
    (200, 0,   0),
    (0,   180, 0),
    (0,   0,   200),
    (255, 200, 0),
    (255, 120, 0),
    (150, 0,   150),
    (0,   180, 200),
    (150, 100, 50),
    (255, 255, 255),
]

# === Tool buttons ===
TOOLS = ["Pen", "Rect", "Circle", "Eraser"]

# === State ===
current_color = (0, 0, 0)
current_tool  = "Pen"
brush_size    = 3

drawing     = False
start_pos   = None
last_pos    = None
preview_pos = None

PANEL_Y = WIN_H - PANEL_H


def draw_panel():
    """Draw the bottom panel: tool buttons + color palette."""
    pygame.draw.rect(screen, (220, 220, 220), (0, PANEL_Y, WIN_W, PANEL_H))
    pygame.draw.line(screen, (150, 150, 150), (0, PANEL_Y), (WIN_W, PANEL_Y), 2)

    # Tool buttons
    for i, tool in enumerate(TOOLS):
        btn_x = 10 + i * 90
        btn_y = PANEL_Y + 10
        btn_w, btn_h = 80, 30

        color = (100, 160, 255) if tool == current_tool else (180, 180, 180)
        pygame.draw.rect(screen, color, (btn_x, btn_y, btn_w, btn_h), border_radius=5)
        pygame.draw.rect(screen, (80, 80, 80), (btn_x, btn_y, btn_w, btn_h), 1, border_radius=5)

        text_surf = font.render(tool, True, (0, 0, 0))
        screen.blit(text_surf, (btn_x + (btn_w - text_surf.get_width()) // 2,
                                btn_y + (btn_h - text_surf.get_height()) // 2))

    # Color swatches
    for i, color in enumerate(PALETTE):
        px = 380 + i * 38
        py = PANEL_Y + 10
        pygame.draw.rect(screen, color, (px, py, 30, 30))
        pygame.draw.rect(screen, (80, 80, 80), (px, py, 30, 30), 1)
        if color == current_color:
            pygame.draw.rect(screen, (255, 215, 0), (px - 3, py - 3, 36, 36), 3)


def get_tool_at_click(pos):
    """Return tool name if a tool button was clicked, else None."""
    if pos[1] < PANEL_Y:
        return None
    for i, tool in enumerate(TOOLS):
        btn_x = 10 + i * 90
        btn_y = PANEL_Y + 10
        if btn_x <= pos[0] <= btn_x + 80 and btn_y <= pos[1] <= btn_y + 30:
            return tool
    return None


def get_color_at_click(pos):
    """Return color if a palette swatch was clicked, else None."""
    if pos[1] < PANEL_Y:
        return None
    for i, color in enumerate(PALETTE):
        px = 380 + i * 38
        py = PANEL_Y + 10
        if px <= pos[0] <= px + 30 and py <= pos[1] <= py + 30:
            return color
    return None


# === Main loop ===
running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Mouse button down
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            # Click on tool button?
            tool = get_tool_at_click(event.pos)
            if tool:
                current_tool = tool
                continue

            # Click on color swatch?
            color = get_color_at_click(event.pos)
            if color:
                current_color = color
                continue

            # Click on canvas: start drawing
            if event.pos[1] < PANEL_Y:
                drawing     = True
                start_pos   = event.pos
                last_pos    = event.pos
                preview_pos = event.pos

        # Mouse button up: finalize shape
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if drawing and event.pos[1] < PANEL_Y:

                if current_tool == "Rect" and start_pos:
                    # Draw rectangle from start to release point
                    x = min(start_pos[0], event.pos[0])
                    y = min(start_pos[1], event.pos[1])
                    w = abs(event.pos[0] - start_pos[0])
                    h = abs(event.pos[1] - start_pos[1])
                    pygame.draw.rect(canvas, current_color, (x, y, w, h), 2)

                elif current_tool == "Circle" and start_pos:
                    # Center = midpoint, radius = half the distance
                    cx = (start_pos[0] + event.pos[0]) // 2
                    cy = (start_pos[1] + event.pos[1]) // 2
                    radius = int(math.hypot(event.pos[0] - start_pos[0],
                                           event.pos[1] - start_pos[1]) / 2)
                    if radius > 0:
                        pygame.draw.circle(canvas, current_color, (cx, cy), radius, 2)

            drawing     = False
            start_pos   = None
            preview_pos = None

        # Mouse motion: pen and eraser
        if event.type == pygame.MOUSEMOTION:
            preview_pos = event.pos

            if drawing and event.pos[1] < PANEL_Y:
                if current_tool == "Pen":
                    pygame.draw.line(canvas, current_color, last_pos, event.pos, brush_size)
                    last_pos = event.pos

                elif current_tool == "Eraser":
                    # Eraser = large white circle
                    pygame.draw.circle(canvas, (255, 255, 255), event.pos, 15)
                    last_pos = event.pos

    # Draw frame
    # 1. Canvas
    screen.blit(canvas, (0, 0))

    # 2. Preview shape while drawing rect or circle
    if drawing and preview_pos and current_tool in ("Rect", "Circle") and start_pos:
        preview_surf = canvas.copy()

        if current_tool == "Rect":
            x = min(start_pos[0], preview_pos[0])
            y = min(start_pos[1], preview_pos[1])
            w = abs(preview_pos[0] - start_pos[0])
            h = abs(preview_pos[1] - start_pos[1])
            pygame.draw.rect(preview_surf, current_color, (x, y, w, h), 2)

        elif current_tool == "Circle":
            cx = (start_pos[0] + preview_pos[0]) // 2
            cy = (start_pos[1] + preview_pos[1]) // 2
            radius = int(math.hypot(preview_pos[0] - start_pos[0],
                                    preview_pos[1] - start_pos[1]) / 2)
            if radius > 0:
                pygame.draw.circle(preview_surf, current_color, (cx, cy), radius, 2)

        screen.blit(preview_surf, (0, 0))

    # 3. Show eraser cursor
    if current_tool == "Eraser" and preview_pos and preview_pos[1] < PANEL_Y:
        pygame.draw.circle(screen, (150, 150, 150), preview_pos, 15, 2)

    # 4. Bottom panel
    draw_panel()

    pygame.display.flip()

pygame.quit()