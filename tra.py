import os
import tempfile
import streamlit as st
from moviepy.editor import *
import openai

# Set the OpenAI API key
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "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"))

def convert_video_audio_to_wav(input_file):
    try:
        video = VideoFileClip(input_file)
        audio = video.audio
        output_file = "temp_audio.wav"
        audio.write_audiofile(output_file, codec="pcm_s16le", verbose=False)
        return output_file
    except Exception as e:
        st.error(f"An error occurred during audio extraction: {e}")
        return None

def transcribe_audio(audio_file_path):
    try:
        audio_file = open(audio_file_path, "rb")
        transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file, 
            response_format="text"
        )
        return transcription.text
    except Exception as e:
        st.error(f"An error occurred during transcription: {e}")
        return None
def main():
    st.title("Video to Text Converter")
    uploaded_file = st.file_uploader("Upload a video file", type=["mp4"])

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False) as fp:
            fp.write(uploaded_file.getvalue())
            audio_file_path = convert_video_audio_to_wav(fp.name)
            if audio_file_path is not None:
                with st.form(key='transcribe_form'):
                    st.write("Click the button below to transcribe the audio")
                    if st.form_submit_button(label='Transcribe Audio'):
                        transcription = transcribe_audio(audio_file_path)
                        if transcription:
                            st.subheader("Transcript:")
                            st.write(transcription)


if __name__ == "__main__":
    main()
