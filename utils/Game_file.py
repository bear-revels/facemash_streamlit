# import streamlit as st
# import random
# from utils import Database


# class Game:
#     def __init__(self):
#         """Initialize the Game class with a database instance."""
#         self.db = Database()

#     def display_play_page(self):
#         """Display the game play page."""
#         player_name = st.text_input("Enter your name to start playing:", "")
#         if player_name:
#             if "player_id" not in st.session_state:
#                 st.session_state.player_id = self.db.add_player(player_name)
#             self.start_game()

#     def start_game(self):
#         """Start the game and handle game logic."""
#         if "level" not in st.session_state:
#             st.session_state.level = 1
#             st.session_state.score = 0
#             st.session_state.timer = 30
#         #
#         real_image = self.db.select_images_real()
#         genai_image = self.db.select_images_real()
#         images = [(real_image, 1), (genai_image, 0)]
#         random.shuffle(images)

#         col1, col2 = st.columns(2)
#         with col1:
#             if st.button("Select Left Image", key="left"):
#                 self.check_selection(images[0][1] == 1)
#             st.image(images[0][0][0]['filepath'], use_column_width=False)
#         with col2:
#             if st.button("Select Right Image", key="right"):
#                 self.check_selection(images[1][1] == 1)
#             st.image(images[1][0][0]['filepath'], use_column_width=False)

#     def check_selection(self, is_real_image):
#         """Check the user's selection and update the game state."""
#         if is_real_image:
#             st.session_state.score += 1
#             st.session_state.level += 1
#             st.session_state.timer *= 0.9
#             st.write(f"Correct! Your current score: {st.session_state.score}")
#             self.start_game()
#         else:
#             st.write("Wrong! Game Over!")
#             st.write(f"Your final score: {st.session_state.score}")
#             st.session_state.page = "home"


# Utils/Game_file.py
import streamlit as st
import random
from utils.Database_file import Database
from utils.Leaderboard_file import Leaderboard

class Game:
    """Class to handle the game functionality."""
    
    def __init__(self):
        self.db = Database()
        self.db.refresh_active_status()  # Refresh the database status
        self.images = self.db.get_active_images()
        self.current_image_pair = random.sample(self.images, 2)
        self.player_name = ""
        self.match_count = 0
        if 'reviewed_images' not in st.session_state:
            st.session_state.reviewed_images = set()
        
    @staticmethod
    def display_game_page():
        """Displays the game page."""
        st.title("Game Page")
        player_name = st.text_input("Enter your name to start playing:", key="player_name")
        
        if player_name:
            game = Game()
            game.player_name = player_name
            if 'match_count' not in st.session_state:
                st.session_state.match_count = 0
            if 'current_image_pair' not in st.session_state:
                st.session_state.current_image_pair = game.current_image_pair
            Game.play_game(game)
    
    @staticmethod
    def play_game(game):
        """Main game loop to display images and capture player choices."""
        if st.session_state.match_count >= 10:
            Game.display_pause_screen(game)
        else:
            st.write(f"Match {st.session_state.match_count + 1} of 10")
            st.write("Click the image you like better:")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("Choose Image 1"):
                    game.process_choice(st.session_state.current_image_pair[0], st.session_state.current_image_pair[1])
            with col2:
                if st.button("Choose Image 2"):
                    game.process_choice(st.session_state.current_image_pair[1], st.session_state.current_image_pair[0])

            col1.image(st.session_state.current_image_pair[0]['filepath'], use_column_width=True)
            col2.image(st.session_state.current_image_pair[1]['filepath'], use_column_width=True)

    @staticmethod
    def display_pause_screen(game):
        """Displays the pause screen with leaderboard and options to continue or view leaderboard."""
        st.write("Level complete!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Continue playing"):
                st.session_state.match_count = 0
                Game.play_game(game)
        with col2:
            if st.button("View full leaderboard"):
                Leaderboard.display_leaderboard_page()

        st.write("Top 5 Images You Reviewed:")
        Game.display_reviewed_leaderboard()
    
    @staticmethod
    def display_reviewed_leaderboard():
        """Displays the leaderboard of reviewed images."""
        db = Database()
        reviewed_images = list(st.session_state.reviewed_images)
        if not reviewed_images:
            st.write("No images reviewed yet.")
            return
        
        placeholders = ', '.join('?' for _ in reviewed_images)
        query = f"""
            SELECT image_id, filepath, score, (SELECT creator_name FROM creators WHERE creator_id = images.creator_id)
            FROM images
            WHERE image_id IN ({placeholders})
            ORDER BY score DESC
            LIMIT 5
        """
        scores = db.conn.execute(query, reviewed_images).fetchall()
        
        for index, entry in enumerate(scores):
            st.write(f"Rank {index + 1}")
            col1, col2, col3 = st.columns([1, 3, 2])
            col1.image(entry[1], width=50)
            col2.write(f"Score: {entry[2]}")
            col3.write(f"Creator: {entry[3]}")
            st.write("---")

    def process_choice(self, winner, loser):
        """Process the chosen image and update the next pair."""
        self.update_image_score(winner, loser)
        
        # Keep track of reviewed images
        st.session_state.reviewed_images.add(winner['image_id'])
        st.session_state.reviewed_images.add(loser['image_id'])
        
        # Keep the chosen image and replace the other one
        if winner == st.session_state.current_image_pair[0]:
            st.session_state.current_image_pair[1] = self.get_new_image()
        else:
            st.session_state.current_image_pair[0] = self.get_new_image()
        
        if len(self.images) < 2:
            self.images = self.db.get_active_images()  # Reset images when run out

        st.session_state.match_count += 1

    def get_new_image(self):
        """Get a new image that is not currently displayed."""
        remaining_images = [img for img in self.images if img not in st.session_state.current_image_pair]
        if not remaining_images:
            remaining_images = self.db.get_active_images()
            remaining_images = [img for img in remaining_images if img not in st.session_state.current_image_pair]
        return random.choice(remaining_images)

    def update_image_score(self, winner, loser):
        """Update the ELO score of the chosen image."""
        Leaderboard.update_elo(winner['image_id'], loser['image_id'])