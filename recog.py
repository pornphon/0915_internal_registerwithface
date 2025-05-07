import os
import requests
import streamlit as st

#ยังรอแก้ไข  error อยู่


# Azure API Credentials
AZURE_FACE_ENDPOINT = os.getenv('AZURE_FACE_ENDPOINT')
AZURE_FACE_KEY = os.getenv('AZURE_FACE_KEY')
FACE_LIST_ID = 'album_list'

from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials

face_client = FaceClient(AZURE_FACE_ENDPOINT, CognitiveServicesCredentials(AZURE_FACE_KEY))

# Create Face List
def create_face_list():
    try:
        face_client.face_list.create(face_list_id=FACE_LIST_ID, name='Album List')
        st.success("Face List created successfully.")
    except Exception as e:
        st.error(f"Error creating face list: {e}")

# Upload Images to Album without creating Person
def upload_images(files):
    try:
        for image_file in files:
            with image_file:
                faces = face_client.face.detect_with_stream(image_file)
                for face in faces:
                    face_id = face.face_id
                    st.write(f"Detected face ID: {face_id}")
                    image_file.seek(0)
                    face_client.face_list.add_face_from_stream(FACE_LIST_ID, image_file)
        st.success("Images uploaded and faces added successfully.")
    except Exception as e:
        st.error(f"Error uploading images: {e}")

# Search for Person in Album
def search_person(image_file):
    try:
        with image_file:
            faces = face_client.face.detect_with_stream(image_file)
        if not faces:
            st.warning("No faces detected in the search image.")
            return

        face_ids = [face.face_id for face in faces]
        search_results = []
        for face_id in face_ids:
            results = face_client.face.find_similar(face_id=face_id, face_list_id=FACE_LIST_ID)
            for result in results:
                search_results.append(result.persisted_face_id)

        if search_results:
            st.success("Found matches in the album:")
            for face_id in search_results:
                st.write(f"Matched Face ID: {face_id}")
        else:
            st.info("No matches found in the album.")

    except Exception as e:
        st.error(f"Error during search: {e}")

# Streamlit UI
def main():
    st.title("Azure Face Recognition Album System")

    if st.button("Create Album List"):
        create_face_list()

    st.subheader("Upload Images to Album")
    uploaded_files = st.file_uploader("Select images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    if st.button("Upload to Album") and uploaded_files:
        upload_images(uploaded_files)

    st.subheader("Search for Person in Album")
    search_file = st.file_uploader("Select image to search", type=["jpg", "jpeg", "png"])
    if st.button("Search in Album") and search_file:
        search_person(search_file)

if __name__ == "__main__":
    main()