import pygame
import random


pygame.init()
clock = pygame.time.Clock()

# Настройки экрана и цвета
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Морской бой")
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Настройки сетки
CELL_SIZE = 30
GRID_OFFSET_X, GRID_OFFSET_Y = 50, 50
ROWS, COLS = 10, 10

# Определение кораблей
ship_sizes = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]

# Инициализация сеток игрока и компьютера
player_grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
computer_grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
player_shots = [[0 for _ in range(COLS)] for _ in range(ROWS)]
computer_shots = [[0 for _ in range(COLS)] for _ in range(ROWS)]

player_turn = True

# Проверка на возможность размещения корабля
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


# Расстановка кораблей без соседних клеток
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


# Проверка попадания
def check_hit(grid, row, col):
    return grid[row][col] == 1


# Поиск всех клеток корабля
def get_ship_cells(grid, row, col):
    ship_cells = [(row, col)]
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        r, c = row, col
        while 0 <= r < ROWS and 0 <= c < COLS and grid[r][c] == 1:
            if (r, c) not in ship_cells:
                ship_cells.append((r, c))
            r, c = r + dr, c + dc
    return ship_cells


# Проверка, уничтожен ли корабль
def is_ship_sunk(grid, shots, row, col):
    ship_cells = get_ship_cells(grid, row, col)
    return all(shots[r][c] == 1 for r, c in ship_cells)


# Проверка, уничтожены ли все корабли
def all_ships_sunk(grid, shots):
    for row in range(ROWS):
        for col in range(COLS):
            if grid[row][col] == 1 and shots[row][col] == 0:
                return False
    return True


# Отметка клеток вокруг уничтоженного корабля
def mark_surrounding_cells(shots, ship_cells):
    for row, col in ship_cells:
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                r, c = row + dr, col + dc
                if 0 <= r < ROWS and 0 <= c < COLS and shots[r][c] == 0:
                    shots[r][c] = 2  # Отмечаем как промах вокруг корабля


# Функция для отрисовки сетки с отметками
def draw_grid(grid, shots, offset_x, offset_y, highlight=False, show_ships=False):
    # Выделение рамкой активного поля
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


# Ход компьютера с задержкой
def computer_move():
    global player_turn
    row, col = random.randint(0, ROWS - 1), random.randint(0, COLS - 1)
    if computer_shots[row][col] == 0:
        computer_shots[row][col] = 1
        if check_hit(player_grid, row, col):
            print("Компьютер попал!")
            if is_ship_sunk(player_grid, computer_shots, row, col):
                ship_cells = get_ship_cells(player_grid, row, col)
                mark_surrounding_cells(computer_shots, ship_cells)
                pygame.time.delay(100)
        else:
            print("Компьютер промахнулся!")
            player_turn = True
            pygame.time.delay(500)  # Задержка после каждого хода компьютера


# Начальная расстановка кораблей
place_ships(player_grid)
place_ships(computer_grid)

# Основной игровой цикл
running = True


while running:
    screen.fill(WHITE)
    # Отрисовка сетки с рамкой для текущего хода
    draw_grid(player_grid, computer_shots, GRID_OFFSET_X, GRID_OFFSET_Y, highlight=not player_turn, show_ships=True)
    draw_grid(computer_grid, player_shots, GRID_OFFSET_X + WIDTH // 2, GRID_OFFSET_Y, highlight=player_turn)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

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
                        print("Попадание!")
                    else:
                        print("Промах!")
                        player_turn = False  # Передача хода компьютеру после промаха


    pygame.display.flip()
    clock.tick(30)

pygame.quit()
