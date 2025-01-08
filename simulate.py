import random
import time
import os
from collections import deque

def has_numbers(table):
    return any(cell is not None for row in table for cell in row)

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
            if table1[row][col] != table2[row][col] and table1[row][col] != float('inf'):
                table1[row][col] = None

def filter_table_min(table1, table2):
    """
    Mantém os menores valores entre duas tabelas  
    """
    for row in range(len(table1)):
        for col in range(len(table1[0])):
            if table1[row][col] > table2[row][col]:
                table1[row][col] = table2[row][col]     
def count_zeros(table):
    count = 0
    for row in range(len(table)):
        for col in range(len(table[0])):
            if table[row][col] == 0:
                count += 1
    return count

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

def get_zero(table):
    for row in range(len(table)):
        for col in range(len(table[0])):
            if table[row][col] == 0:
                return row, col

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

# def populate_torradeira(table, row, col, inf=False):
#     if inf:
#         table[row][col] = float('inf')
#         if 0 <= row - 1 < len(table) and table[row - 1][col] == 0:
#             table[row - 1][col] = float('inf')
#         if 0 <= row + 1 < len(table) and table[row + 1][col] == 0:
#             table[row + 1][col] = float('inf')
#         if 0 <= col - 1 < len(table[0]) and table[row][col - 1] == 0:
#             table[row][col - 1] = float('inf')
#         if 0 <= col + 1 < len(table[0]) and table[row][col + 1] == 0:
#             table[row][col + 1] = float('inf')
#     else:
#         table[row][col] = 1
#         if 0 <= row - 1 < len(table) and table[row - 1][col] is None:
#             table[row - 1][col] = 0
#         if 0 <= row + 1 < len(table) and table[row + 1][col] is None:
#             table[row + 1][col] = 0
#         if 0 <= col - 1 < len(table[0]) and table[row][col - 1] is None:
#             table[row][col - 1] = 0
#         if 0 <= col + 1 < len(table[0]) and table[row][col + 1] is None:
#             table[row][col + 1] = 0

def populate_torradeira(table, row, col, inf=False):
    """
    Enhanced population of heat matrix that better tracks possible toaster locations
    Args:
        table: The heat matrix
        row, col: Current robot position
        inf: Whether to mark impossible locations
    """
    if inf:
        # Mark current position and adjacents as impossible toaster locations
        table[row][col] = float('inf')
        
        # Only mark adjacent positions as impossible if they haven't been confirmed as hot
        adjacent_positions = [
            (row - 1, col), (row + 1, col),
            (row, col - 1), (row, col + 1)
        ]
        
        for adj_row, adj_col in adjacent_positions:
            if 0 <= adj_row < len(table) and 0 <= adj_col < len(table[0]):
                if table[adj_row][adj_col] == 0:  # Only if it's marked as possible
                    table[adj_row][adj_col] = float('inf')
    else:
        # We found a hot spot
        table[row][col] = 1
        
        # Mark adjacent positions as potential toaster locations
        adjacent_positions = [
            (row - 1, col), (row + 1, col),
            (row, col - 1), (row, col + 1)
        ]
        
        for adj_row, adj_col in adjacent_positions:
            if 0 <= adj_row < len(table) and 0 <= adj_col < len(table[0]):
                if table[adj_row][adj_col] is None:
                    table[adj_row][adj_col] = 0  # Potential toaster location



class GameBoard:
    def __init__(self):
        self.size = 6
        self.board = [[' ' for _ in range(self.size)] for _ in range(self.size)]
        self.robot_pos = {'row': 0, 'col': 0}
        self.bolor_pos = {'row': 5, 'col': 5}
        self.manteiga_pos = None
        self.torradeira_pos = None
        self.game_over = False
        self.won = False
        self.skip = False
        self.has_butter = False
        self.need_return_home = False
        self.home_pos = {'row': 0, 'col': 0}
        
        # Matrizes de distância e calor
        self.distancia_manteiga = [[None] * self.size for _ in range(self.size)]
        self.known_manteiga = None #{'row': None, 'col': None}
        self.calor_torradeira = [[None] * self.size for _ in range(self.size)]
        self.known_torradeira = None #{'row': None, 'col': None}
        
        self.last_positions = []

        self.manteiga_strat = True
        # Estrutura para armazenar barreiras
        # Agora armazenamos as barreiras como pares de posições que não podem ser atravessadas
        self.barriers = set()  # Conjunto de tuplas ((row1, col1), (row2, col2))
        
        # Barreiras descobertas
        self.discovered_barriers = set()


        # Inicializar o jogo
        self.setup_game()

    def setup_game(self):
        # Posicionar manteiga aleatoriamente (não na posição inicial do robot ou bolor)
        while True:
            row = random.randint(0, self.size-1)
            col = random.randint(0, self.size-1)
            if (row, col) != (0, 0) and (row, col) != (5, 5):
                self.manteiga_pos = {'row': row, 'col': col}
                break
        # Posicionar torradeira aleatoriamente
        while True:
            row = random.randint(0, self.size-1)
            col = random.randint(0, self.size-1)
            if (row, col) != (0, 0) and (row, col) != (5, 5) and \
               (row, col) != (self.manteiga_pos['row'], self.manteiga_pos['col']):
                self.torradeira_pos = {'row': row, 'col': col}
                break
            
        self.manteiga_pos = {'row': 1, 'col': 5}        
        self.torradeira_pos = {'row': 1, 'col': 1}


        # Inicializar as barreiras
        self.setup_barriers()

        # Atualizar matrizes de distância e calor
        self.update_matrices()

    def setup_barriers(self):
        # Adicionar barreiras aleatórias em algumas posições
        num_barriers = random.randint(5, 10)  # Número aleatório de posições com barreiras
        
        # for _ in range(num_barriers):
        #     row = random.randint(0, self.size-1)
        #     col = random.randint(0, self.size-1)
        #     pos = (row, col)
            
        #     # Evitar posições importantes
        #     if (row == self.robot_pos['row'] and col == self.robot_pos['col']) or \
        #        (row == self.bolor_pos['row'] and col == self.bolor_pos['col']) or \
        #        (row == self.manteiga_pos['row'] and col == self.manteiga_pos['col']) or \
        #        (row == self.torradeira_pos['row'] and col == self.torradeira_pos['col']):
        #         continue
                
        #     # Escolher aleatoriamente uma direção para a barreira
        #     directions = []
        #     if row > 0:  # Pode ter barreira para cima
        #         directions.append(((row, col), (row-1, col)))
        #     if row < self.size-1:  # Pode ter barreira para baixo
        #         directions.append(((row, col), (row+1, col)))
        #     if col > 0:  # Pode ter barreira para esquerda
        #         directions.append(((row, col), (row, col-1)))
        #     if col < self.size-1:  # Pode ter barreira para direita
        #         directions.append(((row, col), (row, col+1)))
            
        #     if directions:
        #         barrier = random.choice(directions)
        #         # Adicionar a barreira nos dois sentidos
        #         self.barriers.add(barrier)
        #         self.barriers.add((barrier[1], barrier[0]))  # Adiciona a barreira no sentido oposto

        self.barriers.add(((2,0), (3,0)))
        self.barriers.add(((3,0), (2,0)))

        self.barriers.add(((2,1), (2,2)))
        self.barriers.add(((2,2), (2,1)))


    def discover_barriers(self, row, col):
        """Descobre as barreiras conectadas à posição atual"""
        current_pos = (row, col)
        discovered = False
        
        # Verificar todas as barreiras possíveis conectadas a esta posição
        for barrier in self.barriers:
            if barrier[0] == current_pos and barrier not in self.discovered_barriers:
                self.discovered_barriers.add(barrier)
                self.discovered_barriers.add((barrier[1], barrier[0]))  # Adiciona também no sentido oposto
                discovered = True
        
        return discovered
    
    def find_toaster_position(self):
        """
        Advanced method to find toaster position based on heat patterns
        Returns: Dictionary with row and col if found, None otherwise
        """
        # If we already found the toaster
        if hasattr(self, 'known_torradeira') and self.known_torradeira:
            return self.known_torradeira

        # Count cells marked as possible toaster locations (0s)
        zero_count = sum(1 for row in self.calor_torradeira 
                        for cell in row if cell == 0)

        # If only one possible location remains
        if zero_count == 1:
            for row in range(len(self.calor_torradeira)):
                for col in range(len(self.calor_torradeira[0])):
                    if self.calor_torradeira[row][col] == 0:
                        self.known_torradeira = {'row': row, 'col': col}
                        return self.known_torradeira

        # If we found multiple hot spots, try to triangulate
        hot_spots = []
        for row in range(len(self.calor_torradeira)):
            for col in range(len(self.calor_torradeira[0])):
                if self.calor_torradeira[row][col] == 1:
                    hot_spots.append((row, col))

        if len(hot_spots) >= 2:
            # Find intersection of possible toaster locations from multiple hot spots
            possible_locations = set()
            for hot_row, hot_col in hot_spots:
                current_possible = set()
                # Add adjacent positions
                adjacent_positions = [
                    (hot_row - 1, hot_col), (hot_row + 1, hot_col),
                    (hot_row, hot_col - 1), (hot_row, hot_col + 1)
                ]
                for adj_row, adj_col in adjacent_positions:
                    if (0 <= adj_row < len(self.calor_torradeira) and 
                        0 <= adj_col < len(self.calor_torradeira[0]) and
                        self.calor_torradeira[adj_row][adj_col] == 0):
                        current_possible.add((adj_row, adj_col))
                
                if not possible_locations:
                    possible_locations = current_possible
                else:
                    possible_locations &= current_possible

            # If we found exactly one intersection point
            if len(possible_locations) == 1:
                row, col = possible_locations.pop()
                self.known_torradeira = {'row': row, 'col': col}
                return self.known_torradeira

        return None
    def update_toaster_knowledge(self):
        """
        Main method to update toaster knowledge after each move
        """
        if self.known_torradeira is not None:
            return
        dist_torradeira = (abs(self.robot_pos['row'] - self.torradeira_pos['row']) + \
                        abs(self.robot_pos['col'] - self.torradeira_pos['col']))
        
        # Update heat matrix based on current position
        if dist_torradeira == 1:
            populate_torradeira(self.calor_torradeira, self.robot_pos['row'], self.robot_pos['col'])
        elif dist_torradeira == 0:
            self.known_torradeira = {'row': self.robot_pos['row'], 'col': self.robot_pos['col']}
        else:
            populate_torradeira(self.calor_torradeira, self.robot_pos['row'], self.robot_pos['col'], True)
        
        # Try to find toaster position
        toaster_pos = self.find_toaster_position()
        
        if toaster_pos:
            print(f"\n--------------------------------\nToaster found at position: ({toaster_pos['row']}, {toaster_pos['col']})")
            
    def update_matrices(self):
        aux = [[None] * 6 for _ in range(6)]

        # Atualizar matriz de distância da manteiga apenas se ainda não foi pega
        if self.manteiga_pos is not None and not self.has_butter:
            dist_manteiga = abs(self.robot_pos['row'] - self.manteiga_pos['row']) + \
                        abs(self.robot_pos['col'] - self.manteiga_pos['col'])
            if dist_manteiga:
                if has_numbers(self.distancia_manteiga):
                    disperse_table(aux, dist_manteiga, self.robot_pos['row'], self.robot_pos['col'])
                    filter_table(self.distancia_manteiga, aux)
                    self.distancia_manteiga, possible_zeros_manteiga = populate_tabela(self.distancia_manteiga)
                    if possible_zeros_manteiga == 1:
                        krow, kcol = get_zero(self.distancia_manteiga)
                        self.known_manteiga = {'row': krow, 'col': kcol}
                else:
                    disperse_table(self.distancia_manteiga, dist_manteiga, self.robot_pos['row'], self.robot_pos['col'])
        
        # Atualizar matriz de calor da torradeira
        self.update_toaster_knowledge()


    def print_matrices(self):
        print_table(self.distancia_manteiga, "Distância da Manteiga")
        print_table(self.calor_torradeira, "Calor da Torradeira")

    def get_barriers_for_position(self, row, col):
        """Retorna lista de direções bloqueadas para uma posição"""
        barriers_list = []
        pos = (row, col)
        
        for barrier in self.discovered_barriers:
            if barrier[0] == pos:
                # Determinar a direção da barreira
                other_row, other_col = barrier[1]
                if other_row < row:
                    barriers_list.append('U')
                elif other_row > row:
                    barriers_list.append('D')
                elif other_col < col:
                    barriers_list.append('L')
                elif other_col > col:
                    barriers_list.append('R')
        
        return barriers_list
        
    def can_move(self, from_pos, to_pos):
        """Verifica se o movimento entre duas posições é permitido"""
        # Verifica se existe uma barreira descoberta entre as posições
        barrier = (from_pos, to_pos)
        return barrier not in self.discovered_barriers

    def move_robot(self, direction):
        if self.game_over:
            return False

        new_row, new_col = self.robot_pos['row'], self.robot_pos['col']
        current_pos = (self.robot_pos['row'], self.robot_pos['col'])

        if direction == 'w':  # cima
            new_row -= 1
        elif direction == 's':  # baixo
            new_row += 1
        elif direction == 'a':  # esquerda
            new_col -= 1
        elif direction == 'd':  # direita
            new_col += 1

        # Verificar se o movimento é válido
        if 0 <= new_row < self.size and 0 <= new_col < self.size:
            new_pos = (new_row, new_col)
            
            # Verificar barreiras
            if not self.can_move(current_pos, new_pos):
                print("\nBarreira! Não é possível mover nessa direção.")
                return False

            # Verificar se está na torradeira
            if new_row == self.torradeira_pos['row'] and new_col == self.torradeira_pos['col']:
                self.game_over = True
                return True

            self.robot_pos['row'] = new_row
            self.robot_pos['col'] = new_col

            # Descobrir barreiras na nova posição
            if self.discover_barriers(new_row, new_col):
                print("\nBarreiras descobertas nesta posição!")

            # Verificar vitória/derrota
            self.check_game_state()
            return True
        return False

    def get_autonomous_move(self):
        """
        Determines the best move for the robot based on:
        - Distance to butter (manteiga)
        - Heat from toaster (torradeira)
        - Discovered barriers
        - Mold (bolor) position
        Returns: 'w', 'a', 's', or 'd'
        """
        possible_moves = []
        current_row, current_col = self.robot_pos['row'], self.robot_pos['col']
        directions = [('w', -1, 0), ('s', 1, 0), ('a', 0, -1), ('d', 0, 1)]
        
        # Check each possible move
        for move, row_delta, col_delta in directions:
            new_row = current_row + row_delta
            new_col = current_col + col_delta
            
            # Skip if move is invalid
            if not (0 <= new_row < self.size and 0 <= new_col < self.size):
                continue
                
            # Skip if there's a discovered barrier
            if not self.can_move((current_row, current_col), (new_row, new_col)):
                continue
                
            # Calculate score for this move
            score, change_strat = self._evaluate_move(new_row, new_col)
            possible_moves.append((move, score, change_strat))
        time.sleep(2)
        # If no valid moves, return random move
        if not possible_moves:
            return random.choice(['w', 'a', 's', 'd'])
        
        # Return move with highest score
        val = max(possible_moves, key=lambda x: x[1])
        return val[0], val[2]


    def move_robot(self, direction, strat):
        if self.game_over:
            return False

        new_row, new_col = self.robot_pos['row'], self.robot_pos['col']

        if direction == 'w':  # cima
            new_row -= 1
        elif direction == 's':  # baixo
            new_row += 1
        elif direction == 'a':  # esquerda
            new_col -= 1
        elif direction == 'd':  # direita
            new_col += 1

        # Verificar se o movimento é válido
        if 0 <= new_row < self.size and 0 <= new_col < self.size:
            # Verificar barreiras
            if not self.can_move((self.robot_pos['row'], self.robot_pos['col']), 
                               (new_row, new_col)):
                print("\nBarreira! Não é possível mover nessa direção.")
                return False

            # Verificar se está na torradeira
            if new_row == self.torradeira_pos['row'] and new_col == self.torradeira_pos['col']:
                self.skip = True

            self.robot_pos['row'] = new_row
            self.robot_pos['col'] = new_col

            self.last_positions.append((new_row, new_col))

            if strat:
                self.manteiga_strat = False
                print("Mudar estratégia-------------")
                time.sleep(1)

            # Descobrir barreiras na nova posição
            if self.discover_barriers(new_row, new_col):
                print("\nBarreiras descobertas nesta posição!")

            self.update_matrices()

            # Verificar vitória/derrota
            self.check_game_state()
            return True
        return False

    def simulate_move_bolor(self, robot_row, robot_col, new_row=None, new_col=None):
        if self.game_over:
            return None, None

        if new_row is None or new_col is None:
            new_row, new_col = self.bolor_pos['row'], self.bolor_pos['col']

        if robot_row < new_row:  # Vai andar para cima
            new_row -= 1
        elif robot_row > new_row:  # Vai andar para baixo
            new_row += 1
        elif robot_row == new_row:  # Vai andar para a esquerda/direita
            if robot_col < new_col:
                new_col -= 1
            elif robot_col > new_col:
                new_col += 1
            
        return new_row, new_col


    def move_bolor(self):
        if self.game_over:
            return

        self.bolor_pos['row'], self.bolor_pos['col'] = self.simulate_move_bolor(self.robot_pos['row'], self.robot_pos['col'])

        # Verificar vitória/derrota
        self.check_game_state()



    def _evaluate_move(self, new_row, new_col):
        score = 0
        print(f"New position: ({new_row}, {new_col})")
        
        if (0 > new_row > self.size and 0 > new_col > self.size):
            print("Fora dos limites")
            return -float('inf'), False
        
        change_start = False
        
        # Simulate mold movement first
        bolor_row, bolor_col = self.simulate_move_bolor(new_row, new_col)
        
        # If returning home
        if self.need_return_home:
            home_distance = abs(new_row - self.home_pos['row']) + abs(new_col - self.home_pos['col'])
            score += (10 - home_distance) * 10
            
            if new_row == self.home_pos['row'] and new_col == self.home_pos['col']:
                score += 1000
                
            if new_row == bolor_row and new_col == bolor_col:
                score -= 2000
                
            if new_row == self.bolor_pos['row'] or new_col == self.bolor_pos['col']:
                score -= 15

            # Additional penalty for positions near barriers
            # for barrier in self.discovered_barriers:
            #     barrier_start, barrier_end = barrier
            #     if (abs(new_row - barrier_start[0]) + abs(new_col - barrier_start[1])) <= 1:
            #         score -= 50  # Penalize being next to a barrier
            
            print(f"Score: {score}")
            return score, False

        # If using butter strategy and haven't got butter yet
        elif self.manteiga_strat and not self.has_butter and self.manteiga_pos is not None:
            if self.known_manteiga:
                butter_distance = abs(new_row - self.known_manteiga['row']) + abs(new_col - self.known_manteiga['col'])
                bolor_to_butter = abs(bolor_row - self.known_manteiga['row']) + abs(bolor_col - self.known_manteiga['col'])
                
                print(f"Distance to butter: {butter_distance}")
                print(f"Distance bolor to butter: {bolor_to_butter}")
                
                if butter_distance < bolor_to_butter:
                    score += (10 - butter_distance) * 10
                else:
                    change_start = True
                    score -= 35
            else:
                # Look for nearest zero
                nrow, ncol, distance = find_nearest_zero(self.distancia_manteiga, self.robot_pos['row'], self.robot_pos['col'])
                if nrow is not None:
                    crow, ccol, cdistance = find_nearest_zero(self.distancia_manteiga, new_row, new_col)
                    if crow is not None:
                        if cdistance < distance:
                            score += 100

        # Using toaster strategy
        else:
            if self.known_torradeira:
                distance_bolor_robot = (abs(bolor_row - new_row) + abs(bolor_col - new_col))
                distance_bolor_torradeira = abs(self.bolor_pos['row'] - self.known_torradeira['row']) + abs(self.bolor_pos['col'] - self.known_torradeira['col'])
                print(f"Distance bolor to robot: {distance_bolor_robot}")
                if (new_row == self.known_torradeira['row'] and new_col == self.known_torradeira['col']):
                    if (distance_bolor_robot >=2 and distance_bolor_robot < distance_bolor_torradeira):
                        score += 500
                    else:
                        score -= 500
                else:
                    new_distance_bolor_torradeira = abs(bolor_row - self.known_torradeira['row']) + abs(bolor_col - self.known_torradeira['col'])

                    if new_distance_bolor_torradeira < distance_bolor_torradeira:
                        val = 50*(distance_bolor_torradeira - new_distance_bolor_torradeira)
                        score += val
                        #score -= 10*(distance_bolor_robot-new_distance_bolor_robot)
                    else:
                        score -= 15

                    if (bolor_row == self.known_torradeira['row'] and bolor_col == self.known_torradeira['col']):
                        score += 1500
        # Common penalties
        if new_row == bolor_row and new_col == bolor_col:
            score -= 5000

        if self.known_manteiga is not None and bolor_row == self.known_manteiga['row'] and bolor_col == self.known_manteiga['col']:
            score -= 2000

        # Penalize previously visited positions
        for i in range(len(self.last_positions)):
            if (new_row, new_col) == self.last_positions[i]:
                score -= (5*i+5)
                print(f"Movimento antigo {i}: {5*i}")
                break

        print(f"Score: {score}")
        return score, change_start
        

    def play_game_autonomous(self):
        """
        Runs the game autonomously using the heuristic movement
        """
        moves_count = 0
        max_moves = 100  # Prevent infinite loops
        
        try:
            while not self.game_over and moves_count < max_moves:
                self.display()
                time.sleep(1)  # Add delay to make movement visible
                
                # Get and execute best move
                if self.skip:
                    self.skip = False
                    print("\nBolor está na mesma posição que o robot. Pular jogada.")
                    self.move_bolor()
                    continue

                move, strat = self.get_autonomous_move()
                if self.move_robot(move, strat):
                    self.move_bolor()
                    moves_count += 1
            
            self.display()
            if self.won:
                print("\nRobot wins!")
            else:
                print("\nGame Over! Mold wins!")
            print(f"Total moves: {moves_count}")
            
        except KeyboardInterrupt:
            print("\nJogo interrompido pelo usuário!")
            self.display()  # Show final state
            print(f"Total moves before interruption: {moves_count}")
        except Exception as e:
            print(f"\nErro inesperado: {str(e)}")
        
    def check_game_state(self):
        # Check if robot reached butter
        if (self.manteiga_pos is not None and 
            self.robot_pos['row'] == self.manteiga_pos['row'] and 
            self.robot_pos['col'] == self.manteiga_pos['col'] and 
            not self.has_butter):
            self.has_butter = True
            self.need_return_home = True
            self.manteiga_pos = None
            print("\nManteiga encontrada! A voltar para casa inicial...")
            return
        
        # Check if robot returned home with butter
        if (self.has_butter and 
            self.robot_pos['row'] == self.home_pos['row'] and 
            self.robot_pos['col'] == self.home_pos['col']):
            self.game_over = True
            self.won = True
            return

        # Check if mold caught the robot
        if (self.bolor_pos['row'] == self.robot_pos['row'] and 
            self.bolor_pos['col'] == self.robot_pos['col']):
            self.game_over = True
            self.won = False
            return

        # Check if mold reached toaster
        if (self.bolor_pos['row'] == self.torradeira_pos['row'] and 
            self.bolor_pos['col'] == self.torradeira_pos['col']):
            self.game_over = True
            self.won = True
            return

    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n  0 1 2 3 4 5")
        for i in range(self.size):
            row_str = f"{i} "
            for j in range(self.size):
                pos_char = '.'
                if i == self.robot_pos['row'] and j == self.robot_pos['col']:
                    pos_char = 'R*' if self.has_butter else 'R'  # Add * when robot has butter
                elif i == self.bolor_pos['row'] and j == self.bolor_pos['col']:
                    pos_char = 'B'
                elif self.manteiga_pos and i == self.manteiga_pos['row'] and j == self.manteiga_pos['col']:
                    pos_char = 'M'
                elif i == self.torradeira_pos['row'] and j == self.torradeira_pos['col']:
                    pos_char = 'T'
                
                barriers = self.get_barriers_for_position(i, j)
                if barriers:
                    pos_char = '#'
                
                row_str += pos_char + ' '
            
            # Mostrar barreiras descobertas para esta linha
            barriers_info = []
            for j in range(self.size):
                barriers = self.get_barriers_for_position(i, j)
                if barriers:
                    barriers_info.append(f"({i},{j}): {','.join(sorted(barriers))}")
            
            print(row_str + "  " + "  ".join(barriers_info))


        print("\nLegenda:")
        print("R - Robot")
        print("B - Bolor")
        print("M - Manteiga")
        print("T - Torradeira")
        print("# - Posição com barreiras descobertas")
        print("U,D,L,R - Direções bloqueadas (Cima, Baixo, Esquerda, Direita)")
        #self.print_matrices()

def play_game():
    game = GameBoard()
    
    print("\nBem-vindo ao jogo do Robot e Bolor!")
    print("Use WASD para mover o robot (w-cima, a-esquerda, s-baixo, d-direita)")
    print("Pressione 'q' para sair")
    
    while not game.game_over:
        game.display()
        
        # Input do jogador
        move = input("\nPróximo movimento (WASD): ").lower()
        if move == 'q':
            break
        
        if move in ['w', 'a', 's', 'd']:
            if game.move_robot(move):
                game.move_bolor()
        
    game.display()
    if game.won:
        print("\nParabéns! O ganhaste!")
        print(f"Total de movimentos: {len(game.last_positions)}")
        if game.known_manteiga:
            print(f"O robot sabe onde está a manteiga: ({game.known_manteiga['row']}, {game.known_manteiga['col']})")
        else:
            print("O robot não sabe onde está a manteiga.")

        #Mostra se sabe da torradeira
        if game.known_torradeira:
            print(f"O robot sabe onde está a torradeira: ({game.known_torradeira['row']}, {game.known_torradeira['col']})")
        else:
            print("O robot não sabe onde está a torradeira.")

    else:
        print("\nGame Over! O bolor venceu!")

if __name__ == "__main__":
    game = GameBoard()
    # mode = input("Choose mode (1 for manual, 2 for autonomous): ")
    # if mode == "1":
    #     play_game()
    # else:
    game.play_game_autonomous()
        
