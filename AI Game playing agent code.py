import queue
import random
import copy
from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod

numberOfFixedMoves1 = 2
numberOfFixedMoves2 = 2

# ==================== GAME UTILITIES ====================
# Essential utility functions for game state analysis

def copyBoard(board):
    return [row[:] for row in board]

def countPiecesBlocked(board, player, rows, cols, score_cols):
    count = 0
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    
    for y in range(rows):
        for x in range(cols):
            piece = board[y][x]
            if piece and piece.owner == player and piece.side == "stone":
                blocked = 0
                for dx, dy in dirs:
                    nx, ny = x + dx, y + dy
                    if (in_bounds(nx, ny, rows, cols) and 
                        board[ny][nx] and 
                        board[ny][nx].owner != player):
                        blocked += 1
                if blocked >= 2:
                    count += 1
    return count

def dis(x,y,m,n):
    return abs(x-m) + abs(y-n)

def manhattan(board,rows,cols):
    scoringCols = score_cols_for(cols)
    rowCircle = top_score_row()
    rowSquare = bottom_score_row(rows)

    distance1 =0 # for circle
    distance2 = 0

    for x in range(rows):
        for y in range(cols):
            cell = board[x][y]
            if cell:
                if cell.owner == 'circle':
                    temp = 999999999
                    for c in scoringCols:
                        temp = min(temp, dis(x, y, rowCircle, c))
                    if temp != 999999999:
                        distance1 += temp
                else:
                    temp = 999999999
                    for c in scoringCols:
                        temp = min(temp, dis(x, y, rowSquare, c))
                    if temp != 999999999:
                        distance2 += temp

    return distance1, distance2

def getOneStep(board, r:int, scoreCols, player:str):
    count =0
    for c in scoreCols:
        cell = board[r-1][c]
        if cell and cell.owner == player:
            count = count+1
        cell = board[r+1][c]
        if cell and cell.owner == player:
            count = count+1

    cell = board[r][3]
    if cell and cell.owner == player:
        count = count+1

    cell = board[r][8]
    if cell and cell.owner == player:
        count = count + 1
    
    return count

def in_bounds(x: int, y: int, rows: int, cols: int) -> bool:
    """Check if coordinates are within board boundaries."""
    return 0 <= x < cols and 0 <= y < rows


def score_cols_for(cols: int) -> List[int]:
    """Get the column indices for scoring areas."""
    w = 4
    start = max(0, (cols - w) // 2)
    return list(range(start, start + w))


def top_score_row() -> int:
    """Get the row index for Circle's scoring area."""
    return 2


def bottom_score_row(rows: int) -> int:
    """Get the row index for Square's scoring area."""
    return rows - 3


def is_opponent_score_cell(x: int, y: int, player: str, rows: int, cols: int, score_cols: List[int]) -> bool:
    """Check if a cell is in the opponent's scoring area."""
    if player == "circle":
        return (y == bottom_score_row(rows)) and (x in score_cols)
    else:
        return (y == top_score_row()) and (x in score_cols)


def is_own_score_cell(x: int, y: int, player: str, rows: int, cols: int, score_cols: List[int]) -> bool:
    """Check if a cell is in the player's own scoring area."""
    if player == "circle":
        return (y == top_score_row()) and (x in score_cols)
    else:
        return (y == bottom_score_row(rows)) and (x in score_cols)


def get_opponent(player: str) -> str:
    """Get the opponent player identifier."""
    return "square" if player == "circle" else "circle"

# ==================== MOVE GENERATION HELPERS ====================

def agent_river_flow(board, rx:int, ry:int, sx:int, sy:int, player:str, rows:int, cols:int, score_cols:List[int], river_push:bool=False) -> List[Dict[str, Any]]:
    """
        for river flow for both river and stone
        board: Current board state
        rx, ry: River entry point
        sx, sy: Source position (where piece is moving from)
        player: Current player
        rows, cols: Board dimensions
        score_cols: Scoring column indices
        river_push: Whether this is for a river push move
    """
    destinations = []
    visited = set()
    queue = [(rx, ry)]

    while queue:
        x, y = queue.pop(0)
        if (x,y) in visited or not in_bounds(x, y, rows, cols):
            continue
        visited.add((x,y))

        cell = board[y][x]

        if river_push and x==rx and y==ry: # when we push stone through a river
            cell = board[sy][sx]

        if cell is None:
            if is_opponent_score_cell(x, y, player, rows, cols, score_cols):
                pass
            else:
                destinations.append((x, y))
            continue
            
        if cell.side != "river":
            continue

        dir = [(1, 0), (-1, 0)] if cell.orientation == "horizontal" else [(0, 1), (0, -1)]

        for dx, dy, in dir:
            nx,ny = x+dx, y+dy
            while in_bounds(nx, ny, rows, cols):
                if is_opponent_score_cell(nx, ny, player, rows, cols, score_cols):
                    break

                nextCell = board[ny][nx]
                if nextCell is None:
                    destinations.append((nx, ny))
                    nx+=dx
                    ny+=dy
                    continue

                if nx==sx and ny==sy:
                    nx+=dx
                    ny+=dy
                    continue

                if nextCell.side == "river":
                    queue.append((nx, ny))
                    break
                break

    uDes = []
    seen = set()
    for d in destinations:
        seen.add(d)
    for d in seen:
        uDes.append(d)   
        
    return uDes

def get_valid_moves_for_piece(board, x: int, y: int, player: str, rows: int, cols: int, score_cols: List[int]) -> List[Dict[str, Any]]:
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    moves = set()
    pushes = []

    if not in_bounds(x, y, rows, cols):
        return []

    p = board[y][x]
    if p is None or p.owner != player:
        return []

    for dx, dy in dirs:
        tx, ty = x + dx, y + dy
        if not in_bounds(tx, ty, rows, cols):
            continue
        if is_opponent_score_cell(tx, ty, player, rows, cols, score_cols):
            continue

        target = board[ty][tx]

        if target is None:
            moves.add((tx, ty))
        elif target.side == "river":  # river
            flow = agent_river_flow(board, tx, ty, x, y, player, rows, cols, score_cols)
            for dest in flow:
                moves.add(dest)
        elif target.side == "stone":  # stone
            if p.side == "stone":
                px, py = tx + dx, ty + dy
                pushed_player = target.owner
                if (in_bounds(px, py, rows, cols) and
                        board[py][px] is None and
                        not is_opponent_score_cell(px, py, pushed_player, rows, cols, score_cols)):
                    pushes.append(((tx, ty), (px, py)))
            else:
                pushed_player = target.owner
                flow = agent_river_flow(board, tx, ty, x, y, pushed_player, rows, cols, score_cols, True)
                for dest in flow:
                    if not is_opponent_score_cell(dest[0],dest[1], pushed_player, rows, cols, score_cols):
                        pushes.append(((tx, ty), dest))
    out = []
    for m in moves:
        out.append({'type': 'move', 'from': [x, y], 'to': m})
    for push in pushes:
        out.append({'type': 'push', 'from': [x, y], 'to': p[0], 'pushed_to': p[1]})
    if p.side == "stone":
        out.append({"action": "flip", "from": [x, y], "orientation": "horizontal"})
        out.append({"action": "flip", "from": [x, y], "orientation": "vertical"})
    else:
        out.append({"action": "flip", "from": [x, y], "orientation": None})
        new_orient = "vertical" if p.orientation == "horizontal" else "horizontal"
        out.append({"action": "rotate", "from": [x, y], "orientation": new_orient})
    return out

def generate_all_moves(board: List[List[Any]], player: str, rows: int, cols: int, score_cols: List[int]) -> List[
    Dict[str, Any]]:
    """
    Generate all legal moves for the current player.

    Args:
        board: Current board state
        player: Current player ("circle" or "square")
        rows, cols: Board dimensions
        score_cols: Scoring column indices

    Returns:
        List of all valid move dictionaries
    """
    moves = []
    for y in range(rows):
        for x in range(cols):
            p = board[y][x]
            if not p or p.owner != player:
                continue

            valid_moves = get_valid_moves_for_piece(board, x, y, player, rows, cols, score_cols)
            moves.extend(valid_moves)

    return moves

# ==================== BOARD EVALUATION ====================

def count_stones_in_scoring_area(board: List[List[Any]], player: str, rows: int, cols: int, score_cols: List[int]) -> int:
    """Count how many stones a player has in their scoring area."""
    count = 0
    
    if player == "circle":
        score_row = top_score_row()
    else:
        score_row = bottom_score_row(rows)
    
    for x in score_cols:
        if in_bounds(x, score_row, rows, cols):
            piece = board[score_row][x]
            if piece and piece.owner == player and piece.side == "stone":
                count += 1
    
    return count
    
def count_rivers_in_scoring_area(board: List[List[Any]], player: str, rows: int, cols: int, score_cols: List[int]) -> int:
    """Count how many stones a player has in their scoring area."""
    count = 0
    
    if player == "circle":
        score_row = top_score_row()
    else:
        score_row = bottom_score_row(rows)
    
    for x in score_cols:
        if in_bounds(x, score_row, rows, cols):
            piece = board[score_row][x]
            if piece and piece.owner == player and piece.side == "river":
                count += 1
    
    return count


def simulate_move(board: List[List[Any]], move: Dict[str, Any], player: str, rows: int, cols: int,
                  score_cols: List[int]) -> Tuple[bool, Any]:
    """
    Simulate a move on a copy of the board.

    Args:
        board: Current board state
        move: Move to simulate
        player: Player making the move
        rows, cols: Board dimensions
        score_cols: Scoring column indices

    Returns:
        (success: bool, new_board_state or error_message)
    """
    # Import the game engine's move validation function
    try:
        from gameEngine import validate_and_apply_move
        board_copy = copy.deepcopy(board)
        success, message = validate_and_apply_move(board_copy, move, player, rows, cols, score_cols)
        return success, board_copy if success else message
    except ImportError:
        # Fallback to basic simulation if game engine not available
        return True, copy.deepcopy(board)

# ==================== BASE AGENT CLASS ====================

class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    """
    
    def __init__(self, player: str):
        """Initialize agent with player identifier."""
        self.player = player
        self.opponent = get_opponent(player)
    
    @abstractmethod
    def choose(self, board: List[List[Any]], rows: int, cols: int, score_cols: List[int], current_player_time: float, opponent_time: float) -> Optional[Dict[str, Any]]:
        """
        Choose the best move for the current board state.
        
        Args:
            board: 2D list representing the game board
            rows, cols: Board dimensions
            score_cols: List of column indices for scoring areas
        
        Returns:
            Dictionary representing the chosen move, or None if no moves available
        """
        pass

# ==================== STUDENT AGENT IMPLEMENTATION ====================

class StudentAgent(BaseAgent):
    """
    Student Agent Implementation
    
    TODO: Implement your AI agent for the River and Stones game.
    The goal is to get 4 of your stones into the opponent's scoring area.
    
    You have access to these utility functions:
    - generate_all_moves(): Get all legal moves for current player
    - basic_evaluate_board(): Basic position evaluation 
    - simulate_move(): Test moves on board copy
    - count_stones_in_scoring_area(): Count stones in scoring positions
    """
    
    def __init__(self, player: str):
        self.depth = 2
        super().__init__(player)
    

    def generate_best_moves(self, player:str, board:List[List[Any]], rows:int, cols:int, score_cols:List[int]) -> List[Dict[str,Any]]:
        moves=[]
        priorityMoves = []
        dirs=[(1,0),(-1,0),(0,1),(0,-1)]
    
        # all 4 pieces in there
        scoringStonesPlayer = count_stones_in_scoring_area(board, player, rows, cols, score_cols)
        scoringRiversPlayer = count_rivers_in_scoring_area(board, player, rows, cols, score_cols)

        if scoringStonesPlayer + scoringRiversPlayer == 4:
            scoringCols = score_cols_for(cols)
            if player == 'circle':
                scoringRow = top_score_row()
            else:
                scoringRow = bottom_score_row(rows)

            for c in scoringCols:
                p = board[scoringRow][c]
                if p is not None and p.side == 'river':
                    moves.append({"action":"flip","from":[c, scoringRow]})
            if moves:
                return moves ,1


        for y in range(rows):
            for x in range(cols):
                p = board[y][x]
                if not p or p.owner != player: continue
                if p.side == "river":
                    for dx,dy in dirs:
                        nx,ny = x+dx,y+dy
                        if not in_bounds(nx,ny,rows,cols): continue
                        if is_opponent_score_cell(nx,ny,player,rows,cols,score_cols): continue
                        if board[ny][nx]:
                            target = board[ny][nx]
                            if target.side == "river":
                                flow = agent_river_flow(board, nx, ny, x, y, player, rows, cols, score_cols, 1)
                                for d in flow:
                                    if is_own_score_cell(d[0], d[1], player, rows, cols, score_cols):
                                        priorityMoves.append({"action":"move","from":[x,y],"to":d})
                else:
                    for dx,dy in dirs:
                        nx,ny = x+dx,y+dy
                        if not in_bounds(nx,ny,rows,cols): continue
                        if is_opponent_score_cell(nx,ny,player,rows,cols,score_cols): continue
                        if board[ny][nx]:
                            target = board[ny][nx]
                            if target.side == "river":
                                # moves that flow through the river
                                flow = agent_river_flow(board, nx, ny, x, y,player, rows, cols, score_cols)
                                for d in flow:
                                    if is_own_score_cell(d[0], d[1], player, rows, cols, score_cols):
                                        priorityMoves.append({"action":"move","from":[x,y],"to":d})

        if priorityMoves:
            return priorityMoves, 1
        # if my player is able to go to scoring area in one step and when it is his turn
        
        direct = False
        fixedCol = score_cols_for(cols)
        if player == 'circle':
            fixedRow = top_score_row()
        else:
            fixedRow = bottom_score_row(rows)

        for c in fixedCol:
            cell=board[fixedRow-1][c]
            tar = board[fixedRow][c]
            if cell and cell.owner == self.player and tar is None:
                direct = True
                moves.append({"action":"move","from":[c,fixedRow-1],"to":[c, fixedRow]})

            cell=board[fixedRow+1][c]
            tar = board[fixedRow][c]
            if cell and cell.owner == self.player and tar is None:
                direct = True
                moves.append({"action":"move","from":[c,fixedRow+1],"to":[c, fixedRow]})

        cell = board[fixedRow][fixedCol[0]-1]
        tar = board[fixedRow][fixedCol[0]]
        if cell and cell.owner == self.player and tar is None:
            direct = True
            moves.append({"action":"move","from":[fixedCol[0]-1,fixedRow],"to":[fixedCol[0], fixedRow]})
        elif cell and cell.owner==self.player and tar.side == 'stone':
            nextTar = board[fixedRow][fixedCol[1]]
            if nextTar is None:
                direct = True
                moves.append({"action":"push","from":[fixedCol[0]-1, fixedRow],"to":[fixedCol[0],fixedRow],"pushed_to":[fixedCol[1],fixedRow]})
            
        cell = board[fixedRow][fixedCol[3]+1]
        tar = board[fixedRow][fixedCol[3]]
        if cell and cell.owner == self.player and tar is None:
            direct = True
            moves.append({"action":"move","from":[fixedCol[3]+1,fixedRow],"to":[fixedCol[3], fixedRow]})
        elif cell and cell.owner==self.player and tar.side =='stone':
            nextTar = board[fixedRow][fixedCol[2]]
            if nextTar is None:
                direct = True
                moves.append({"action":"push","from":[fixedCol[3]+1, fixedRow],"to":[fixedCol[3],fixedRow],"pushed_to":[fixedCol[2],fixedRow]})


        if direct:
            return moves, 1

        for y in range(rows):
            for x in range(cols):
                p = board[y][x]

                if not p or p.owner != player: continue
                
                # for defense
                if player == self.player:
                    fixedCol = score_cols_for(cols)
                    if player == 'circle':
                        fixedRow = bottom_score_row(rows) - 1
                        if y == fixedRow and x in fixedCol:
                            continue

                        if y == fixedRow+1 and x == 3:
                            continue
                        if y == fixedRow+1 and x == 8:
                            continue
                        
                    else:
                        fixedRow = top_score_row() + 1
                        if y == fixedRow and x in fixedCol:
                            continue

                        if y == fixedRow-1 and x == 3:
                            continue
                        if y == fixedRow-1 and x == 8:
                            continue

                if is_own_score_cell(x, y, player, rows, cols, score_cols):
                    if p.side == 'river':
                        moves.append({"action":"flip","from":[x,y]})
                    else:
                        if is_own_score_cell(x+1, y, player, rows, cols, score_cols):
                            cell = board[y][x+1]
                            if cell is None:
                                moves.append({"action":"move","from":[x,y],"to":[x+1, y]})

                        if is_own_score_cell(x-1, y, player, rows, cols, score_cols):
                            cell = board[y][x-1]
                            if cell is None:
                                moves.append({"action":"move","from":[x,y],"to":[x-1, y]})
                    continue

                if p.side == "river":
                    for dx,dy in dirs:
                        nx,ny = x+dx,y+dy
                        if not in_bounds(nx,ny,rows,cols): continue
                        if is_opponent_score_cell(nx,ny,player,rows,cols,score_cols): continue
                        if board[ny][nx] is None:
                            moves.append({"action":"move","from":[x,y],"to":[nx,ny]})
                        else:
                            target = board[ny][nx]
                            if target.side == "river":
                                flow = agent_river_flow(board, nx, ny, x, y, player, rows, cols, score_cols, 1)
                                for d in flow:
                                    if is_own_score_cell(d[0], d[1], player, rows, cols, score_cols):
                                        priorityMoves.append({"action":"move","from":[x,y],"to":d})
                                    moves.append({"action":"move","from":[x,y],"to":d})
                            else:
                                px,py = nx+dx, ny+dy
                                if in_bounds(px,py,rows,cols) and board[py][px] is None and not is_opponent_score_cell(px,py,target.owner,rows,cols,score_cols):
                                    moves.append({"action":"push","from":[x,y],"to":[nx,ny],"pushed_to":[px,py]})
                    
                    moves.append({"action":"flip","from":[x,y]})
                    new_ori = "vertical" if p.orientation=="horizontal" else "horizontal"
                    moves.append({"action":"rotate","from":[x,y], "orientation":new_ori})

                else:
                    for dx,dy in dirs:
                        nx,ny = x+dx,y+dy
                        if not in_bounds(nx,ny,rows,cols): continue
                        if is_opponent_score_cell(nx,ny,player,rows,cols,score_cols): continue
                        if board[ny][nx] is None:
                            moves.append({"action":"move","from":[x,y],"to":[nx,ny]})
                        else:
                            target = board[ny][nx]
                            if target.side == "river":
                                flow = agent_river_flow(board, nx, ny, x, y,player, rows, cols, score_cols)
                                for d in flow:
                                    if is_own_score_cell(d[0], d[1], player, rows, cols, score_cols):
                                        priorityMoves.append({"action":"move","from":[x,y],"to":d})
                                    moves.append({"action":"move","from":[x,y],"to":d})
                            else:
                                px,py = nx+dx, ny+dy
                                if in_bounds(px,py,rows,cols) and board[py][px] is None and not is_opponent_score_cell(px,py,target.owner,rows,cols,score_cols):
                                    moves.append({"action":"push","from":[x,y],"to":[nx,ny],"pushed_to":[px,py]})
                    
                    for ori in ("horizontal","vertical"):
                        moves.append({"action":"flip","from":[x,y],"orientation":ori})
        
        if priorityMoves:
            return priorityMoves,1
        return moves, 0

    def evaluateBoard(self, board, rows, cols, score_cols):
        player = self.player
        opponent = get_opponent(player)
        score = 0.0
        if rows==13:
            circlePositionalAdvantage = [[-80, -80,  30,  50,  80,  80,  80,  80,  50,  30, -80, -80], 
                                        [ -60, -60,  80, 120, 180, 200, 200, 180, 120,  80, -60, -60],
                                        [ -40, -40, 150, 200, 600, 800, 800, 600, 200, 150, -40, -40],
                                        [ -20, -20, 120, 180, 400, 500, 500, 400, 180, 120, -20, -20],
                                        [   0,   0, 100, 150, 300, 400, 400, 300, 150, 100,   0,   0],
                                        [  10,  10,  80, 120, 250, 350, 350, 250, 120,  80,  10,  10],
                                        [  20,  20,  60, 100, 200, 300, 300, 200, 100,  60,  20,  20],
                                        [  30,  30,  50,  80, 150, 250, 250, 150,  80,  50,  30,  30],
                                        [  40,  40,  40,  60, 100, 200, 200, 100,  60,  40,  40,  40],
                                        [  50,  50,  60,  80, 150, 300, 300, 150,  80,  60,  50,  50],
                                        [  60,  60, 120, 180, 500, 900, 900, 500, 180, 120,  60,  60],
                                        [  40,  40,  80, 120, 300, 600, 600, 300, 120,  80,  40,  40],
                                        [  20,  20,  40,  60, 150, 300, 300, 150,  60,  40,  20,  20]]

            riverPositionalAdvantage = [[ -50, -50, 100, 120, 150, 150, 150, 150, 120, 100, -50, -50],
                                        [ -50, -50, 150, 180, 250, 250, 250, 250, 180, 150, -50, -50],
                                        [ -50, -50, 200, 250, 700, 800, 800, 700, 250, 200, -50, -50],
                                        [ -50, -50, 150, 200, 300, 350, 350, 300, 200, 150, -50, -50],
                                        [ -50, -50, 120, 150, 250, 300, 300, 250, 150, 120, -50, -50],
                                        [ -50, -50, 100, 120, 200, 250, 250, 200, 120, 100, -50, -50],
                                        [ -50, -50,  80, 100, 150, 200, 200, 150, 100,  80, -50, -50],
                                        [ -50, -50,  60,  80, 120, 150, 150, 120,  80,  60, -50, -50],
                                        [ -50, -50,  50,  70, 100, 120, 120, 100,  70,  50, -50, -50],
                                        [ -50, -50,  40,  60,  80, 100, 100,  80,  60,  40, -50, -50],
                                        [ -50, -50, 200, 250, 700, 800, 800, 700, 250, 200, -50, -50],
                                        [ -50, -50,  20,  40,  80, 100, 100,  80,  40,  20, -50, -50],
                                        [ -50, -50,  10,  20,  50,  60,  60,  50,  20,  10, -50, -50]]
        elif rows == 15:
            circlePositionalAdvantage = [[ -80, -80, -80,  30,  50,  80,  80,  80,  80,  50,  30, -80, -80, -80], 
                                        [ -60, -60,  -60,  80, 120, 180, 200, 200, 180, 120,  80, -60, -60, -60],
                                        [ -40, -40,  -40, 150, 200, 600, 800, 800, 600, 200, 150, -40, -40, -40],
                                        [ -20, -20,  -20, 120, 180, 400, 500, 500, 400, 180, 120, -20, -20, -20],
                                        [   0,   0,    0, 100, 150, 300, 400, 400, 300, 150, 100,   0,   0,   0],
                                        [  10,  10,   10,  80, 120, 250, 350, 350, 250, 120,  80,  10,  10,  10],
                                        [  20,  20,   20,  60, 100, 200, 300, 300, 200, 100,  60,  20,  20,  20],
                                        [  30,  30,   30,  50,  80, 150, 250, 250, 150,  80,  50,  30,  30,  30],
                                        [  30,  30,   30,  50,  80, 150, 250, 250, 150,  80,  50,  30,  30,  30],
                                        [  40,  40,   40,  40,  60, 100, 200, 200, 100,  60,  40,  40,  40,  40],
                                        [  30,  30,   30,  50,  80, 150, 250, 250, 150,  80,  50,  30,  30,  30],
                                        [  50,  50,   50,  60,  80, 150, 300, 300, 150,  80,  60,  50,  50,  50],
                                        [  60,  60,   60, 120, 180, 500, 900, 900, 500, 180, 120,  60,  60,  60],
                                        [  40,  40,   40,  80, 120, 300, 600, 600, 300, 120,  80,  40,  40,  40],
                                        [  20,  20,   20,  40,  60, 150, 300, 300, 150,  60,  40,  20,  20,  20]]

            riverPositionalAdvantage = [[ -50, -50, -50, 100, 120, 150, 150, 150, 150, 120, 100, -50, -50, -50],
                                        [ -50, -50, -50, 150, 180, 250, 250, 250, 250, 180, 150, -50, -50, -50],
                                        [ -50, -50, -50, 200, 250, 700, 800, 800, 700, 250, 200, -50, -50, -50],
                                        [ -50, -50, -50, 150, 200, 300, 350, 350, 300, 200, 150, -50, -50, -50],
                                        [ -50, -50, -50, 120, 150, 250, 300, 300, 250, 150, 120, -50, -50, -50],
                                        [ -50, -50, -50, 100, 120, 200, 250, 250, 200, 120, 100, -50, -50, -50],
                                        [ -50, -50, -50,  80, 100, 150, 200, 200, 150, 100,  80, -50, -50, -50],
                                        [ -50, -50, -50,  60,  80, 120, 150, 150, 120,  80,  60, -50, -50, -50],
                                        [ -50, -50, -50,  60,  80, 120, 150, 150, 120,  80,  60, -50, -50, -50],
                                        [ -50, -50, -50,  50,  70, 100, 120, 120, 100,  70,  50, -50, -50, -50],
                                        [ -50, -50, -50,  60,  80, 120, 150, 150, 120,  80,  60, -50, -50, -50],
                                        [ -50, -50, -50,  40,  60,  80, 100, 100,  80,  60,  40, -50, -50, -50],
                                        [ -50, -50, -50, 200, 250, 700, 800, 800, 700, 250, 200, -50, -50, -50],
                                        [ -50, -50, -50,  20,  40,  80, 100, 100,  80,  40,  20, -50, -50, -50],
                                        [ -50, -50, -50,  10,  20,  50,  60,  60,  50,  20,  10, -50, -50, -50]]
        else:
            circlePositionalAdvantage = [[-80, -80, -80, -80,  30,  50,  80,  80,  80,  80,  50,  30, -80, -80, -80, -80], 
                                        [ -60, -60, -60, -60,  80, 120, 180, 200, 200, 180, 120,  80, -60, -60, -60, -60],
                                        [ -40, -40, -40, -40, 150, 200, 600, 800, 800, 600, 200, 150, -40, -40, -40, -40],
                                        [ -20, -20, -20, -20, 120, 180, 400, 500, 500, 400, 180, 120, -20, -20, -20, -20],
                                        [   0,   0,   0,   0, 100, 150, 300, 400, 400, 300, 150, 100,   0,   0,   0,   0],
                                        [  10,  10,  10,  10,  80, 120, 250, 350, 350, 250, 120,  80,  10,  10,  10,  10],
                                        [  20,  20,  20,  20,  60, 100, 200, 300, 300, 200, 100,  60,  20,  20,  20,  20],
                                        [  30,  30,  30,  30,  50,  80, 150, 250, 250, 150,  80,  50,  30,  30,  30,  30],
                                        [  40,  40,  40,  40,  40,  60, 100, 200, 200, 100,  60,  40,  40,  40,  40,  40],
                                        [  40,  40,  40,  40,  40,  60, 100, 200, 200, 100,  60,  40,  40,  40,  40,  40],
                                        [  40,  40,  40,  40,  40,  60, 100, 200, 200, 100,  60,  40,  40,  40,  40,  40],
                                        [  50,  50,  50,  50,  60,  80, 150, 300, 300, 150,  80,  60,  50,  50,  50,  50],
                                        [  40,  40,  40,  40,  40,  60, 100, 200, 200, 100,  60,  40,  40,  40,  40,  40],
                                        [  40,  40,  40,  40,  40,  60, 100, 200, 200, 100,  60,  40,  40,  40,  40,  40],
                                        [  60,  60,  60,  60, 120, 180, 500, 900, 900, 500, 180, 120,  60,  60,  60,  60],
                                        [  40,  40,  40,  40,  80, 120, 300, 600, 600, 300, 120,  80,  40,  40,  40,  40],
                                        [  20,  20,  20,  20,  40,  60, 150, 300, 300, 150,  60,  40,  20,  20,  20,  20]]

            riverPositionalAdvantage = [[ -50, -50, -50, -50, 100, 120, 150, 150, 150, 150, 120, 100, -50, -50, -50, -50],
                                        [ -50, -50, -50, -50, 150, 180, 250, 250, 250, 250, 180, 150, -50, -50, -50, -50],
                                        [ -50, -50, -50, -50, 200, 250, 700, 800, 800, 700, 250, 200, -50, -50, -50, -50],
                                        [ -50, -50, -50, -50, 150, 200, 300, 350, 350, 300, 200, 150, -50, -50, -50, -50],
                                        [ -50, -50, -50, -50, 120, 150, 250, 300, 300, 250, 150, 120, -50, -50, -50, -50],
                                        [ -50, -50, -50, -50, 100, 120, 200, 250, 250, 200, 120, 100, -50, -50, -50, -50],
                                        [ -50, -50, -50, -50,  80, 100, 150, 200, 200, 150, 100,  80, -50, -50, -50, -50],
                                        [ -50, -50, -50, -50,  60,  80, 120, 150, 150, 120,  80,  60, -50, -50, -50, -50],
                                        [ -50, -50, -50, -50,  60,  80, 120, 150, 150, 120,  80,  60, -50, -50, -50, -50],
                                        [ -50, -50, -50, -50,  50,  70, 100, 120, 120, 100,  70,  50, -50, -50, -50, -50],
                                        [ -50, -50, -50, -50,  50,  70, 100, 120, 120, 100,  70,  50, -50, -50, -50, -50],
                                        [ -50, -50, -50, -50,  60,  80, 120, 150, 150, 120,  80,  60, -50, -50, -50, -50],
                                        [ -50, -50, -50, -50,  50,  70, 100, 120, 120, 100,  70,  50, -50, -50, -50, -50],
                                        [ -50, -50, -50, -50,  40,  60,  80, 100, 100,  80,  60,  40, -50, -50, -50, -50],
                                        [ -50, -50, -50, -50, 200, 250, 700, 800, 800, 700, 250, 200, -50, -50, -50, -50],
                                        [ -50, -50, -50, -50,  20,  40,  80, 100, 100,  80,  40,  20, -50, -50, -50, -50],
                                        [ -50, -50, -50, -50,  10,  20,  50,  60,  60,  50,  20,  10, -50, -50, -50, -50]]
        

        square_table = list(reversed(circlePositionalAdvantage))

        #Stones in scoring areas
        scoringStonesPlayer = count_stones_in_scoring_area(board, player, rows, cols, score_cols)
        scoringRiversPlayer = count_rivers_in_scoring_area(board, player, rows, cols, score_cols)

        scoringStonesOpponent = count_stones_in_scoring_area(board, opponent, rows, cols, score_cols)
        scoringRiversOpponent = count_rivers_in_scoring_area(board, opponent, rows, cols, score_cols)

        if scoringStonesPlayer == 4:
            return float('inf')
        elif scoringStonesOpponent == 4:
            return float('-inf')

        score += scoringStonesPlayer*1500
        score -= scoringStonesOpponent*1400
        score += scoringRiversPlayer*1000
        score -= scoringRiversOpponent*1100

        # Opponents blocked river by my stone
        blockedRiverOpponent = 0 # opponent's rivere blocked by player
        blockedRiverPlayer = 0 

        for y in range(rows):
            for x in range(cols):
                p = board[y][x]
                if p and p.owner == opponent and p.side == 'river':
                    if p.orientation == 'horizontal':
                        if in_bounds(x+1, y, rows, cols):
                            q = board[y][x+1]
                            if q and q.owner == player and q.side == 'stone':
                                blockedRiverOpponent = blockedRiverOpponent + 1

                        if in_bounds(x-1, y, rows, cols):
                            q = board[y][x-1]
                            if q and q.owner == player and q.side == 'stone':
                                blockedRiverOpponent = blockedRiverOpponent + 1
                    else:
                        if in_bounds(x, y+1, rows, cols):
                            q = board[y+1][x]
                            if q and q.owner == player and q.side == 'stone':
                                blockedRiverOpponent = blockedRiverOpponent + 1
                        if in_bounds(x, y-1, rows, cols):
                            q = board[y-1][x]
                            if q and q.owner == player and q.side == 'stone':
                                blockedRiverOpponent = blockedRiverOpponent + 1

                elif p and p.owner==player and p.side == 'river':
                        if p.orientation == 'horizontal':
                            if in_bounds(x+1, y, rows, cols):
                                q = board[y][x+1]
                                if q and q.owner == player and q.side == 'stone':
                                    blockedRiverPlayer = blockedRiverPlayer + 1

                            if in_bounds(x-1, y, rows, cols):
                                q = board[y][x-1]
                                if q and q.owner == player and q.side == 'stone':
                                    blockedRiverPlayer = blockedRiverPlayer + 1
                        else:
                            if in_bounds(x, y+1, rows, cols):
                                q = board[y+1][x]
                                if q and q.owner == player and q.side == 'stone':
                                    blockedRiverPlayer = blockedRiverPlayer + 1
                            if in_bounds(x, y-1, rows, cols):
                                q = board[y-1][x]
                                if q and q.owner == player and q.side == 'stone':
                                    blockedRiverPlayer = blockedRiverPlayer + 1


        score += blockedRiverOpponent * 400
        score -= blockedRiverPlayer * 450

        
        #Stones that can reach scoring in 1
        scoreCols = score_cols_for(cols)
        oneStepPlayer = getOneStep(board,top_score_row(), scoreCols, player)
        oneStepOpponent = getOneStep(board,bottom_score_row(rows), scoreCols, opponent)


        score -= oneStepOpponent*600
        score += oneStepPlayer*600
        
        # Manhattan feature
        mp, mo = manhattan(board, rows, cols)
        if player == 'square':
            mo, mp = mp, mo

        score = score + (mo - mp)*50


        # positional advantage
        for y in range(rows):
            for x in range(cols):
                p = board[y][x]
                if not p: continue
                if p.side == "stone":
                    if p.owner == "circle":
                        score += circlePositionalAdvantage[y][x] if player=="circle" else -circlePositionalAdvantage[y][x]
                    else:
                        score += square_table[y][x] if player=="square" else -square_table[y][x]
                elif p.side == "river":
                    if p.owner == player:
                        score += riverPositionalAdvantage[y][x]
                    else:
                        score -= riverPositionalAdvantage[y][x]
        
        _,isPM = self.generate_best_moves(player, board, rows, cols,score_cols)
        if isPM:
            score += 1500
        _,isPM = self.generate_best_moves(opponent, board, rows, cols,score_cols)
        if isPM:
            score -= 1600

        threatToOpponent = countPiecesBlocked(board, player, rows, cols, score_cols)
        threatToPlayer = countPiecesBlocked(board, opponent, rows, cols, score_cols)
        
        score += threatToOpponent*500
        score -= threatToPlayer*600

        return score

    def alphabetapruning(self, board: List[List[Any]], depth:int, player:str, max:bool, rows:int, cols:int, score_cols:List[int], alpha:float, beta:float):
        if(depth == 0):
            return self.evaluateBoard(board, rows, cols, score_cols), None # evaluate board
        moves, _ = self.generate_best_moves(player, board, rows, cols, score_cols)
        random.shuffle(moves) ## for value ordering i don't have idea right now so directly shuffling all moves
        
        if not moves:
            return self.evaluateBoard(board, rows, cols, score_cols), None # evaluate board
        # random.shuffle(moves)
        bestMove = None
        if player == self.player:
            maxUtility = float('-inf')
            for move in moves:
                valid, board2 = simulate_move(board, move, player, rows, cols, score_cols)
                if not valid:
                    continue
                util, _ = self. alphabetapruning(board2, depth-1, get_opponent(player), 0, rows, cols, score_cols, alpha, beta)
                if(util > maxUtility):
                    maxUtility = util
                    bestMove = move

                if(util > alpha):
                    alpha = util

                if alpha >= beta:
                    break
            return maxUtility, bestMove
        else:
            minUtility = float('inf')
            for move in moves:
                valid, board2 = simulate_move(board, move, player, rows, cols, score_cols)
                if not valid:
                    continue
                util, _ = self. alphabetapruning(board2, depth-1, get_opponent(player), 1, rows, cols, score_cols, alpha, beta)
                if(util < minUtility):
                    minUtility = util
                    bestMove = move

                if util < beta:
                    beta = util

                if alpha >= beta:
                    break
            return minUtility, bestMove

    def choose(self, board: List[List[Any]], rows: int, cols: int, score_cols: List[int], current_player_time: float, opponent_time: float) -> Optional[Dict[str, Any]]:
        """
        Choose the best move for the current board state.
        
        Args:
            board: 2D list representing the game board
            rows, cols: Board dimensions  
            score_cols: Column indices for scoring areas
            
        Returns:
            Dictionary representing your chosen move
        """
        util, bestMove = self.alphabetapruning(board, self.depth, self.player, 1, rows, cols, score_cols, float('-inf'), float('inf'))
        chosen_move = bestMove
        
        if chosen_move:
            valid, _ = simulate_move(board, chosen_move, self.player, rows, cols, score_cols)
            if valid:
                return chosen_move
            else:
                all_legal_moves, _ = self.generate_all_moves(self.player, board, rows, cols, score_cols)
                truly_valid_moves = []
                for move in all_legal_moves:
                    valid_check, _ = simulate_move(board, move, self.player, rows, cols, score_cols)
                    if valid_check:
                        truly_valid_moves.append(move)
                if truly_valid_moves:
                    return random.choice(truly_valid_moves)
                else:
                    return None 
        return None

# ==================== TESTING HELPERS ====================

def test_student_agent():
    """
    Basic test to verify the student agent can be created and make moves.
    """
    print("Testing StudentAgent...")

    try:
        from gameEngine import default_start_board, DEFAULT_ROWS, DEFAULT_COLS

        rows, cols = DEFAULT_ROWS, DEFAULT_COLS
        score_cols = score_cols_for(cols)
        board = default_start_board(rows, cols)

        agent = StudentAgent("circle")
        move = agent.choose(board, rows, cols, score_cols, 1.0, 1.0)

        if move:
            print("✓ Agent successfully generated a move")
        else:
            print("✗ Agent returned no move")

    except ImportError:
        agent = StudentAgent("circle")
        print("✓ StudentAgent created successfully")


if __name__ == "__main__":
    # Run basic test when file is executed directly
    test_student_agent()