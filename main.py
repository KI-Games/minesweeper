import pygame
import random
import sys

pygame.init()

CELL_SIZE = 30
EXTRA_HEIGHT = 100

# Default values
COLS, ROWS, MINES = 10, 10, 15
CRAZY_MODE = False

# Parse command line arguments
if len(sys.argv) >= 4:
    try:
        COLS = int(sys.argv[1])
        ROWS = int(sys.argv[2])
        MINES = int(sys.argv[3])
        if len(sys.argv) >= 5 and sys.argv[4].lower() in ['1', 'true', 'crazy']:
            CRAZY_MODE = True
    except ValueError:
        pass

WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE + EXTRA_HEIGHT

title = "Minesweeper"
if CRAZY_MODE:
    title += " - Crazy"

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(title)

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)
button_font = pygame.font.SysFont(None, 30)

click_count = 0

def reset_game():
    global grid, revealed, flagged, click_count, first_click, game_over, win
    grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    revealed = [[False] * COLS for _ in range(ROWS)]
    flagged = [[False] * COLS for _ in range(ROWS)]
    first_click = True
    game_over = False
    win = False
    click_count = 0

reset_game()

def place_mines(exclude_x, exclude_y):
    mines = 0
    while mines < MINES:
        x = random.randint(0, COLS - 1)
        y = random.randint(0, ROWS - 1)
        if (x, y) != (exclude_x, exclude_y) and grid[y][x] != -1:
            grid[y][x] = -1
            mines += 1

def count_adjacent(x, y):
    if grid[y][x] == -1:
        return -1
    count = 0
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if dx == dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS and grid[ny][nx] == -1:
                count += 1
    return count

def reveal(x, y):
    if not (0 <= x < COLS and 0 <= y < ROWS) or revealed[y][x]:
        return
    revealed[y][x] = True
    if grid[y][x] == 0:
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == dy == 0:
                    continue
                reveal(x + dx, y + dy)

def get_unrevealed_unflagged_cells():
    return [(x, y) for y in range(ROWS) for x in range(COLS) if not revealed[y][x] and not flagged[y][x]]

def move_mines():
    safe_cells = get_unrevealed_unflagged_cells()
    if len(safe_cells) < MINES:
        return
    # Clear all mines
    for y in range(ROWS):
        for x in range(COLS):
            if grid[y][x] == -1:
                grid[y][x] = 0
    # Place mines only in safe cells
    random.shuffle(safe_cells)
    for i in range(MINES):
        ux, uy = safe_cells[i]
        grid[uy][ux] = -1
    # Update all numbers
    for y in range(ROWS):
        for x in range(COLS):
            if grid[y][x] != -1:
                grid[y][x] = count_adjacent(x, y)

def reveal_all_mines():
    for y in range(ROWS):
        for x in range(COLS):
            if grid[y][x] == -1:
                revealed[y][x] = True

def check_win():
    for y in range(ROWS):
        for x in range(COLS):
            if grid[y][x] != -1 and not revealed[y][x]:
                return False
    return True

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            x, y = mx // CELL_SIZE, my // CELL_SIZE
            if y >= ROWS:
                if game_over:
                    button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 70, 200, 40)
                    if button_rect.collidepoint(mx, my):
                        reset_game()
                continue
            if not game_over:
                if event.button == 1:  # Left click
                    if flagged[y][x]:
                        continue
                    if first_click:
                        place_mines(x, y)
                        for yy in range(ROWS):
                            for xx in range(COLS):
                                if grid[yy][xx] != -1:
                                    grid[yy][xx] = count_adjacent(xx, yy)
                        first_click = False
                    click_count += 1
                    if grid[y][x] == -1:
                        reveal_all_mines()
                        game_over = True
                    else:
                        reveal(x, y)
                        if check_win():
                            win = True
                            game_over = True
                    if CRAZY_MODE and click_count % 5 == 0 and not game_over:
                        move_mines()
                elif event.button == 3:  # Right click
                    if not revealed[y][x]:
                        flagged[y][x] = not flagged[y][x]

    screen.fill((200, 200, 200))
    
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if revealed[y][x]:
                if grid[y][x] == -1:
                    pygame.draw.rect(screen, (255, 0, 0), rect)
                    pygame.draw.circle(screen, (0, 0, 0), rect.center, 10)
                    if flagged[y][x]:
                        pygame.draw.line(screen, (255, 0, 0), (x*CELL_SIZE+5, y*CELL_SIZE+5), (x*CELL_SIZE+25, y*CELL_SIZE+25), 4)
                        pygame.draw.line(screen, (255, 0, 0), (x*CELL_SIZE+5, y*CELL_SIZE+25), (x*CELL_SIZE+25, y*CELL_SIZE+5), 4)
                else:
                    pygame.draw.rect(screen, (180, 180, 180), rect)
                    if grid[y][x] > 0:
                        colors = [(0,0,0), (0,0,255), (0,128,0), (255,0,0), (128,0,128), (255,128,0), (0,255,255), (255,255,0), (128,128,128)]
                        text = font.render(str(grid[y][x]), True, colors[grid[y][x]-1])
                        screen.blit(text, (x * CELL_SIZE + 10, y * CELL_SIZE + 5))
                    if win and flagged[y][x]:
                        pygame.draw.line(screen, (0, 255, 0), (x*CELL_SIZE+5, y*CELL_SIZE+5), (x*CELL_SIZE+25, y*CELL_SIZE+25), 4)
                        pygame.draw.line(screen, (0, 255, 0), (x*CELL_SIZE+5, y*CELL_SIZE+25), (x*CELL_SIZE+25, y*CELL_SIZE+5), 4)
            else:
                pygame.draw.rect(screen, (100, 100, 255), rect)
                if flagged[y][x]:
                    pygame.draw.polygon(screen, (255, 0, 0), [(x*CELL_SIZE+5, y*CELL_SIZE+10), (x*CELL_SIZE+15, y*CELL_SIZE+25), (x*CELL_SIZE+25, y*CELL_SIZE+10)])
            pygame.draw.rect(screen, (0, 0, 0), rect, 1)

    if game_over:
        status = "WIN!" if win else "BOOM!"
        status_text = font.render(status, True, (255, 0, 0) if not win else (0, 255, 0))
        screen.blit(status_text, (WIDTH//2 - status_text.get_width()//2, HEIGHT - 100))

        button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 70, 200, 40)
        pygame.draw.rect(screen, (0, 255, 0), button_rect)
        button_text = button_font.render("Play Again", True, (0, 0, 0))
        screen.blit(button_text, (WIDTH//2 - button_text.get_width()//2, HEIGHT - 65))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()