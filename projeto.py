#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor, UltrasonicSensor)
from pybricks.parameters import Port, Stop, Color
from pybricks.tools import wait
from pybricks.robotics import DriveBase

from sys import exit
import time
import random
from collections import deque

# -------------------------------
# INICIALIZAÇÃO (variáveis EV3)
# -------------------------------
ev3 = EV3Brick()
color_sensor = ColorSensor(Port.S2)
touch_sensorLeft = TouchSensor(Port.S3)
touch_sensorRight = TouchSensor(Port.S4)
ultrasonic_sensor = UltrasonicSensor(Port.S1)
left_motor = Motor(Port.D)
right_motor = Motor(Port.A)

robot = DriveBase(left_motor, right_motor, wheel_diameter=50, axle_track=150)

robot_col = 0
robot_row = 0
TEMPO_ENTRE_JOGADA = 10000  # 10 segundos

# Direção inicial
change_col = 1
change_row = 0

ambient = {
    "barreira": Color.RED,
    "casa": Color.BLACK,
}

color_weights = {
    Color.BROWN: 4,
    Color.GREEN: 2,
    Color.BLUE: 1,
}

is_first_move = True

# -------------------------------
# Tabelas e variáveis do jogo
# -------------------------------
distancia_manteiga = [[None] * 6 for _ in range(6)]
possible_zeros_manteiga = 36

calor_torradeira = [[None] * 6 for _ in range(6)]
possible_zeros_torradeira = 36

# Posição do bolor
position_bolor = {'row': 5, 'col': 5}

# Variável para indicar se o robô já pegou a manteiga
has_manteiga = False

# Posição calculada/descoberta da torradeira
posicao_torradeira = {"row": None, "col": None}

# -------------------------------
# NOVAS VARIÁVEIS GLOBAIS
# (vindas da lógica de evaluate_move)
# -------------------------------
last_positions = []             # Para penalizar revisitas
need_return_home = False        # Se quisermos habilitar “retornar para (0,0)”
home_pos = {'row': 0, 'col': 0} # Posição da “casa”/início
manteiga_strat = True           # Estratégia de procurar manteiga
known_manteiga = None           # Se descobrimos onde está a manteiga
known_torradeira = None         # Se descobrimos onde está a torradeira

# -------------------------------
#  Funções auxiliares
# -------------------------------
def has_numbers(table):
    return any(cell is not None for row in table for cell in row)

def disperse_table(table, value, row, col, radius=6):
    for r in range(row - radius, row + radius + 1):
        for c in range(col - radius, col + radius + 1):
            if 0 <= r < len(table) and 0 <= c < len(table[0]):
                distance = abs(r - row) + abs(c - col)
                decremented_value = abs(value - distance)
                table[r][c] = decremented_value

def filter_table(table1, table2):
    for row in range(len(table1)):
        for col in range(len(table1[0])):
            if table1[row][col] != table2[row][col]:
                table1[row][col] = None

def filter_table_min(table1, table2):
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

def print_table(table, table_name):
    print("\n" + "=" * 50)
    print(table_name)
    print("=" * 50)
    print("     ", end="")
    for col in range(6):
        print(" {:^5} ".format(col), end="")
    print("\n")
    for row in range(6):
        print(" {} |".format(row), end="")
        for col in range(6):
            value = table[row][col]
            if value is None:
                print("  -   ", end="")
            else:
                print(" {:.2f} ".format(value), end="")
        print()
    print()

def print_all_tables(dist_manteiga, calor_torrad):
    print_table(dist_manteiga, "Tabela de Distância da Manteiga")
    print_table(calor_torrad, "Tabela de Calor da Torradeira")

# -------------------------------
# BFS para achar zero
# -------------------------------
def find_nearest_zero(table, start_row, start_col):
    rows, cols = len(table), len(table[0])
    visited = [[False] * cols for _ in range(rows)]
    queue = deque([(start_row, start_col, 0)])  # (row, col, dist)

    while queue:
        row, col, distance = queue.popleft()
        if row < 0 or col < 0 or row >= rows or col >= cols or visited[row][col]:
            continue
        visited[row][col] = True
        if table[row][col] == 0:
            return (row, col, distance)
        # Adiciona vizinhos
        queue.extend([
            (row - 1, col, distance + 1),
            (row + 1, col, distance + 1),
            (row, col - 1, distance + 1),
            (row, col + 1, distance + 1)
        ])
    return None

# -------------------------------
#  MOVIMENTOS
# -------------------------------
def forward(distance):
    robot.straight(distance)

def backward(distance):
    robot.straight(-distance)

def turn_left():
    global change_col, change_row
    robot.turn(-78)
    change_col, change_row = change_row, -change_col

def turn_right():
    global change_col, change_row
    robot.turn(78)
    change_col, change_row = -change_row, change_col

def change_position():
    global robot_col, robot_row
    robot_col += change_col
    robot_row += change_row

# -------------------------------
#  SIMULATE MOVE BOLOR
#  (para uso no evaluate_move expandido)
# -------------------------------
def simulate_move_bolor(robot_target_row, robot_target_col, tmp_bolor_row=None, tmp_bolor_col=None):
    """
    Simula como o bolor se moveria se o robô fosse para (robot_target_row, robot_target_col).
    Se tmp_bolor_row/col não forem dados, usa a posição global do bolor.
    Retorna (novo_bolor_row, novo_bolor_col).
    """
    global position_bolor
    if tmp_bolor_row is None or tmp_bolor_col is None:
        tmp_bolor_row = position_bolor['row']
        tmp_bolor_col = position_bolor['col']

    # Move 1 passo na direção do robô
    if robot_target_row < tmp_bolor_row:
        tmp_bolor_row -= 1
    elif robot_target_row > tmp_bolor_row:
        tmp_bolor_row += 1
    elif robot_target_row == tmp_bolor_row:
        if robot_target_col < tmp_bolor_col:
            tmp_bolor_col -= 1
        elif robot_target_col > tmp_bolor_col:
            tmp_bolor_col += 1

    return tmp_bolor_row, tmp_bolor_col

# -------------------------------
# LÓGICA DE VERIFICAÇÃO
# (manteiga, torradeira, bolor)
# -------------------------------
def verify_manteiga():
    return (distancia_manteiga[robot_row][robot_col] == 0)

def verify_torradeira():
    return (calor_torradeira[robot_row][robot_col] == 0)

def verify_bolor():
    return (robot_row == position_bolor["row"] and robot_col == position_bolor["col"])

def verify_objects():
    global has_manteiga

    # Se o robô estiver em uma casa de manteiga e ainda não tiver pegado
    if (not has_manteiga) and verify_manteiga():
        ev3.screen.clear()
        ev3.screen.draw_text(10, 10, "Pegou a manteiga!")
        has_manteiga = True
        wait(2000)
        # (Opcional) Remover a manteiga do mapa:
        # distancia_manteiga[robot_row][robot_col] = None

    # Se já pegou a manteiga e voltou para (0,0), vence
    if has_manteiga and robot_row == 0 and robot_col == 0:
        ev3.screen.clear()
        ev3.screen.draw_text(10, 10, "VITÓRIA! Manteiga em (0,0).")
        wait(5000)
        exit()

    # Se está em torradeira (calor_torradeira == 0)
    if verify_torradeira():
        ev3.screen.clear()
        ev3.screen.draw_text(10, 10, "CAISTE NA TORRADEIRA")
        wait(5000)

    # Se o bolor pegou o robô
    if verify_bolor():
        ev3.screen.clear()
        ev3.screen.draw_text(10, 10, "GAME OVER! Bolor encontrou o robô")
        wait(5000)
        exit()

# -------------------------------
# ANDAR CASA e BOLOR
# -------------------------------
def andar_casa():
    robot.drive(40, 0)
    while True:
        currentColor = color_sensor.color()
        if currentColor == ambient["barreira"]:
            robot.stop()
            backward(35)
            turn_right()
            wait(500)
            andar_casa()
            break
        elif currentColor == ambient["casa"]:
            wait_to_drive(170)
            change_position()
            break
    ev3.screen.clear()
    ev3.screen.print("Col: " + str(robot_col) + "\nRow: " + str(robot_row))
    wait(2000)

def andar_bolor():
    global position_bolor
    if robot_row < position_bolor["row"]:
        position_bolor["row"] -= 1
    elif robot_row > position_bolor["row"]:
        position_bolor["row"] += 1
    elif robot_row == position_bolor["row"]:
        if robot_col < position_bolor["col"]:
            position_bolor["col"] -= 1
        elif robot_col > position_bolor["col"]:
            position_bolor["col"] += 1

    # Se o bolor pegou o robô
    if robot_row == position_bolor["row"] and robot_col == position_bolor["col"]:
        ev3.screen.clear()
        ev3.screen.draw_text(10, 10, "DERROTA: Bolor")
        wait(5000)
        exit()

def check_pause_and_wait(TEMPO_ENTRE_JOGADA):
    paused = False
    for i in range(TEMPO_ENTRE_JOGADA//100):
        if touch_sensorLeft.pressed() or touch_sensorRight.pressed():
            paused = True
            ev3.screen.print("EM PAUSA")
            break
        wait(100)

    while paused:
        if touch_sensorLeft.pressed() or touch_sensorRight.pressed():
            paused = False
            ev3.screen.print("SAIU DE ESPERA")
        wait(100)

def wait_to_drive(distance, speed=40):
    wait(distance/speed*1000)
    robot.stop()

# -------------------------------
# NOVO evaluate_move (expandido)
# -------------------------------
def evaluate_move(new_row, new_col):
    """
    Combina características do _evaluate_move e do evaluate_move antigo,
    incluindo checagens de bolor, barreiras, revisitadas, manteiga, etc.
    """
    global position_bolor, last_positions
    global need_return_home, home_pos
    global manteiga_strat, has_manteiga, known_manteiga
    global known_torradeira
    global distancia_manteiga, calor_torradeira
    global color_sensor, ambient

    size = 6

    score = 0
    change_start = False  # se quiser alterar alguma estratégia externamente

    print("New position: (", new_row, ", ", new_col, ")")

    # 1) Fora dos limites?
    if not (0 <= new_row < size and 0 <= new_col < size):
        print("Fora dos limites")
        return -float('inf')

    # 2) Simular movimento do bolor
    bolor_row, bolor_col = simulate_move_bolor(new_row, new_col)

    # 3) Se “precisamos voltar para casa”
    if need_return_home:
        home_distance = abs(new_row - home_pos['row']) + abs(new_col - home_pos['col'])
        score += (10 - home_distance) * 10
        # Bônus se chegar em casa
        if new_row == home_pos['row'] and new_col == home_pos['col']:
            score += 1000
        # Se o bolor for cair na mesma casa
        if new_row == bolor_row and new_col == bolor_col:
            score -= 2000
        # Penaliza se estiver na mesma linha/col do bolor
        if (new_row == position_bolor['row']) or (new_col == position_bolor['col']):
            score -= 15
        print("Score (return_home):", score)
        return score

    # 4) Estratégia de manteiga
    elif manteiga_strat and (not has_manteiga) and (known_manteiga is not None):
        # Distâncias
        butter_distance = abs(new_row - known_manteiga['row']) + abs(new_col - known_manteiga['col'])
        bolor_to_butter = abs(bolor_row - known_manteiga['row']) + abs(bolor_col - known_manteiga['col'])
        print("Distance to butter:", butter_distance)
        print("Distance bolor to butter:", bolor_to_butter)
        if butter_distance <= bolor_to_butter:
            # Bom se chegamos antes do bolor
            score += (10 - butter_distance) * 10
        else:
            # Penaliza e sinaliza mudança de estrat
            change_start = True
            score -= 35

    # Se (known_manteiga é None) mas a gente ainda não pegou, poderia BFS...
    # (Igual no snippet do simulate)

    else:
        # 5) Estratégia da torradeira
        if known_torradeira is not None:
            # Se new_row,new_col == known torradeira
            if new_row == known_torradeira['row'] and new_col == known_torradeira['col']:
                # Simula bolor e vê se ele cairia tb
                temp_bolor_row, temp_bolor_col = simulate_move_bolor(new_row, new_col, bolor_row, bolor_col)
                if temp_bolor_row == known_torradeira['row'] and temp_bolor_col == known_torradeira['col']:
                    score += 1500
                else:
                    distance_bolor_torr = abs(position_bolor['row'] - known_torradeira['row']) \
                                          + abs(position_bolor['col'] - known_torradeira['col'])
                    new_dist_bolor_torr = abs(bolor_row - known_torradeira['row']) \
                                          + abs(bolor_col - known_torradeira['col'])
                    if new_dist_bolor_torr < distance_bolor_torr:
                        score += 50*(distance_bolor_torr - new_dist_bolor_torr)
                    else:
                        score -= 15

    # 6) Penalidades gerais
    # Se new_row == bolor => penaliza
    if new_row == bolor_row and new_col == bolor_col:
        score -= 2000

    # Se a cor do sensor for barreira => penaliza
    if color_sensor.color() == ambient["barreira"]:
        score -= 50

    # Se existe valor em distancia_manteiga => soma
    if distancia_manteiga[new_row][new_col] is not None:
        manteiga_distance = distancia_manteiga[new_row][new_col]
        score += (10 - manteiga_distance) * 10

    # 7) Penalizar revisitas / loop 1,0 e 2,0
    for i, pos in enumerate(last_positions):
        if (new_row, new_col) == pos:
            score -= 5*(len(last_positions)-i)  
            print("Penalizado por revisitar", pos)
            break

    if (new_row, new_col) in [(1,0), (2,0)]:
        score -= 10

    print("Score:", score)
    return score

# -------------------------------
# get_autonomous_move
# -------------------------------
def get_autonomous_move():
    directions = [
        (0, -1),  # Esquerda
        (0, 1),   # Direita
        (-1, 0),  # Cima
        (1, 0)    # Baixo
    ]
    best_move = None
    best_score = -float('inf')
    for row_delta, col_delta in directions:
        new_row = robot_row + row_delta
        new_col = robot_col + col_delta
        # Chamamos a nova evaluate_move (expandida)
        score = evaluate_move(new_row, new_col)
        if score > best_score:
            best_score = score
            best_move = (row_delta, col_delta)
    return best_move

def atualizar_direcao(row_delta, col_delta):
    global change_row, change_col
    if row_delta == -1 and col_delta == 0:
        while not (change_row == -1 and change_col == 0):
            turn_left()
    elif row_delta == 1 and col_delta == 0:
        while not (change_row == 1 and change_col == 0):
            turn_left()
    elif row_delta == 0 and col_delta == -1:
        while not (change_row == 0 and change_col == -1):
            turn_left()
    elif row_delta == 0 and col_delta == 1:
        while not (change_row == 0 and change_col == 1):
            turn_left()

# -------------------------------
# DETECTAR TORRADEIRA (78°)
# -------------------------------
def determinar_direcao_torradeira():
    global posicao_torradeira, change_row, change_col

    min_distance = 500
    best_direction = None

    left_motor.reset_angle(0)

    for _ in range(5):
        distance = ultrasonic_sensor.distance()
        if distance <= 500 and distance < min_distance:
            min_distance = distance
            best_direction = (change_row, change_col)
        turn_right()
        wait(500)

    robot.stop()
    if best_direction is not None:
        delta_row, delta_col = best_direction
        torradeira_row = robot_row + delta_row
        torradeira_col = robot_col + delta_col
        posicao_torradeira["row"] = torradeira_row
        posicao_torradeira["col"] = torradeira_col
        ev3.screen.clear()
        ev3.screen.draw_text(10, 10, "Torradeira detectada!")
        ev3.screen.draw_text(10, 30, "Distância: " + str(min_distance) + " mm")
        ev3.screen.draw_text(10, 50, "Pos: (" + str(torradeira_row) + ", " + str(torradeira_col) + ")")
    else:
        ev3.screen.clear()
        ev3.screen.draw_text(10, 10, "Torradeira não detectada.")

def atualizar_direcao_para_angulo(target_angle):
    current_angle = left_motor.angle()
    angle_to_turn = target_angle - current_angle
    robot.turn(angle_to_turn)

# -------------------------------
# LOOP PRINCIPAL
# -------------------------------
def realizar_jogada():
    # Atualiza a info do ambiente
    get_all_objects()
    # Verifica se o robô pegou manteiga, ou se bolor pegou robô, etc.
    verify_objects()

    distance_torradeira = get_distance("Calor Torradeira")
    if distance_torradeira == 1:
        ev3.screen.print("Calor da torradeira detectado!")
        determinar_direcao_torradeira()
    else:
        ev3.screen.print("Nenhum calor detectado.")
        ev3.screen.print(distance_torradeira)

    # Usa a IA de movimento
    move = get_autonomous_move()
    if move:
        row_delta, col_delta = move

        # Guarda a posição atual para penalizar revisitas
        last_positions.append((robot_row, robot_col))

        # Ajusta direção e anda
        atualizar_direcao(row_delta, col_delta)
        andar_casa()
    else:
        ev3.screen.clear()
        ev3.screen.draw_text(10, 10, "SEM MOVIMENTOS VÁLIDOS")
        wait(5000)
        exit()

    # Move o bolor
    andar_bolor()

    # Mostra tabelas
    print_all_tables(distancia_manteiga, calor_torradeira)

    # Faz pausa
    check_pause_and_wait(TEMPO_ENTRE_JOGADA)

def main():
    while True:
        realizar_jogada()

if __name__ == "__main__":
    main()
