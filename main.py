import itertools
import random

class Minesweeper():
    # Minesweeper game representation 
    def __init__(self, height=8, width=8, mines=8):
        self.height = height
        self.width = width
        self.mines = set()
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True
        self.mines_found = set()

    def print(self):
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]: print("|X", end="")
                else: print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        count = 0
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) == cell: continue
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]: count += 1
        return count

    def won(self):
        return self.mines_found == self.mines

class Sentence():
    # Logical statement about a Minesweeper game 
    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        if len(self.cells) == self.count and self.count > 0:
            return self.cells
        return set()

    def known_safes(self):
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)

class MinesweeperAI():
    # Minesweeper game player #
    def __init__(self, height=8, width=8):
        self.height = height
        self.width = width
        self.moves_made = set()
        self.mines = set()
        self.safes = set()
        self.knowledge = []

    def mark_mine(self, cell):
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # Build sentence for neighbors
        neighbors = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) == cell or not (0 <= i < self.height and 0 <= j < self.width):
                    continue
                if (i, j) in self.safes: continue
                if (i, j) in self.mines: count -= 1
                else: neighbors.add((i, j))
        
        self.knowledge.append(Sentence(neighbors, count))

        # Infer knowledge
        changed = True
        while changed:
            changed = False
            self.knowledge = [s for s in self.knowledge if len(s.cells) > 0]
            
            for sentence in self.knowledge:
                mines = sentence.known_mines()
                safes = sentence.known_safes()
                for mine in mines.copy():
                    if mine not in self.mines:
                        self.mark_mine(mine); changed = True
                for safe in safes.copy():
                    if safe not in self.safes:
                        self.mark_safe(safe); changed = True
            
            # Subset inference
            for s1, s2 in itertools.combinations(self.knowledge, 2):
                if s1.cells.issubset(s2.cells):
                    new_sentence = Sentence(s2.cells - s1.cells, s2.count - s1.count)
                    if new_sentence not in self.knowledge:
                        self.knowledge.append(new_sentence); changed = True

    def make_safe_move(self):
        for cell in self.safes:
            if cell not in self.moves_made: return cell
        return None

    def make_random_move(self):
        possible = []
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    possible.append((i, j))
        return random.choice(possible) if possible else None
