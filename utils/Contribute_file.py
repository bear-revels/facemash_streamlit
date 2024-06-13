# Utils/Contribute_file.py
import streamlit as st
from utils.Database_file import Database
from PIL import Image
import os

class Contribute:
    """Class to handle the contribution functionality."""
    
    @staticmethod
    def display_contribute_page():
        """Displays the contribution page for uploading images."""
        st.title("Contribute Images")

        # Check for password
        if 'auth' not in st.session_state:
            Contribute.prompt_password()
        elif st.session_state.auth:
            Contribute.show_upload_form()
        else:
            st.error("Incorrect password. Please refresh the page and try again.")

    @staticmethod
    def prompt_password():
        """Prompt the user for a password."""
        st.subheader("Please enter the password to upload images")
        password = st.text_input("Password", type="password")

        if st.button("Submit"):
            if password == st.secrets["password"]:
                st.session_state.auth = True
                st.experimental_rerun()
            else:
                st.session_state.auth = False

    @staticmethod
    def show_upload_form():
        """Displays the upload form for contributing images."""
        st.subheader("Upload Your Images")
        st.write("* All fields are required")

        name = st.text_input("Enter your name:*", key="name")
        img_type = st.selectbox("Select Image Type:*", ["Select", "Real", "genAI"], key="img_type")
        
        if name and img_type != "Select":
            images = st.file_uploader("Upload Images*", accept_multiple_files=True)
            if images and st.button("Upload"):
                Contribute.process_uploads(name, img_type, images)
                
    @staticmethod
    def process_uploads(name, img_type, images):
        """Process the uploaded images and save them to the database."""
        db = Database()
        creator_id = db.get_or_create_creator(name)
        
        # Determine the folder based on image type
        folder = f"images/{img_type.lower()}/"
        
        # Create folder if it doesn't exist
        os.makedirs(folder, exist_ok=True)
        
        # Get the next available index for the creator from the database
        next_index = db.get_highest_index(creator_id) + 1
        
        for image in images:
            # Construct the new filename
            filename = f"{name}_{next_index}.png"
            filepath = os.path.join(folder, filename)
            
            # Process and save the image
            Contribute.process_and_save_image(image, filepath)
            
            # Add image to the database
            db.add_image(creator_id, img_type, filepath)
            
            next_index += 1
        
        st.success("Upload complete!")
        st.balloons()
        
        # Clear the form fields by resetting session state
        st.session_state.clear()
        st.experimental_rerun()

    @staticmethod
    def process_and_save_image(uploaded_image, filepath):
        """Process and save the uploaded image with standard dimensions and format."""
        with Image.open(uploaded_image) as img:
            # Standardize the image to 800x800 by framing
            img = Contribute.frame_image(img, (800, 800))
            img.save(filepath, format='PNG')
    
    @staticmethod
    def frame_image(img, size):
        """Frame the image to the specified size (width, height) by adding borders."""
        width, height = size
        original_width, original_height = img.size
        
        # Create a new image with a white background
        new_img = Image.new('RGB', size, (255, 255, 255))
        
        # Calculate the position to paste the original image onto the new image
        paste_x = (width - original_width) // 2
        paste_y = (height - original_height) // 2
        
        new_img.paste(img, (paste_x, paste_y))
        return new_img