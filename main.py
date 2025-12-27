import pygame
import random
import sys

pygame.init()

CELL_SIZE = 30
EXTRA_HEIGHT = 100

# Default values
COLS, ROWS, MINES = 10, 10, 15
TIME_LIMIT = 240  # seconds
CRAZY_MODE = False
LOCK_FLAGGED_MINES = True  # In crazy mode, flagged mines won't move (default setting)

# Parse command line arguments
if len(sys.argv) >= 4:
    try:
        COLS = int(sys.argv[1])
        ROWS = int(sys.argv[2])
        MINES = int(sys.argv[3])
        if len(sys.argv) >= 5:
            TIME_LIMIT = int(sys.argv[4])
        if len(sys.argv) >= 6 and sys.argv[5].lower() in ['1', 'true', 'crazy']:
            CRAZY_MODE = True
    except ValueError:
        pass

# Validate mine count
max_mines = COLS * ROWS - 1  # Need at least one safe cell
if MINES > max_mines:
    print(f"Warning: Too many mines ({MINES}). Setting to maximum ({max_mines})")
    MINES = max_mines
if MINES < 1:
    print(f"Warning: Invalid mine count ({MINES}). Setting to 1")
    MINES = 1

WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE + EXTRA_HEIGHT

screen = pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)
button_font = pygame.font.SysFont(None, 30)
small_font = pygame.font.SysFont(None, 28)

click_count = 0
start_time = None
next_crazy_enabled = CRAZY_MODE
crazy_enabled = CRAZY_MODE
next_lock_flagged_mines = LOCK_FLAGGED_MINES
lock_flagged_mines = LOCK_FLAGGED_MINES

# Color array for numbers 1-8 (move outside render loop for efficiency)
NUMBER_COLORS = [(0,0,255), (0,128,0), (255,0,0), (128,0,128), (255,128,0), (0,255,255), (255,255,0), (128,128,128)]

def update_title():
    base = "Minesweeper"
    if crazy_enabled:
        base += " - Crazy"
    pygame.display.set_caption(base)

update_title()

def reset_game():
    global grid, revealed, flagged, click_count, first_click, game_over, win, start_time, crazy_enabled, lock_flagged_mines, final_time
    grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    revealed = [[False] * COLS for _ in range(ROWS)]
    flagged = [[False] * COLS for _ in range(ROWS)]
    first_click = True
    game_over = False
    win = False
    click_count = 0
    start_time = None
    final_time = 0
    crazy_enabled = next_crazy_enabled
    lock_flagged_mines = next_lock_flagged_mines
    update_title()

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

def get_movable_mines():
    if lock_flagged_mines:
        return [(x, y) for y in range(ROWS) for x in range(COLS) if grid[y][x] == -1 and not flagged[y][x]]
    else:
        return [(x, y) for y in range(ROWS) for x in range(COLS) if grid[y][x] == -1]

def get_safe_targets():
    return [(x, y) for y in range(ROWS) for x in range(COLS) if not revealed[y][x] and not flagged[y][x] and grid[y][x] != -1]

def move_mines():
    movable = get_movable_mines()
    if not movable:
        return
    targets = get_safe_targets()
    if len(targets) < len(movable):
        return
    for mx, my in movable:
        grid[my][mx] = 0
    random.shuffle(targets)
    for i in range(len(movable)):
        tx, ty = targets[i]
        grid[ty][tx] = -1
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

def get_remaining_mines():
    flagged_count = sum(1 for y in range(ROWS) for x in range(COLS) if flagged[y][x])
    return MINES - flagged_count

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
                    replay_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 70, 200, 40)
                    if replay_rect.collidepoint(mx, my):
                        reset_game()
                    crazy_rect = pygame.Rect(10, HEIGHT - 55, 200, 30)
                    if crazy_rect.collidepoint(mx, my):
                        next_crazy_enabled = not next_crazy_enabled
                    lock_rect = pygame.Rect(10, HEIGHT - 25, 280, 30)
                    if lock_rect.collidepoint(mx, my):
                        next_lock_flagged_mines = not next_lock_flagged_mines
                continue
            if not game_over:
                if event.button == 1:
                    if flagged[y][x]:
                        continue
                    if first_click:
                        place_mines(x, y)
                        for yy in range(ROWS):
                            for xx in range(COLS):
                                if grid[yy][xx] != -1:
                                    grid[yy][xx] = count_adjacent(xx, yy)
                        first_click = False
                        start_time = pygame.time.get_ticks()
                    click_count += 1
                    if grid[y][x] == -1:
                        reveal_all_mines()
                        game_over = True
                        final_time = (pygame.time.get_ticks() - start_time) // 1000 if start_time else 0
                    else:
                        reveal(x, y)
                        if check_win():
                            win = True
                            game_over = True
                            final_time = (pygame.time.get_ticks() - start_time) // 1000 if start_time else 0
                    if crazy_enabled and click_count % 5 == 0 and not game_over:
                        move_mines()
                elif event.button == 3:
                    if not revealed[y][x]:
                        flagged[y][x] = not flagged[y][x]

    if start_time is not None and not game_over:
        elapsed = (pygame.time.get_ticks() - start_time) // 1000
        if elapsed >= TIME_LIMIT:
            reveal_all_mines()
            game_over = True
            win = False
            final_time = TIME_LIMIT

    screen.fill((200, 200, 200))
    
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if revealed[y][x]:
                if grid[y][x] == -1:
                    if flagged[y][x] and game_over:
                        pygame.draw.rect(screen, (0, 200, 0), rect)
                    else:
                        pygame.draw.rect(screen, (255, 0, 0), rect)
                    pygame.draw.circle(screen, (0, 0, 0), rect.center, 10)
                    if flagged[y][x]:
                        pygame.draw.line(screen, (255, 255, 255), (x*CELL_SIZE+5, y*CELL_SIZE+5), (x*CELL_SIZE+25, y*CELL_SIZE+25), 4)
                        pygame.draw.line(screen, (255, 255, 255), (x*CELL_SIZE+5, y*CELL_SIZE+25), (x*CELL_SIZE+25, y*CELL_SIZE+5), 4)
                else:
                    pygame.draw.rect(screen, (180, 180, 180), rect)
                    if grid[y][x] > 0:
                        color_index = min(grid[y][x] - 1, len(NUMBER_COLORS) - 1)
                        text = font.render(str(grid[y][x]), True, NUMBER_COLORS[color_index])
                        screen.blit(text, (x * CELL_SIZE + 10, y * CELL_SIZE + 5))
            else:
                pygame.draw.rect(screen, (100, 100, 255), rect)
                if flagged[y][x]:
                    pygame.draw.polygon(screen, (255, 0, 0), [(x*CELL_SIZE+5, y*CELL_SIZE+10), (x*CELL_SIZE+15, y*CELL_SIZE+25), (x*CELL_SIZE+25, y*CELL_SIZE+10)])
            pygame.draw.rect(screen, (0, 0, 0), rect, 1)

    remaining = get_remaining_mines() if not first_click else MINES
    mines_text = small_font.render(f"Mines: {remaining}", True, (0, 0, 0))
    screen.blit(mines_text, (10, ROWS * CELL_SIZE + 10))

    if start_time is not None:
        elapsed = (pygame.time.get_ticks() - start_time) // 1000
        time_left = max(0, TIME_LIMIT - elapsed)
        timer_text = small_font.render(f"Time: {time_left}", True, (255,0,0) if time_left < 30 else (0,0,0))
        screen.blit(timer_text, (WIDTH - timer_text.get_width() - 10, ROWS * CELL_SIZE + 10))

    if crazy_enabled and not first_click and not game_over:
        clicks_until = 5 - (click_count % 5)
        if clicks_until == 5:
            clicks_until = 0
        shift_text = small_font.render(f"Shift in: {clicks_until}", True, (0, 0, 0))
        screen.blit(shift_text, (10, ROWS * CELL_SIZE + 40))

    if game_over:
        status = "WIN!" if win else ("TIME UP!" if final_time >= TIME_LIMIT else "BOOM!")
        status_text = font.render(status, True, (0, 255, 0) if win else (255, 0, 0))
        screen.blit(status_text, (WIDTH//2 - status_text.get_width()//2, HEIGHT - 110))

        button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 70, 200, 40)
        pygame.draw.rect(screen, (0, 255, 0), button_rect)
        button_text = button_font.render("Play Again", True, (0, 0, 0))
        screen.blit(button_text, (WIDTH//2 - button_text.get_width()//2, HEIGHT - 65))

        # Crazy Mode checkbox
        crazy_rect = pygame.Rect(10, HEIGHT - 55, 200, 30)
        pygame.draw.rect(screen, (255, 255, 255), crazy_rect)
        pygame.draw.rect(screen, (0, 0, 0), crazy_rect, 2)
        crazy_check = pygame.Rect(15, HEIGHT - 50, 20, 20)
        pygame.draw.rect(screen, (0, 0, 0), crazy_check, 2)
        if next_crazy_enabled:
            pygame.draw.line(screen, (0, 0, 0), (crazy_check.left + 2, crazy_check.top + 2), (crazy_check.right - 2, crazy_check.bottom - 2), 3)
            pygame.draw.line(screen, (0, 0, 0), (crazy_check.left + 2, crazy_check.bottom - 2), (crazy_check.right - 2, crazy_check.top + 2), 3)
        crazy_text = small_font.render("Crazy Mode", True, (0, 0, 0))
        screen.blit(crazy_text, (40, HEIGHT - 52))

        # Lock Flagged Mines checkbox
        lock_rect = pygame.Rect(10, HEIGHT - 25, 280, 30)
        pygame.draw.rect(screen, (255, 255, 255), lock_rect)
        pygame.draw.rect(screen, (0, 0, 0), lock_rect, 2)
        lock_check = pygame.Rect(15, HEIGHT - 20, 20, 20)
        pygame.draw.rect(screen, (0, 0, 0), lock_check, 2)
        if next_lock_flagged_mines:
            pygame.draw.line(screen, (0, 0, 0), (lock_check.left + 2, lock_check.top + 2), (lock_check.right - 2, lock_check.bottom - 2), 3)
            pygame.draw.line(screen, (0, 0, 0), (lock_check.left + 2, lock_check.bottom - 2), (lock_check.right - 2, lock_check.top + 2), 3)
        lock_text = small_font.render("Lock Flagged Mines", True, (0, 0, 0))
        screen.blit(lock_text, (40, HEIGHT - 22))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()