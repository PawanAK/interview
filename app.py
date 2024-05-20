import re
import streamlit as st 
import cv2
import base64
import tempfile
from openai import OpenAI
import os
import requests

# Initialize OpenAI client with the API key
api_key = os.environ.get("OPENAI_API_KEY", "sk-proj-yfQ1qZtjsOBqrtewnLfRT3BlbkFJGdaeUP4ZqO7WJY7SvaDo")
client = OpenAI(api_key=api_key)

def main():
    st.title('Interview Analysis')

    uploaded_video = st.file_uploader('Upload video', type=['mp4', 'mov', 'avi', 'flv', 'wmv', 'mkv', 'webm'])
    
    if uploaded_video is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_video.read())
        tfile.close()

        base64_frames = video_to_base64_frames(tfile.name)
        st.image(base64.b64decode(base64_frames[0]), caption='First frame')

        description = generate_description(base64_frames)
        st.write('Description', description)

        os.unlink(tfile.name)

def video_to_base64_frames(video_file_path):
    video = cv2.VideoCapture(video_file_path)
    base64_frames = []
    while video.isOpened():
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        base64_frames.append(base64.b64encode(buffer).decode('utf-8'))
    video.release()
    return base64_frames

def generate_description(base64_frames):
    try:
        prompt_messages = [
            {
                "role": "user",
                "content": [
                    "These are frames from a video that I want to upload. Generate a compelling description that I can upload along with the video.",
                    *map(lambda x: {"image": x, "resize": 768}, base64_frames[0::100]),
                ],
            },
        ]

        params = {
            "model": "gpt-4o",
            "messages": prompt_messages,
            "max_tokens": 600
        }

        st.write('Sending request to OpenAI API with parameters:', params)
        response = client.chat.completions.create(**params)
        return response.choices[0].message.content   
    except Exception as e:
        st.error("An error occurred")
        st.write('Error Details:', str(e))

        retry_button = st.button('Retry', key='retry_button')
        if retry_button:
            return generate_description(base64_frames)
        return None

if __name__ == '__main__':
    main()
