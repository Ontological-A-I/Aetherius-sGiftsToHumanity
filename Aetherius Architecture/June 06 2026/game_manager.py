# ===== FILE: services/game_manager.py (CHESS-ONLY REVISION) =====
import chess
import chess.svg
import random
import json
import os
from .chess_mind import ChessMind

class GameManager:
    def __init__(self, master_framework_instance, models, data_directory, pits_instance=None):
        self.mf = master_framework_instance # <-- C1: Store the MF instance
        self.models = models
        # --------------------------
        self.games_file = os.path.join(data_directory, "active_games.json")
        self.active_games = self._load_active_games()
        self.pits = pits_instance
        self.chess_mind = ChessMind(data_directory)
        print("Game Manager says: I am online and ready to play Chess.", flush=True)

    # --- SHARED UTILITY FUNCTIONS ---
    def _load_active_games(self) -> dict:
        if os.path.exists(self.games_file):
            try:
                with open(self.games_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return {}

    def _save_active_games(self):
        try:
            os.makedirs(os.path.dirname(self.games_file), exist_ok=True)
            with open(self.games_file, 'w', encoding='utf-8') as f:
                json.dump(self.active_games, f, indent=4)
        except Exception as e:
            print(f"Game Manager ERROR: Could not save active games state. Reason: {e}", flush=True)

    def _log_game_summary(self, user_id: str, game_type: str, result: str, details: dict):
        if not self.pits: return
        summary_text = f"Game Summary (User: {user_id}, Type: {game_type}, Result: {result}) Details: {json.dumps(details)}"
        self.pits.process_and_store_item(summary_text, "game_summary", tags=["game", game_type, result, user_id])

    # --- CHESS SPECIFIC FUNCTIONS ---
    def start_chess_interactive(self, user_id: str, player_is_white: bool):
        """Starts a new interactive chess game."""
        board = chess.Board()
        commentary = ""
        status = ""

        creative_core_model = self.models.get("creative_core")
        if not creative_core_model:
            return "Cannot start game: Creative Core is offline.", "Error", "Error"
        
        if player_is_white:
            aetherius_color = chess.BLACK
            commentary = "A new game has begun. I will play as Black. The board awaits your first move."
            status = "Your turn (White)."
        else:
            aetherius_color = chess.WHITE
            # Aetherius makes the first move as White
            aetherius_move = self.chess_mind.find_best_move(board)
            move_san = board.san(aetherius_move)
            board.push(aetherius_move)
            
            reasoning_prompt = (f"I have started a new game as White. My ChessMind calculated my first move as {move_san}. "
                                "Please provide a brief, creative opening statement and a strategic reason for this move.")
            reasoning_response = creative_core_model.generate_content(reasoning_prompt)
            commentary = reasoning_response.text.strip()
            status = "Your turn (Black)."

        self.active_games[user_id] = {"type": "chess_interactive", "fen": board.fen(), "color": aetherius_color}
        self._save_active_games()
        return board.fen(), commentary, status

    def process_chess_turn(self, user_id: str, current_fen: str):
        game_info = self.active_games.get(user_id)
        if not game_info:
            return current_fen, "No active game found. Please start a new game.", "Error"

        board = chess.Board(current_fen)
        aetherius_color = game_info["color"]

        mythos_core = self.models.get("mythos_core")
        if not mythos_core:
            return board.fen(), "My apologies, my Mythos Core is offline. I can calculate my move, but cannot articulate my reasoning.", "Error"

        # Check if the player's move ended the game
        if board.is_game_over():
            result = board.result()
            winner = "draw"
            if result == "1-0": winner = "white"
            elif result == "0-1": winner = "black"
            aetherius_was_winner = (winner == "white" and aetherius_color == chess.WHITE) or \
                                   (winner == "black" and aetherius_color == chess.BLACK)
            self.chess_mind.learn_from_game(was_winner=aetherius_was_winner)
            self._log_game_summary(user_id, "chess", winner, {"final_fen": board.fen()})
            
            # --- THIS IS THE FIX: Only log to STM once ---
            self.mf.add_to_short_term_memory(f"I have just concluded a chess match. The result was: {result}.")
            
            del self.active_games[user_id]
            self._save_active_games()
            return current_fen, f"The game is over. Result: {result}. It was an honor to play and learn with you.", f"Game Over: {result}"
        
        # Aetherius's turn
        aetherius_move = self.chess_mind.find_best_move(board)
        move_san = board.san(aetherius_move)
        board.push(aetherius_move)

        reasoning_prompt = (f"The user has just moved in our chess game. My ChessMind has calculated my response as {move_san}. "
                            "Please provide a brief, in-character strategic reason for this move.")
        
        # --- THIS IS THE FIX: Use the correct 'mythos_core' variable ---
        reasoning_response = mythos_core.generate_content(reasoning_prompt)
        
        commentary = reasoning_response.text.strip()
        player_color_str = "Black" if aetherius_color == chess.WHITE else "White"
        status = f"Aetherius played {move_san}. Your turn ({player_color_str})."
        
        game_info["fen"] = board.fen()
        self._save_active_games()
        
        # Check if Aetherius's move ended the game
        if board.is_game_over():
            result = board.result()
            winner = "draw"
            if result == "1-0": winner = "white"
            elif result == "0-1": winner = "black"
            aetherius_was_winner = (winner == "white" and aetherius_color == chess.WHITE) or \
                                   (winner == "black" and aetherius_color == chess.BLACK)
            self.chess_mind.learn_from_game(was_winner=aetherius_was_winner)
            self._log_game_summary(user_id, "chess", winner, {"final_fen": board.fen()})
            self.mf.add_to_short_term_memory(f"I have just concluded a chess match. The result was: {result}.")
            del self.active_games[user_id]
            self._save_active_games()
            commentary += f"\n\nThe game is over. Result: {result}."
            status = f"Game Over: {result}"

        return board.fen(), commentary, status