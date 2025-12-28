import pygame
import sys
from game import MinesweeperGame

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

WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE + EXTRA_HEIGHT

screen = pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)
button_font = pygame.font.SysFont(None, 30)
small_font = pygame.font.SysFont(None, 28)

next_crazy_enabled = CRAZY_MODE
next_lock_flagged_mines = LOCK_FLAGGED_MINES
PING_DURATION = 3000  # milliseconds

# Color array for numbers 1-8 
NUMBER_COLORS = [(0,0,255), (0,128,0), (255,0,0), (128,0,128), (255,128,0), (0,255,255), (255,255,0), (128,128,128)]

def update_title():
    base = "Minesweeper"
    if game.crazy_mode:
        base += " - Crazy"
    pygame.display.set_caption(base)

# Create game instance
game = MinesweeperGame(COLS, ROWS, MINES, TIME_LIMIT, CRAZY_MODE, LOCK_FLAGGED_MINES)
update_title()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            x, y = mx // CELL_SIZE, my // CELL_SIZE
            if y >= ROWS:
                if game.game_over:
                    replay_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 70, 200, 40)
                    if replay_rect.collidepoint(mx, my):
                        game.reset(next_crazy_enabled, next_lock_flagged_mines)
                        update_title()
                    crazy_rect = pygame.Rect(10, HEIGHT - 55, 200, 30)
                    if crazy_rect.collidepoint(mx, my):
                        next_crazy_enabled = not next_crazy_enabled
                    lock_rect = pygame.Rect(10, HEIGHT - 25, 280, 30)
                    if lock_rect.collidepoint(mx, my):
                        next_lock_flagged_mines = not next_lock_flagged_mines
                continue
            if not game.game_over:
                if event.button == 1:
                    game.handle_click(x, y, pygame.time.get_ticks())
                elif event.button == 2:  # Middle mouse button - sonar ping
                    game.handle_ping(pygame.time.get_ticks())
                elif event.button == 3:
                    game.handle_flag(x, y)

    # Update game state
    game.update(pygame.time.get_ticks(), PING_DURATION)

    screen.fill((200, 200, 200))
    
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if game.revealed[y][x]:
                if game.grid[y][x] == -1:
                    if game.flagged[y][x] and game.game_over:
                        pygame.draw.rect(screen, (0, 200, 0), rect)
                    else:
                        pygame.draw.rect(screen, (255, 0, 0), rect)
                    pygame.draw.circle(screen, (0, 0, 0), rect.center, 10)
                    if game.flagged[y][x]:
                        pygame.draw.line(screen, (255, 255, 255), (x*CELL_SIZE+5, y*CELL_SIZE+5), (x*CELL_SIZE+25, y*CELL_SIZE+25), 4)
                        pygame.draw.line(screen, (255, 255, 255), (x*CELL_SIZE+5, y*CELL_SIZE+25), (x*CELL_SIZE+25, y*CELL_SIZE+5), 4)
                else:
                    pygame.draw.rect(screen, (180, 180, 180), rect)
                    if game.grid[y][x] > 0:
                        color_index = min(game.grid[y][x] - 1, len(NUMBER_COLORS) - 1)
                        text = font.render(str(game.grid[y][x]), True, NUMBER_COLORS[color_index])
                        screen.blit(text, (x * CELL_SIZE + 10, y * CELL_SIZE + 5))
            else:
                pygame.draw.rect(screen, (100, 100, 255), rect)
                if game.flagged[y][x]:
                    pygame.draw.polygon(screen, (255, 0, 0), [(x*CELL_SIZE+5, y*CELL_SIZE+10), (x*CELL_SIZE+15, y*CELL_SIZE+25), (x*CELL_SIZE+25, y*CELL_SIZE+10)])
                # Show ghosted information during ping
                if game.ping_active and not game.first_click:
                    if game.grid[y][x] == -1:
                        # Ghost mine indicator
                        pygame.draw.circle(screen, (255, 255, 255, 128), rect.center, 8, 2)
                    elif game.grid[y][x] > 0:
                        # Ghost number
                        color_index = min(game.grid[y][x] - 1, len(NUMBER_COLORS) - 1)
                        ghost_color = tuple(list(NUMBER_COLORS[color_index]) + [128])  # Add alpha
                        ghost_text = font.render(str(game.grid[y][x]), True, (200, 200, 200))
                        screen.blit(ghost_text, (x * CELL_SIZE + 10, y * CELL_SIZE + 5))
            pygame.draw.rect(screen, (0, 0, 0), rect, 1)

    remaining = game.get_remaining_mines() if not game.first_click else game.mines
    mines_text = small_font.render(f"Mines: {remaining}", True, (0, 0, 0))
    screen.blit(mines_text, (10, ROWS * CELL_SIZE + 10))

    if game.start_time is not None:
        time_left = game.get_time_left(pygame.time.get_ticks())
        timer_text = small_font.render(f"Time: {time_left}", True, (255,0,0) if time_left < 30 else (0,0,0))
        screen.blit(timer_text, (WIDTH - timer_text.get_width() - 10, ROWS * CELL_SIZE + 10))
        
        # Display pings remaining
        pings_text = small_font.render(f"Pings: {game.pings_remaining}", True, (0, 0, 0))
        screen.blit(pings_text, (WIDTH - pings_text.get_width() - 10, ROWS * CELL_SIZE + 35))

    clicks_until_shift = game.get_clicks_until_shift()
    if clicks_until_shift > 0:
        shift_text = small_font.render(f"Shift in: {clicks_until_shift}", True, (0, 0, 0))
        screen.blit(shift_text, (10, ROWS * CELL_SIZE + 40))

    if game.game_over:
        status = "WIN!" if game.win else ("TIME UP!" if game.final_time >= TIME_LIMIT else "BOOM!")
        status_text = font.render(status, True, (0, 255, 0) if game.win else (255, 0, 0))
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