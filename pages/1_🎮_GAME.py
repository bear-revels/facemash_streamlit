# import streamlit as st
# from utils.Ui_file import UI
# from utils.Database_file import Database

# db = Database()
# db.refresh_images()
# game = UI(db)

# game.display_play_page()



# Pages/1_🎮_GAME.py
import streamlit as st
from utils import Game

def main():
    Game.display_game_page()

if __name__ == "__main__":
    main()
