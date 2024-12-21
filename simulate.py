import random
import time
import os

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
        
        # Matrizes de distância e calor
        self.distancia_manteiga = [[None] * self.size for _ in range(self.size)]
        self.calor_torradeira = [[None] * self.size for _ in range(self.size)]
        
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

        # Inicializar as barreiras
        self.setup_barriers()

        # Atualizar matrizes de distância e calor
        self.update_matrices()

    def setup_barriers(self):
        # Adicionar barreiras aleatórias em algumas posições
        num_barriers = random.randint(5, 10)  # Número aleatório de posições com barreiras
        
        for _ in range(num_barriers):
            row = random.randint(0, self.size-1)
            col = random.randint(0, self.size-1)
            pos = (row, col)
            
            # Evitar posições importantes
            if (row == self.robot_pos['row'] and col == self.robot_pos['col']) or \
               (row == self.bolor_pos['row'] and col == self.bolor_pos['col']) or \
               (row == self.manteiga_pos['row'] and col == self.manteiga_pos['col']) or \
               (row == self.torradeira_pos['row'] and col == self.torradeira_pos['col']):
                continue
                
            # Escolher aleatoriamente uma direção para a barreira
            directions = []
            if row > 0:  # Pode ter barreira para cima
                directions.append(((row, col), (row-1, col)))
            if row < self.size-1:  # Pode ter barreira para baixo
                directions.append(((row, col), (row+1, col)))
            if col > 0:  # Pode ter barreira para esquerda
                directions.append(((row, col), (row, col-1)))
            if col < self.size-1:  # Pode ter barreira para direita
                directions.append(((row, col), (row, col+1)))
            
            if directions:
                barrier = random.choice(directions)
                # Adicionar a barreira nos dois sentidos
                self.barriers.add(barrier)
                self.barriers.add((barrier[1], barrier[0]))  # Adiciona a barreira no sentido oposto


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


    def update_matrices(self):
        aux = [[None] * 6 for _ in range(6)]

        # Atualizar matriz de distância da manteiga
        dist_manteiga = abs(self.robot_pos['row'] - self.manteiga_pos['row']) + abs(self.robot_pos['col'] - self.manteiga_pos['col'])
        if dist_manteiga:
            if has_numbers(self.distancia_manteiga):
                disperse_table(aux, dist_manteiga, self.robot_pos['row'], self.robot_pos['col'])
                filter_table(self.distancia_manteiga, aux)
                self.distancia_manteiga, possible_zeros_manteiga = populate_tabela(self.distancia_manteiga)
            else:
                disperse_table(self.distancia_manteiga, dist_manteiga, self.robot_pos['row'], self.robot_pos['col'])

        # Atualizar matriz de calor da torradeira
        
        dist_torradeira = abs(self.robot_pos['row'] - self.torradeira_pos['row']) + abs(self.robot_pos['col'] - self.torradeira_pos['col'])
        if dist_torradeira <= 1:
            if has_numbers(self.calor_torradeira):
                disperse_table(aux, dist_torradeira, self.robot_pos['row'], self.robot_pos['col'])
                filter_table(self.calor_torradeira, aux)
                self.calor_torradeira, possible_zeros_torradeira = populate_tabela(self.calor_torradeira)
            else:
                disperse_table(self.calor_torradeira, dist_torradeira, self.robot_pos['row'], self.robot_pos['col'])
    
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



    def move_robot(self, direction):
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
                self.game_over = True
                return True

            self.robot_pos['row'] = new_row
            self.robot_pos['col'] = new_col

            # Descobrir barreiras na nova posição
            if self.discover_barriers(new_row, new_col):
                print("\nBarreiras descobertas nesta posição!")

            self.update_matrices()

            # Verificar vitória/derrota
            self.check_game_state()
            return True
        return False

    def move_bolor(self):
        if self.game_over:
            return

        if self.robot_pos['row'] < self.bolor_pos['row']: # Vai andar para cima
            self.bolor_pos['row'] -= 1
        elif self.robot_pos['row'] > self.bolor_pos['row']: # Vai andar para baixo
            self.bolor_pos['row'] += 1
        elif self.robot_pos['row'] == self.bolor_pos['row']: # Vai andar para a esquerda/direita
            if self.robot_pos['row'] < self.bolor_pos['col']:
                self.bolor_pos['col'] -= 1
            elif self.robot_pos['row'] > self.bolor_pos['col']:
                self.bolor_pos['col'] += 1

        # Verificar vitória/derrota
        self.check_game_state()





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
            score = self._evaluate_move(new_row, new_col)
            possible_moves.append((move, score))
        
        # If no valid moves, return random move
        if not possible_moves:
            return random.choice(['w', 'a', 's', 'd'])
        
        # Return move with highest score
        return max(possible_moves, key=lambda x: x[1])[0]

    def _evaluate_move(self, new_row, new_col):
        """
        Evaluates a potential move position and returns a score.
        Higher score = better move
        """
        score = 0
        
        # Factor 1: Distance to butter
        butter_distance = self.distancia_manteiga[new_row][new_col]
        if butter_distance is not None:
            # Lower distance = higher score
            score += (10 - butter_distance) * 2
        
        # Factor 2: Heat from toaster
        heat_value = self.calor_torradeira[new_row][new_col]
        if heat_value is not None:
            # Higher heat = lower score
            score -= heat_value * 3
        
        # Factor 3: Distance from mold
        mold_distance = abs(new_row - self.bolor_pos['row']) + abs(new_col - self.bolor_pos['col'])
        if mold_distance < 2:  # If mold is too close
            score -= 20
        else:
            score += mold_distance
            
        # Factor 4: Avoid moving towards mold
        if (new_row == self.bolor_pos['row'] or new_col == self.bolor_pos['col']):
            score -= 5
        
        # Bonus: Reaching butter position
        if (new_row == self.manteiga_pos['row'] and new_col == self.manteiga_pos['col']):
            score += 50
            
        # Penalty: Moving to toaster position
        if (new_row == self.torradeira_pos['row'] and new_col == self.torradeira_pos['col']):
            score -= 100
        
        return score

    def play_game_autonomous(self):
        """
        Runs the game autonomously using the heuristic movement
        """
        moves_count = 0
        max_moves = 100  # Prevent infinite loops
        
        while not self.game_over and moves_count < max_moves:
            self.display()
            time.sleep(2)  # Add delay to make movement visible
            
            # Get and execute best move
            move = self.get_autonomous_move()
            if self.move_robot(move):
                self.move_bolor()
                moves_count += 1
        
        self.display()
        if self.won:
            print("\nRobot wins!")
        else:
            print("\nGame Over! Mold wins!")
        print(f"Total moves: {moves_count}")

    def check_game_state(self):
        # Verificar se o robot chegou à manteiga
        if self.robot_pos['row'] == self.manteiga_pos['row'] and \
           self.robot_pos['col'] == self.manteiga_pos['col']:
            self.game_over = True
            self.won = True
            return

        # Verificar se o bolor chegou à manteiga ou ao robot
        if (self.bolor_pos['row'] == self.manteiga_pos['row'] and \
            self.bolor_pos['col'] == self.manteiga_pos['col']) or \
           (self.bolor_pos['row'] == self.robot_pos['row'] and \
            self.bolor_pos['col'] == self.robot_pos['col']):
            self.game_over = True
            self.won = False

        if self.bolor_pos['row'] == self.torradeira_pos['row'] and \
           self.bolor_pos['col'] == self.torradeira_pos['col']:
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
                    pos_char = 'R'
                elif i == self.bolor_pos['row'] and j == self.bolor_pos['col']:
                    pos_char = 'B'
                elif i == self.manteiga_pos['row'] and j == self.manteiga_pos['col']:
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
    else:
        print("\nGame Over! O bolor venceu!")

if __name__ == "__main__":
    game = GameBoard()
    # mode = input("Choose mode (1 for manual, 2 for autonomous): ")
    # if mode == "1":
    #     play_game()
    # else:
        #game.play_game_autonomous()
    game.play_game_autonomous()