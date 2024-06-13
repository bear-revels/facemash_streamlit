# import streamlit as st
# from utils.Ui_file import UI
# from utils.Database_file import Database

# db = Database()
# db.refresh_images()
# board = UI(db)

# board.display_leaderboard_page()


# Pages/3_🏆_Leaderboard.py
import streamlit as st
from utils.Leaderboard_file import Leaderboard

def main():
    st.set_page_config(page_title="Leaderboard", layout="wide")
    Leaderboard.display_leaderboard_page()

if __name__ == "__main__":
    main()