import pygame
import random

pygame.init()
clock = pygame.time.Clock()

WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

CELL_SIZE = 30
GRID_OFFSET_X, GRID_OFFSET_Y = 50, 50
ROWS, COLS = 10, 10

ship_sizes = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]

player_grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
computer_grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
player_shots = [[0 for _ in range(COLS)] for _ in range(ROWS)]
computer_shots = [[0 for _ in range(COLS)] for _ in range(ROWS)]

player_turn = True
smart_mode = False
last_hit = None
game_over = False
winner_text = ""


def can_place_ship(grid, row, col, size, orientation):
    for i in range(size):
        r, c = row + (i if orientation == 'V' else 0), col + (i if orientation == 'H' else 0)
        if r >= ROWS or c >= COLS or grid[r][c] == 1:
            return False
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                nr, nc = r + dr, c + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr][nc] == 1:
                    return False
    return True


def place_ships(grid):
    for size in ship_sizes:
        placed = False
        while not placed:
            row, col = random.randint(0, ROWS - 1), random.randint(0, COLS - 1)
            orientation = random.choice(['H', 'V'])
            if can_place_ship(grid, row, col, size, orientation):
                for i in range(size):
                    r, c = row + (i if orientation == 'V' else 0), col + (i if orientation == 'H' else 0)
                    grid[r][c] = 1
                placed = True


def check_hit(grid, row, col):
    return grid[row][col] == 1


def get_ship_cells(grid, row, col):
    ship_cells = [(row, col)]
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        r, c = row, col
        while 0 <= r < ROWS and 0 <= c < COLS and grid[r][c] == 1:
            if (r, c) not in ship_cells:
                ship_cells.append((r, c))
            r, c = r + dr, c + dc
    return ship_cells


def is_ship_sunk(grid, shots, row, col):
    ship_cells = get_ship_cells(grid, row, col)
    return all(shots[r][c] == 1 for r, c in ship_cells)


def all_ships_sunk(grid, shots):
    for row in range(ROWS):
        for col in range(COLS):
            if grid[row][col] == 1 and shots[row][col] == 0:
                return False
    return True


def mark_surrounding_cells(shots, ship_cells):
    for row, col in ship_cells:
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                r, c = row + dr, col + dc
                if 0 <= r < ROWS and 0 <= c < COLS and shots[r][c] == 0:
                    shots[r][c] = 2


def draw_grid(grid, shots, offset_x, offset_y, highlight=False, show_ships=False):
    if highlight:
        pygame.draw.rect(screen, RED, (offset_x - 2, offset_y - 2, COLS * CELL_SIZE + 4, ROWS * CELL_SIZE + 4), 3)

    all_sunk = all_ships_sunk(grid, shots)
    for row in range(ROWS):
        for col in range(COLS):
            pygame.draw.rect(screen, WHITE,
                             (offset_x + col * CELL_SIZE, offset_y + row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, BLACK,
                             (offset_x + col * CELL_SIZE, offset_y + row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
            if show_ships and grid[row][col] == 1 and shots[row][col] == 0:
                pygame.draw.circle(screen, RED,
                                   (offset_x + col * CELL_SIZE + CELL_SIZE // 2,
                                    offset_y + row * CELL_SIZE + CELL_SIZE // 2), 3)
            if shots[row][col] == 1:
                if grid[row][col] == 1:
                    pygame.draw.line(screen, RED,
                                     (offset_x + col * CELL_SIZE, offset_y + row * CELL_SIZE),
                                     (offset_x + (col + 1) * CELL_SIZE, offset_y + (row + 1) * CELL_SIZE), 2)
                    pygame.draw.line(screen, RED,
                                     (offset_x + (col + 1) * CELL_SIZE, offset_y + row * CELL_SIZE),
                                     (offset_x + col * CELL_SIZE, offset_y + (row + 1) * CELL_SIZE), 2)
                else:
                    pygame.draw.circle(screen, BLUE,
                                       (offset_x + col * CELL_SIZE + CELL_SIZE // 2,
                                        offset_y + row * CELL_SIZE + CELL_SIZE // 2), 5)
            elif shots[row][col] == 2 or all_sunk:
                pygame.draw.circle(screen, BLUE,
                                   (offset_x + col * CELL_SIZE + CELL_SIZE // 2,
                                    offset_y + row * CELL_SIZE + CELL_SIZE // 2), 3)


def computer_move():
    global player_turn, last_hit, game_over, winner_text

    if game_over:
        return

    pygame.time.delay(500)
    if smart_mode and last_hit:
        row, col = last_hit
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            r, c = row + dr, col + dc
            if 0 <= r < ROWS and 0 <= c < COLS and computer_shots[r][c] == 0:
                computer_shots[r][c] = 1
                if check_hit(player_grid, r, c):
                    last_hit = (r, c)
                    if is_ship_sunk(player_grid, computer_shots, r, c):
                        ship_cells = get_ship_cells(player_grid, r, c)
                        mark_surrounding_cells(computer_shots, ship_cells)
                        last_hit = None
                    if all_ships_sunk(player_grid, computer_shots):
                        game_over = True
                        winner_text = "Ты проиграл"
                    return
                else:
                    player_turn = True
                    return

    while True:
        row, col = random.randint(0, ROWS - 1), random.randint(0, COLS - 1)
        if computer_shots[row][col] == 0:
            computer_shots[row][col] = 1
            if check_hit(player_grid, row, col):
                last_hit = (row, col)
                if is_ship_sunk(player_grid, computer_shots, row, col):
                    ship_cells = get_ship_cells(player_grid, row, col)
                    mark_surrounding_cells(computer_shots, ship_cells)
                    last_hit = None
                if all_ships_sunk(player_grid, computer_shots):
                    game_over = True
                    winner_text = "Ты проиграл"
            else:
                player_turn = True
            return


def start_screen():
    global smart_mode
    font = pygame.font.Font(None, 36)
    text_random = font.render('1: Режим "Рандомный"', True, BLACK)
    text_smart = font.render('2: Режим "Умный"', True, BLACK)
    running = True

    while running:
        screen.fill(WHITE)
        screen.blit(text_random, (WIDTH // 2 - text_random.get_width() // 2, HEIGHT // 3))
        screen.blit(text_smart, (WIDTH // 2 - text_smart.get_width() // 2, HEIGHT // 3 + 50))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    smart_mode = False
                    running = False
                if event.key == pygame.K_2:
                    smart_mode = True
                    running = False


def check_game_over():
    global game_over, winner_text
    if all_ships_sunk(computer_grid, player_shots):
        game_over = True
        winner_text = "Ты победил"
    elif all_ships_sunk(player_grid, computer_shots):
        game_over = True
        winner_text = "Ты проиграл"


place_ships(player_grid)
place_ships(computer_grid)

start_screen()
running = True

while running:
    screen.fill(WHITE)
    draw_grid(player_grid, computer_shots, GRID_OFFSET_X, GRID_OFFSET_Y, highlight=not player_turn, show_ships=True)
    draw_grid(computer_grid, player_shots, GRID_OFFSET_X + WIDTH // 2, GRID_OFFSET_Y, highlight=player_turn)

    if game_over:
        font = pygame.font.Font(None, 72)
        text = font.render(winner_text, True, RED)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
        pygame.display.flip()


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_over:
            continue

        if not player_turn:
            computer_move()

        elif event.type == pygame.MOUSEBUTTONDOWN and player_turn:
            x, y = pygame.mouse.get_pos()
            if GRID_OFFSET_X + WIDTH // 2 <= x < GRID_OFFSET_X + WIDTH // 2 + COLS * CELL_SIZE and GRID_OFFSET_Y <= y < GRID_OFFSET_Y + ROWS * CELL_SIZE:
                col = (x - GRID_OFFSET_X - WIDTH // 2) // CELL_SIZE
                row = (y - GRID_OFFSET_Y) // CELL_SIZE
                if player_shots[row][col] == 0:
                    player_shots[row][col] = 1
                    if check_hit(computer_grid, row, col):
                        if is_ship_sunk(computer_grid, player_shots, row, col):
                            ship_cells = get_ship_cells(computer_grid, row, col)
                            mark_surrounding_cells(player_shots, ship_cells)
                        print("Попадание")
                    else:
                        print("Промах")
                        player_turn = False
                    check_game_over()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
