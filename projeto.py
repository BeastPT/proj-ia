#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor, UltrasonicSensor)
from pybricks.parameters import Port, Stop, Color
from pybricks.tools import wait
from pybricks.robotics import DriveBase
from sys import exit
import time

from collections import deque

# Inicialização
ev3 = EV3Brick()
color_sensor = ColorSensor(Port.S2)
touch_sensorLeft = TouchSensor(Port.S3)
touch_sensorRight = TouchSensor(Port.S4)
left_motor = Motor(Port.D)
right_motor = Motor(Port.A)

# Definição da base de condução do robô
robot = DriveBase(left_motor, right_motor, wheel_diameter=50, axle_track=150)

# Variáveis para coordenadas
robot_col = 0
robot_row = 0

# Variáveis de tempo
TEMPO_ENTRE_JOGADA = 10000 # 10 segundos

# Variáveis para direção
change_col = 1 # -1 0 1
change_row = 0 # -1 0 1

ambient = {
    "barreira": Color.RED,
    "casa": Color.BLACK,
}


color_weights = {
    Color.YELLOW: 8, #Castanho
    Color.BROWN: 4, #Amarelo
    Color.GREEN: 2, 
    Color.BLUE: 1,
    Color.BLACK: 0
}

is_first_move = True

distancia_manteiga = [[None] * 6 for _ in range(6)]
possible_zeros_manteiga = 36

calor_torradeira = [[None] * 6 for _ in range(6)]
possible_zeros_torradeira = 36

position_bolor = {'row': 5, 'col': 5}


# Funções Auxiliares

def print_table(table, table_name):
    """
    Imprime uma tabela 6x6 com formatação adequada
    """
    # Imprime o nome da tabela
    print("\n" + "=" * 50)
    print(table_name)
    print("=" * 50)
    
    # Imprime os números das colunas
    print("     ", end="")
    for col in range(6):
        print(" {:^5} ".format(col), end="")
    print("\n")
    
    # Imprime cada linha com seus valores
    for row in range(6):
        print(" {} |".format(row), end="")
        for col in range(6):
            value = table[row][col]
            if value is None:
                print("  -   ", end="")
            else:
                print(" {:.2f} ".format(value), end="")
        print()  # Nova linha no final de cada row
    print()  # Linha extra no final da tabela

def print_all_tables(dist_manteiga, calor_torrad):
    """
    Imprime todas as tabelas em sequência
    """
    print_table(dist_manteiga, "Tabela de Distância da Manteiga")
    print_table(calor_torrad, "Tabela de Calor da Torradeira")

def disperse_table(table, value, row, col, radius=6):
    for r in range(row - radius, row + radius + 1):
        for c in range(col - radius, col + radius + 1):
            # Verificar limites da tabela
            if 0 <= r < len(table) and 0 <= c < len(table[0]):
                # Calcular a distância de Manhattan
                distance = abs(r - row) + abs(c - col)
                # Valor decrementado com base na distância
                decremented_value = abs(value - distance)

                table[r][c] = decremented_value

def filter_table(table1, table2):
    """
    Guarda os valores iguais nas duas tabelas e None nos outros      
    """
    for row in range(len(table1)):
        for col in range(len(table1[0])):
            if table1[row][col] != table2[row][col]:
                table1[row][col] = None

def filter_table_min(table1, table2):
    """
    Mantém os menores valores entre duas tabelas  
    """
    for row in range(len(table1)):
        for col in range(len(table1[0])):
            if table1[row][col] > table2[row][col]:
                table1[row][col] = table2[row][col]     


def populate_tabela(table):
    aux_tables = []
    zeros = 0
    for row in range(len(table)):
        for col in range(len(table[0])):
            if table[row][col] == 0:
                zeros += 1
                temp_table = [[None] * len(table[0]) for _ in range(len(table))]
                disperse_table(temp_table, 0, row, col)
                aux_tables.append(temp_table)

    if aux_tables:
        result_table = aux_tables[0]
        for i in range(1, len(aux_tables)):
            filter_table_min(result_table, aux_tables[i])
        return result_table, zeros
    return table, None

def has_numbers(table):
    return any(cell is not None for row in table for cell in row)


# Inicialização
aux = [[None] * 6 for _ in range(6)]


def get_all_objects():
    global distancia_manteiga, calor_torradeira, is_first_move, possible_zeros_manteiga, possible_zeros_torradeira

    if possible_zeros_manteiga != 1:
        distance_manteiga = get_distance("Distância Manteiga")
        if distance_manteiga is not None:
            if has_numbers(distancia_manteiga):
                disperse_table(aux, distance_manteiga, robot_row, robot_col)
                filter_table(distancia_manteiga, aux)
                distancia_manteiga, possible_zeros_manteiga = populate_tabela(distancia_manteiga)
                #print_table(distancia_manteiga, "Tabela de Distância da Manteiga")
            else:
                disperse_table(distancia_manteiga, distance_manteiga, robot_row, robot_col)
    wait(1000)

    if possible_zeros_torradeira != 1:
        distance_torradeira = get_distance("Calor Torradeira")
        if distance_torradeira is not None:
            if has_numbers(calor_torradeira):
                disperse_table(aux, distance_torradeira, robot_row, robot_col)
                filter_table(calor_torradeira, aux)
                calor_torradeira, possible_zeros_torradeira = populate_tabela(calor_torradeira)
                #print_table(calor_torradeira, "Tabela de Distância da Torradeira")
            else:
                disperse_table(calor_torradeira, distance_torradeira, robot_row, robot_col)
    wait(1000)

    print_all_tables(distancia_manteiga, calor_torradeira)
    

def find_nearest_zero(table, start_row, start_col):
    """
    Finds the nearest zero in a 6x6 table from the given row and column.
    Uses Breadth-First Search (BFS) to determine the shortest distance.
    """
    rows, cols = len(table), len(table[0])
    visited = [[False] * cols for _ in range(rows)]
    queue = deque([(start_row, start_col, 0)])  # (row, col, distance)

    while queue:
        row, col, distance = queue.popleft()

        # Check boundaries and if already visited
        if row < 0 or col < 0 or row >= rows or col >= cols or visited[row][col]:
            continue

        # Mark as visited
        visited[row][col] = True

        # Check if the current cell is a 0
        if table[row][col] == 0:
            return (row, col, distance)

        # Add neighbors to the queue
        queue.extend([
            (row - 1, col, distance + 1),  # Up
            (row + 1, col, distance + 1),  # Down
            (row, col - 1, distance + 1),  # Left
            (row, col + 1, distance + 1)   # Right
        ])

    # If no zero is found
    return None

def find_nearest_zero_oriented(table, start_row, start_col):
    """
    Encontra o zero mais próximo, priorizando a direção para onde o robô está virado.
    Usa BFS para determinar a menor distância.
    """
    rows, cols = len(table), len(table[0])
    visited = [[False] * cols for _ in range(rows)]
    queue = deque([(start_row, start_col, 0)])  # (row, col, distance)
    prioritized_queue = []

    while queue:
        row, col, distance = queue.popleft()

        # Verificar limites e se já foi visitado
        if row < 0 or col < 0 or row >= rows or col >= cols or visited[row][col]:
            continue

        # Marcar como visitado
        visited[row][col] = True

        # Verificar se a célula atual é um zero
        if table[row][col] == 0:
            if (row - start_row == change_row) and (col - start_col == change_col):
                # Priorizar se estiver na direção do robô
                return (row, col, distance)
            else:
                # Adicionar para consideração posterior
                prioritized_queue.append((row, col, distance))
            continue

        # Adicionar vizinhos à fila
        queue.extend([
            (row - 1, col, distance + 1),  # Para cima
            (row + 1, col, distance + 1),  # Para baixo
            (row, col - 1, distance + 1),  # Para a esquerda
            (row, col + 1, distance + 1)   # Para a direita
        ])

    # Retornar o primeiro zero encontrado se nenhum estiver na direção do robô
    return prioritized_queue[0] if prioritized_queue else None


def find_nearest_zeros(table, start_row, start_col):
    """
    Finds all zeros at the nearest distance from the given position in a 6x6 table.
    Uses Breadth-First Search (BFS) to determine the shortest distance and returns all zeros at that distance.
    """
    rows, cols = len(table), len(table[0])
    visited = [[False] * cols for _ in range(rows)]
    queue = deque([(start_row, start_col, 0)])  # (row, col, distance)
    nearest_zeros = []
    min_distance = float('inf')

    while queue:
        row, col, distance = queue.popleft()

        # Check boundaries and if already visited
        if row < 0 or col < 0 or row >= rows or col >= cols or visited[row][col]:
            continue

        # Mark as visited
        visited[row][col] = True

        # If a zero is found
        if table[row][col] == 0:
            if distance < min_distance:
                # Found a closer zero, reset results
                nearest_zeros = [(row, col)]
                min_distance = distance
            elif distance == min_distance:
                # Add to results if it's the same shortest distance
                nearest_zeros.append((row, col))
            continue  # Do not explore further from this cell

        # Add neighbors to the queue
        queue.extend([
            (row - 1, col, distance + 1),  # Up
            (row + 1, col, distance + 1),  # Down
            (row, col - 1, distance + 1),  # Left
            (row, col + 1, distance + 1)   # Right
        ])

    return nearest_zeros, min_distance if nearest_zeros else None

# Funções de movimento
def forward(distance):
    robot.straight(distance)

def backward(distance):
    robot.straight(-distance)

def turn_left():
    global change_col, change_row
    robot.turn(-78)
    #print("Inicial: dir=(" + str(change_col) + " ," + str(change_row) +")")
    change_col, change_row = change_row, -change_col
    #print("Após virar à esquerda: dir=(" + str(change_col) + " ," + str(change_row) +")")

def turn_right():
    global change_col, change_row
    robot.turn(78)
    #print("Inicial: dir=(" + str(change_col) + " ," + str(change_row) +")")
    change_col, change_row = -change_row, change_col
    #print("Após virar à direita: dir=(" + str(change_col) + " ," + str(change_row) +")")

def change_position():
    global robot_col, robot_row
    robot_col += change_col
    robot_row += change_row



# Funções da Posição
def get_distance(text):
    has_found = False
    distance = 0
    colors_shown = set()

    ev3.speaker.beep()
    ev3.screen.print(text)

    wait(1000)
    ev3.speaker.beep()

    for i in range(5):
        current_color = color_sensor.color()

        if current_color not in colors_shown and current_color in color_weights:
            colors_shown.add(current_color)
            weight = color_weights[current_color]
            has_found = True

            if weight == 0:
                distance = 0
                ev3.screen.print(str(current_color) + "\n Current Distance: \n" + str(distance))
                wait(2500)
                break

            distance += weight
            ev3.screen.print(str(current_color) + "\n Current Distance:  \n" + str(distance))

        wait(1000)

    ev3.screen.clear()
    return distance if has_found else None

def verify_manteiga():
    return distancia_manteiga[robot_row][robot_col] == 0

def verify_torradeira():
    return calor_torradeira[robot_row][robot_col] == 0

def verify_bolor():
    return robot_row == position_bolor["row"] and robot_col == position_bolor["col"]

def verify_objects():
    if verify_manteiga():
        ev3.screen.clear()
        ev3.screen.draw_text(10, 10, "VITÓRIA")
        wait(10000)
        exit()
    
    if verify_torradeira():
        ev3.screen.clear()
        ev3.screen.draw_text(10, 10, "CAISTE NA TORRADEIRA")
        wait(10000) 
        
    if verify_bolor():
        ev3.screen.clear()
        ev3.screen.draw_text(10, 10, "GAME OVER")  
        exit()  



def wait_to_drive(distance, speed=40):
    wait(distance/speed*1000)
    robot.stop()

def andar_casa():
    robot.drive(40, 0)
    while True:
        currentColor = color_sensor.color()
        if currentColor == ambient["barreira"]: # Encontrou barreira - voltar para tras
            robot.stop()
            backward(35)
            turn_right()
            wait(500)
            andar_casa()
            break
        elif currentColor == ambient["casa"]: # Encontrou próxima - verificar objetos
            wait_to_drive(170)
            change_position()
            break
    
    ev3.screen.clear()
    ev3.screen.print("Col: " + str(robot_col) + "\nRow: " + str(robot_row))
    wait(2000)

def andar_bolor():
    #robot_col, robot_row
    global position_bolor
    # o bolor anda sempre ate se aproximar do robot, onde o bolor comeca na casa 5,5 e o robot na 0, 0 ele segue a prioridade N S E O
    if robot_row < position_bolor["row"]: # Vai andar para cima
        position_bolor["row"] -= 1
    elif robot_row > position_bolor["row"]: # Vai andar para baixo
        position_bolor["row"] += 1
    elif robot_row == position_bolor["row"]: # Vai andar para a esquerda/direita
        if robot_col < position_bolor["col"]:
            position_bolor["col"] -= 1
        elif robot_col > position_bolor["col"]:
            position_bolor["col"] += 1
  
    if robot_row == position_bolor["row"] and robot_col == position_bolor["col"]:
        ev3.screen.clear()
        ev3.screen.draw_text(10, 10, "DERROTA")
        wait(10000)
        exit()


def check_pause_and_wait(TEMPO_ENTRE_JOGADA):
    paused = False
    for i in range(TEMPO_ENTRE_JOGADA/100):
        if (touch_sensorLeft.pressed() or touch_sensorRight.pressed()) and not False:
            paused = True
            ev3.screen.print("EM PAUSA")
        wait(TEMPO_ENTRE_JOGADA/100)

    while paused:
        if touch_sensorLeft.pressed() or touch_sensorRight.pressed():
            paused = False
            ev3.screen.print("SAIU DE ESPERA")
        wait(100)

def _evaluate_move(new_row, new_col):
    """
    Avalia a qualidade de um movimento.
    - Baseia-se na proximidade à manteiga e nos riscos de bolor, torradeira ou barreiras.
    """
    score = 0

    # Penalidade para movimentos fora dos limites do tabuleiro
    if not (0 <= new_row < 6 and 0 <= new_col < 6):
        return -float('inf')  # Penalidade alta

    # Fator 1: Distância ao objetivo (manteiga)
    if distancia_manteiga[new_row][new_col] is not None:
        manteiga_distance = distancia_manteiga[new_row][new_col]
        score += (10 - manteiga_distance) * 10  # Quanto mais perto, maior o score

    # Fator 2: Evitar bolor
    bolor_distance = abs(new_row - position_bolor["row"]) + abs(new_col - position_bolor["col"])
    if bolor_distance <= 1:  # Penalidade alta se estiver próximo ao bolor
        score -= 100

    # Fator 3: Evitar torradeira
    if calor_torradeira[new_row][new_col] is not None and calor_torradeira[new_row][new_col] == 0:
        score -= 100  # Penalidade alta se entrar em uma torradeira

    # Fator 4: Evitar barreiras
    if ambient["barreira"] == color_sensor.color():
        score -= 50  # Penalidade para barreiras

    return score



def get_autonomous_move():
    """
    Determina o melhor movimento baseado em heurísticas.
    Retorna: ('row_delta', 'col_delta') para a direção do movimento.
    """
    directions = [
        (0, -1),  # Esquerda
        (0, 1),   # Direita
        (-1, 0),  # Cima
        (1, 0)    # Baixo
    ]
    best_move = None
    best_score = -float('inf')

    # Avalia cada direção possível
    for row_delta, col_delta in directions:
        new_row = robot_row + row_delta
        new_col = robot_col + col_delta
        score = _evaluate_move(new_row, new_col)

        if score > best_score:
            best_score = score
            best_move = (row_delta, col_delta)

    return best_move

def atualizar_matrizes():
    """
    Atualiza as matrizes de distância da manteiga e calor da torradeira
    com base na posição do robô, bolor e manteiga.
    """
    global distancia_manteiga, calor_torradeira

    # Atualiza a distância à manteiga
    for row in range(6):
        for col in range(6):
            distancia_manteiga[row][col] = abs(row - robot_row) + abs(col - robot_col)

    # Atualiza o calor da torradeira
    for row in range(6):
        for col in range(6):
            calor_torradeira[row][col] = abs(row - position_bolor["row"]) + abs(col - position_bolor["col"])


def determinar_estrategia():
    """
    Determina a estratégia com base nas posições do bolor e da manteiga.
    Retorna "EVITAR_BOLOR" ou "ALCANCAR_MANTEIGA".
    """
    manteiga_distance_robot = abs(robot_row - position_bolor["row"]) + abs(robot_col - position_bolor["col"])
    manteiga_distance_bolor = abs(position_bolor["row"] - robot_row) + abs(position_bolor["col"] - robot_col)

    if manteiga_distance_bolor < manteiga_distance_robot:
        return "EVITAR_BOLOR"
    return "ALCANCAR_MANTEIGA"


def realizar_jogada():
    global robot_row, robot_col

    # Atualize as matrizes de inteligência
    atualizar_matrizes()

    # Obtenha o próximo movimento
    move = get_autonomous_move()
    if move:
        row_delta, col_delta = move
        new_row = robot_row + row_delta
        new_col = robot_col + col_delta

        # Movimente o robô de acordo com a decisão
        if row_delta == -1:
            forward(100)  # Cima
        elif row_delta == 1:
            backward(100)  # Baixo
        elif col_delta == -1:
            turn_left()
            forward(100)  # Esquerda
        elif col_delta == 1:
            turn_right()
            forward(100)  # Direita

        # Atualize a posição do robô
        robot_row = new_row
        robot_col = new_col

        # Verifique os objetos após o movimento
        verify_objects()

        # Atualize as tabelas e exiba os dados
        get_all_objects()
        print_all_tables(distancia_manteiga, calor_torradeira)

        # Movimente o bolor
        andar_bolor()

    else:
        print("Nenhum movimento válido encontrado!")

    # Aguarde antes da próxima jogada
    check_pause_and_wait(TEMPO_ENTRE_JOGADA)


while True:
    realizar_jogada()


#disperse_table(calor_torradeira, 0, 0, 0)
#print_table(calor_torradeira, "Tabela de Distância da Torradeira")
#get_all_objects()