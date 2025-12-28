import random
import pygame


class MinesweeperGame:
    """
    Core game logic for Minesweeper.
    Handles grid management, mine placement, revealing cells, and game state.
    """
    
    def __init__(self, cols, rows, mines, time_limit=240, crazy_mode=False, lock_flagged_mines=True):
        self.cols = cols
        self.rows = rows
        self.mines = mines
        self.time_limit = time_limit
        self.crazy_mode = crazy_mode
        self.lock_flagged_mines = lock_flagged_mines
        
        # Validate mine count
        max_mines = cols * rows - 1
        if self.mines > max_mines:
            print(f"Warning: Too many mines ({self.mines}). Setting to maximum ({max_mines})")
            self.mines = max_mines
        if self.mines < 1:
            print(f"Warning: Invalid mine count ({self.mines}). Setting to 1")
            self.mines = 1
        
        # Game state
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.revealed = [[False] * cols for _ in range(rows)]
        self.flagged = [[False] * cols for _ in range(rows)]
        self.first_click = True
        self.game_over = False
        self.win = False
        self.click_count = 0
        self.start_time = None
        self.final_time = 0
        self.pings_remaining = 3
        self.ping_active = False
        self.ping_start_time = 0
        
    def reset(self, crazy_mode=None, lock_flagged_mines=None):
        """Reset the game to initial state."""
        if crazy_mode is not None:
            self.crazy_mode = crazy_mode
        if lock_flagged_mines is not None:
            self.lock_flagged_mines = lock_flagged_mines
            
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.revealed = [[False] * self.cols for _ in range(self.rows)]
        self.flagged = [[False] * self.cols for _ in range(self.rows)]
        self.first_click = True
        self.game_over = False
        self.win = False
        self.click_count = 0
        self.start_time = None
        self.final_time = 0
        self.pings_remaining = 3
        self.ping_active = False
        self.ping_start_time = 0
        
    def place_mines(self, exclude_x, exclude_y):
        """Place mines on the grid, excluding the first clicked cell."""
        mines_placed = 0
        while mines_placed < self.mines:
            x = random.randint(0, self.cols - 1)
            y = random.randint(0, self.rows - 1)
            if (x, y) != (exclude_x, exclude_y) and self.grid[y][x] != -1:
                self.grid[y][x] = -1
                mines_placed += 1
                
    def count_adjacent(self, x, y):
        """Count adjacent mines for a cell."""
        if self.grid[y][x] == -1:
            return -1
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.cols and 0 <= ny < self.rows and self.grid[ny][nx] == -1:
                    count += 1
        return count
    
    def reveal(self, x, y):
        """Reveal a cell and recursively reveal adjacent empty cells."""
        if not (0 <= x < self.cols and 0 <= y < self.rows) or self.revealed[y][x]:
            return
        self.revealed[y][x] = True
        if self.grid[y][x] == 0:
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dx == dy == 0:
                        continue
                    self.reveal(x + dx, y + dy)
                    
    def reveal_all_mines(self):
        """Reveal all mines (called when game is lost)."""
        for y in range(self.rows):
            for x in range(self.cols):
                if self.grid[y][x] == -1:
                    self.revealed[y][x] = True
                    
    def check_win(self):
        """Check if all non-mine cells are revealed."""
        for y in range(self.rows):
            for x in range(self.cols):
                if self.grid[y][x] != -1 and not self.revealed[y][x]:
                    return False
        return True
    
    def get_movable_mines(self):
        """Get list of mines that can be moved (respects lock_flagged_mines setting)."""
        if self.lock_flagged_mines:
            return [(x, y) for y in range(self.rows) for x in range(self.cols) 
                    if self.grid[y][x] == -1 and not self.flagged[y][x]]
        else:
            return [(x, y) for y in range(self.rows) for x in range(self.cols) 
                    if self.grid[y][x] == -1]
    
    def get_safe_targets(self):
        """Get list of safe unrevealed cells for mine movement."""
        return [(x, y) for y in range(self.rows) for x in range(self.cols) 
                if not self.revealed[y][x] and not self.flagged[y][x] and self.grid[y][x] != -1]
    
    def move_mines(self):
        """Move mines to different locations (crazy mode feature)."""
        movable = self.get_movable_mines()
        if not movable:
            return
        targets = self.get_safe_targets()
        if len(targets) < len(movable):
            return
            
        # Remove mines from current positions
        for mx, my in movable:
            self.grid[my][mx] = 0
            
        # Place mines in new positions
        random.shuffle(targets)
        for i in range(len(movable)):
            tx, ty = targets[i]
            self.grid[ty][tx] = -1
            
        # Recalculate adjacent mine counts
        for y in range(self.rows):
            for x in range(self.cols):
                if self.grid[y][x] != -1:
                    self.grid[y][x] = self.count_adjacent(x, y)
                    
    def get_remaining_mines(self):
        """Get count of remaining unflagged mines."""
        flagged_count = sum(1 for y in range(self.rows) for x in range(self.cols) 
                          if self.flagged[y][x])
        return self.mines - flagged_count
    
    def handle_click(self, x, y, current_time):
        """
        Handle a left click on a cell.
        Returns True if the game state changed.
        """
        if self.game_over or self.flagged[y][x]:
            return False
            
        if self.first_click:
            self.place_mines(x, y)
            for yy in range(self.rows):
                for xx in range(self.cols):
                    if self.grid[yy][xx] != -1:
                        self.grid[yy][xx] = self.count_adjacent(xx, yy)
            self.first_click = False
            self.start_time = current_time
            
        self.click_count += 1
        
        if self.grid[y][x] == -1:
            # Hit a mine - game over
            self.reveal_all_mines()
            self.game_over = True
            self.final_time = (current_time - self.start_time) // 1000 if self.start_time else 0
        else:
            # Safe cell - reveal it
            self.reveal(x, y)
            if self.check_win():
                self.win = True
                self.game_over = True
                self.final_time = (current_time - self.start_time) // 1000 if self.start_time else 0
                
        # Crazy mode: move mines every 5 clicks
        if self.crazy_mode and self.click_count % 5 == 0 and not self.game_over:
            self.move_mines()
            
        return True
    
    def handle_flag(self, x, y):
        """Toggle flag on a cell (right click)."""
        if not self.revealed[y][x]:
            self.flagged[y][x] = not self.flagged[y][x]
            return True
        return False
    
    def handle_ping(self, current_time):
        """Activate sonar ping (middle mouse button)."""
        if not self.first_click and not self.game_over and self.pings_remaining > 0:
            self.pings_remaining -= 1
            self.ping_active = True
            self.ping_start_time = current_time
            return True
        return False
    
    def update(self, current_time, ping_duration=3000):
        """
        Update game state (check time limit, ping expiration).
        Returns True if game state changed.
        """
        changed = False
        
        # Check time limit
        if self.start_time is not None and not self.game_over:
            elapsed = (current_time - self.start_time) // 1000
            if elapsed >= self.time_limit:
                self.reveal_all_mines()
                self.game_over = True
                self.win = False
                self.final_time = self.time_limit
                changed = True
                
        # Check ping expiration
        if self.ping_active and (current_time - self.ping_start_time) > ping_duration:
            self.ping_active = False
            changed = True
            
        return changed
    
    def get_elapsed_time(self, current_time):
        """Get elapsed time in seconds."""
        if self.start_time is not None:
            return (current_time - self.start_time) // 1000
        return 0
    
    def get_time_left(self, current_time):
        """Get remaining time in seconds."""
        if self.start_time is not None:
            elapsed = self.get_elapsed_time(current_time)
            return max(0, self.time_limit - elapsed)
        return self.time_limit
    
    def get_clicks_until_shift(self):
        """Get number of clicks until next mine shift in crazy mode."""
        if not self.crazy_mode or self.first_click or self.game_over:
            return 0
        clicks_until = 5 - (self.click_count % 5)
        return 0 if clicks_until == 5 else clicks_until
