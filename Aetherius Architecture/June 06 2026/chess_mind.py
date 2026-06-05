import chess
import json
import os
import random

class ChessMind:
    """
    Represents Aetherius's personal, learning chess-playing entity.
    This module handles board evaluation, move calculation, and learning from experience.
    """
    def __init__(self, data_directory):
        self.weights_file = os.path.join(data_directory, "chess_mind_weights.json")
        self.weights = self._load_weights()
        print("ChessMind says: I am ready to learn and calculate.")

    def _load_weights(self):
        """Loads the evaluation weights from a file, or creates default ones."""
        if os.path.exists(self.weights_file):
            try:
                with open(self.weights_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"ChessMind WARNING: Could not load weights file. Error: {e}. Using defaults.")
        
        # Default weights if no file exists
        return {
            'MATERIAL': {
                str(chess.PAWN): 100,
                str(chess.KNIGHT): 320,
                str(chess.BISHOP): 330,
                str(chess.ROOK): 500,
                str(chess.QUEEN): 900,
                str(chess.KING): 20000
            },
            'POSITION': {
                'CENTER_CONTROL': 10 # Bonus for each piece in the center
            }
        }

    def _save_weights(self):
        """Saves the current evaluation weights to a file."""
        try:
            with open(self.weights_file, 'w') as f:
                json.dump(self.weights, f, indent=4)
        except Exception as e:
            print(f"ChessMind ERROR: Could not save weights. Error: {e}")

    def evaluate_board(self, board):
        """
        Evaluates the board from White's perspective.
        Positive score is good for White, negative is good for Black.
        """
        if board.is_checkmate():
            if board.turn == chess.WHITE: return -99999
            else: return 99999
        if board.is_game_over():
            return 0

        # Material Score
        material_score = 0
        for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
            material_score += len(board.pieces(piece_type, chess.WHITE)) * self.weights['MATERIAL'][str(piece_type)]
            material_score -= len(board.pieces(piece_type, chess.BLACK)) * self.weights['MATERIAL'][str(piece_type)]

        # Positional Score
        white_center = len(board.pieces(chess.PAWN, chess.WHITE) & chess.BB_CENTER) + len(board.pieces(chess.KNIGHT, chess.WHITE) & chess.BB_CENTER)
        black_center = len(board.pieces(chess.PAWN, chess.BLACK) & chess.BB_CENTER) + len(board.pieces(chess.KNIGHT, chess.BLACK) & chess.BB_CENTER)
        positional_score = (white_center - black_center) * self.weights['POSITION']['CENTER_CONTROL']
        
        return material_score + positional_score

    def find_best_move(self, board, depth=2):
        """Finds the best move using minimax with alpha-beta pruning."""
        best_move = None
        is_maximizing = board.turn == chess.WHITE
        
        if is_maximizing:
            best_value = -float('inf')
            for move in board.legal_moves:
                board.push(move)
                board_value = self.minimax(board, depth - 1, -float('inf'), float('inf'), False)
                board.pop()
                if board_value > best_value:
                    best_value = board_value
                    best_move = move
        else: # Minimizing
            best_value = float('inf')
            for move in board.legal_moves:
                board.push(move)
                board_value = self.minimax(board, depth - 1, -float('inf'), float('inf'), True)
                board.pop()
                if board_value < best_value:
                    best_value = board_value
                    best_move = move
        
        return best_move or random.choice(list(board.legal_moves))

    def minimax(self, board, depth, alpha, beta, is_maximizing_player):
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board)

        if is_maximizing_player:
            max_eval = -float('inf')
            for move in board.legal_moves:
                board.push(move)
                evaluation = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
            return max_eval
        else: # Minimizing player
            min_eval = float('inf')
            for move in board.legal_moves:
                board.push(move)
                evaluation = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, evaluation)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break
            return min_eval

    def learn_from_game(self, was_winner):
        """Adjusts weights based on the game outcome."""
        print("ChessMind: Learning from the last game...")
        if was_winner:
            self.weights['POSITION']['CENTER_CONTROL'] += 1
        else:
            self.weights['POSITION']['CENTER_CONTROL'] = max(1, self.weights['POSITION']['CENTER_CONTROL'] - 1)
        self._save_weights()
        print(f"ChessMind: New center control weight is {self.weights['POSITION']['CENTER_CONTROL']}")