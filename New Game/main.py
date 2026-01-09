from game_engine import GameEngine

def main():
    game = GameEngine()
    try:
        game.start()
    except KeyboardInterrupt:
        print("\n\nGame force quit. Progress may not be saved.")
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
