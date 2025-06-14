"""
planner.py
Plans a sequence of actions that moves an simulated robot around a Vacuum World grid and vacuums all dirty cells.

Usage:
    python3 planner.py [algorithm] [world-file]

Example:
    python3 planner.py uniform-cost tiny-1.txt

Parameters:
- [algorithm] (uniform-cost|depth-first): Selects the desired algorithm for the search.
- [world-file]: location of the file that contains a Vacuum World grid (generated by make_vacuum_world.py)


Outputs to stdout:
1. One action per line (N, S, E, W, V)
2. Number of nodes generated
3. Number of nodes expanded
"""

import sys
from typing import List
from heapq import heappush, heappop

# Represents a possible state of a robot. 
class RobotState:
    def __init__(self, position: tuple, dirty_cells: set, path: list):
        self.position = position
        self.dirty_cells = frozenset(dirty_cells)
        self.path = path

    def __lt__(self, other):
        return len(self.dirty_cells) < len(other.dirty_cells)

# Reads in a world file
def read_input(file_path):
    with open(file_path, "r") as f:
        lines = f.read().splitlines()

    cols = int(lines[0])
    rows = int(lines[1])
    world_lines = lines[2:]

    grid = []
    robot_pos = None
    dirty_cells = set()

    for rind in range(rows):
        row = list(world_lines[rind])
        for cind, cell in enumerate(row):
            # If it is the starting cell mark it down and replace with empty cell
            if cell == "@":
                robot_pos = (rind, cind)
                row[cind] = "_"
            elif cell == "*":
                dirty_cells.add((rind, cind))
        grid.append(row)

    return cols, rows, grid, robot_pos, dirty_cells


def ucs(cols: int, rows: int, world: List[List[str]], start: RobotState):
    # Initialize pq using a heap to store generated nodes, add starting node
    pq = []
    heappush(pq, (0, start))
    explored = set()
    exp = 0
    gen = 0
    directions = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}

    # Search loop
    while pq:
        # Expand a node, pop it off the pq
        exp += 1
        cur = heappop(pq)[1]
        r, c = cur.position

        # Check if we need to vacuum current square
        if cur.position in cur.dirty_cells:
            new_dirty = set(cur.dirty_cells)
            new_dirty.remove(cur.position)
            cur = RobotState(cur.position, new_dirty, cur.path + ["V"])

        # If there are no more remaining dirty squares we can return our path
        if not cur.dirty_cells:
            for i in cur.path:
                print(i)
            print(gen, " nodes generated")
            print(exp, " nodes expanded")
            return

        # Loop to generate new nodes
        for action, (dr, dc) in directions.items():
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and world[nr][nc] != "#":
                new_state = RobotState((nr, nc), cur.dirty_cells, cur.path + [action])
                if (new_state.position, new_state.dirty_cells) not in explored:
                    heappush(pq, (len(new_state.path), new_state))
                    explored.add((new_state.position, new_state.dirty_cells))
                    gen += 1

    # If all possible nodes are expanded and we haven't cleaned every thing
    print("Could not reach all dirty squares")
    print(gen, " nodes generated")
    print(exp, " nodes expanded")
    sys.exit(1)


def dfs(cols: int, rows: int, world: List[List[str]], start: RobotState):
    # Initialize stack array to store generated nodes, add starting node
    stack = [start]
    explored = set()
    exp = 0
    gen = 0
    directions = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}

    # Search loop
    while stack:
        # Expand first node in the stack
        exp += 1
        cur = stack.pop()
        r, c = cur.position

        # If the node is dirty we clean it
        if cur.position in cur.dirty_cells:
            new_dirty = set(cur.dirty_cells)
            new_dirty.remove(cur.position)
            cur = RobotState(cur.position, new_dirty, cur.path + ["V"])

        # If all cells are clean then we can return our successful path
        if not cur.dirty_cells:
            for i in cur.path:
                print(i)
            print(gen, " nodes generated")
            print(exp, " nodes expanded")
            return

        # Generates and adds unexplored nodes to the stack
        for action, (dr, dc) in directions.items():
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and world[nr][nc] != "#":
                new_state = RobotState(
                    (nr, nc), cur.dirty_cells, cur.path + [action]
                )
                if (new_state.position, new_state.dirty_cells) not in explored:
                    stack.append(new_state)
                    explored.add((new_state.position, new_state.dirty_cells))
                    gen += 1

    # If all possible nodes are expanded and we haven't cleaned every thing
    print("Could not reach all dirty squares")
    print(gen, " nodes generated")
    print(exp, " nodes expanded")
    sys.exit(1)


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 planner.py [algorithm] [world-file]")
        sys.exit(1)

    # Uses the [world-file] to generate a world
    inpt = read_input(sys.argv[2]) 
    col = inpt[0]
    row = inpt[1]
    world = inpt[2]
    start = RobotState(inpt[3], inpt[4], [])
    
    # Run the desired algorithm 
    if sys.argv[1] == "uniform-cost":
        ucs(col, row, world, start)
    elif sys.argv[1] == "depth-first":
        dfs(col, row, world, start)
    else:
        print("Please enter a valid algorithm")
        sys.exit(1)


if __name__ == "__main__":
    main()
