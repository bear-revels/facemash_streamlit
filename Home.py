# import streamlit as st
# from utils import Database, Game, Home, Leaderboard, UI


# def main():
#     st.title("ARCADE")

#     db = Database()
#     home = Home(db)
#     home.display_home_page()


# if __name__ == "__main__":
#     main()


# Home.py
import streamlit as st
from utils.Home_file import Home

def main():
    st.set_page_config(page_title="ARCADE", layout="wide")
    Home.display_home_page()

if __name__ == "__main__":
    main()

