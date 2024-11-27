#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor, UltrasonicSensor)
from pybricks.parameters import Port, Stop, Color
from pybricks.tools import wait
from pybricks.robotics import DriveBase
from sys import exit
import time

# Inicialização
ev3 = EV3Brick()
color_sensor = ColorSensor(Port.S2)
touch_sensorLeft = TouchSensor(Port.S3)
touch_sensorRight = TouchSensor(Port.S4)
distance_sensor = UltrasonicSensor(Port.S1)
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
    Color.YELLOW: 8,
    Color.BROWN: 4,
    Color.GREEN: 2,
    Color.BLUE: 1,
    Color.BLACK: 0
}

is_first_move = True

distancia_manteiga = [[None] * 6 for _ in range(6)]
possible_zeros_manteiga = 36

calor_torradeira = [[None] * 6 for _ in range(6)]
possible_zeros_torradeira = 36

cheiro_bolor = [[None] * 6 for _ in range(6)]


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

def print_all_tables(dist_manteiga, calor_torrad, cheiro_bol):
    """
    Imprime todas as tabelas em sequência
    """
    print_table(dist_manteiga, "Tabela de Distância da Manteiga")
    print_table(calor_torrad, "Tabela de Calor da Torradeira")
    print_table(cheiro_bol, "Tabela de Cheiro de Bolor")

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
    for row in range(len(table1)):
        for col in range(len(table1[0])):
            if table[row][col] == 0:
                zeros += 1
                temp_table = [[None] * len(table[0]) for _ in range(len(table1))]
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
    global distancia_manteiga, calor_torradeira, cheiro_bolor, is_first_move

    distance_manteiga = get_distance("Distância Manteiga")
    if distance_manteiga and possible_zeros_manteiga != 1:
        if has_numbers(distancia_manteiga):
            disperse_table(aux, distance_manteiga, robot_row, robot_col)
            filter_table(distancia_manteiga, aux)
            distancia_manteiga, possible_zeros_manteiga = populate_tabela(distancia_manteiga)
            print_table(distancia_manteiga, "Tabela de Distância da Manteiga")
        else:
            disperse_table(distancia_manteiga, distance_manteiga, robot_row, robot_col)
    wait(1000)

    distance_torradeira = get_distance("Calor Torradeira")
    if distance_torradeira and possible_zeros_torradeira != 1:
        if has_numbers(calor_torradeira):
            disperse_table(aux, distance_torradeira, robot_row, robot_col)
            filter_table(calor_torradeira, aux)
            calor_torradeira, possible_zeros_torradeira = populate_tabela(calor_torradeira)
            print_table(calor_torradeira, "Tabela de Distância da Torradeira")
        else:
            disperse_table(calor_torradeira, distance_torradeira, robot_row, robot_col)
    wait(1000)

    distance_bolor = get_distance("Cheiro Bolor")
    if distance_bolor:
        disperse_table(cheiro_bolor, distance_bolor, robot_row, robot_col)
    wait(1000)

    

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
                wait(1000)
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
    return cheiro_bolor[robot_row][robot_col] == 0

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
        exit()

    if verify_bolor():
        ev3.screen.clear()
        ev3.screen.draw_text(10, 10, "DERROTA")
        wait(10000)
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

def realizar_jogada():
    get_all_objects()
    andar_casa()
    verify_objects()
    print_all_tables(distancia_manteiga, calor_torradeira, cheiro_bolor)
    wait(TEMPO_ENTRE_JOGADA)

#while True:
#    realizar_jogada()

#get_all_objects()