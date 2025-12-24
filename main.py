import pygame
import random

pygame.init()

WIDTH, HEIGHT = 300, 400
CELL_SIZE = 30
COLS, ROWS = 10, 15
MINES = 15

screen = pygame.display.set_mode((WIDTH, HEIGHT + 100))
pygame.display.set_caption("Minesweeper")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
revealed = [[False] * COLS for _ in range(ROWS)]
flagged = [[False] * COLS for _ in range(ROWS)]
first_click = True
game_over = False
win = False

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
        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            mx, my = pygame.mouse.get_pos()
            x, y = mx // CELL_SIZE, my // CELL_SIZE
            if y >= ROWS:
                continue
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
                if grid[y][x] == -1:
                    game_over = True
                else:
                    reveal(x, y)
                    if check_win():
                        win = True
                        game_over = True
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
                else:
                    pygame.draw.rect(screen, (180, 180, 180), rect)
                    if grid[y][x] > 0:
                        color = [(0,0,0), (0,0,255), (0,128,0), (255,0,0), (128,0,128), (255,128,0), (0,255,255), (255,255,0), (128,128,128)][grid[y][x]-1]
                        text = font.render(str(grid[y][x]), True, color)
                        screen.blit(text, (x * CELL_SIZE + 10, y * CELL_SIZE + 5))
            else:
                pygame.draw.rect(screen, (100, 100, 255), rect)
                if flagged[y][x]:
                    pygame.draw.polygon(screen, (255, 0, 0), [(x*CELL_SIZE+5, y*CELL_SIZE+10), (x*CELL_SIZE+15, y*CELL_SIZE+25), (x*CELL_SIZE+25, y*CELL_SIZE+10)])
            pygame.draw.rect(screen, (0, 0, 0), rect, 1)

    status = "WIN!" if win else "BOOM!" if game_over and not win else ""
    status_text = font.render(status, True, (255, 0, 0) if not win else (0, 255, 0))
    screen.blit(status_text, (WIDTH//2 - status_text.get_width()//2, HEIGHT - 80))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()