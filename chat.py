
import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)
from urllib.parse import urlparse, parse_qs

load_dotenv()  # Load environment variables (optional)

# Set your Gemini API key here or via .env
GEMINI_API_KEY = "" 
genai.configure(api_key=GEMINI_API_KEY)

# Extract YouTube video ID from URL
def extract_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname == "youtu.be":
        return parsed_url.path[1:]
    elif parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        return parse_qs(parsed_url.query).get("v", [None])[0]
    return None

# Fetch transcript text from preferred language, fallback to others
def extract_transcript_details(youtube_video_url, preferred_lang_code):
    video_id = extract_video_id(youtube_video_url)
    if not video_id:
        st.error("Invalid YouTube link.")
        return None

    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)

        transcript = None
        # Try to get manual or auto transcript in preferred language
        try:
            transcript = transcripts.find_manually_created_transcript([preferred_lang_code])
        except NoTranscriptFound:
            try:
                transcript = transcripts.find_generated_transcript([preferred_lang_code])
            except NoTranscriptFound:
                # Fallback: pick first available transcript in any language
                transcript = transcripts.find_transcript([t.language_code for t in transcripts])

        transcript_list = transcript.fetch()
        transcript_text = " ".join([t.text for t in transcript_list])
        return transcript_text, transcript.language_code

    except TranscriptsDisabled:
        st.error("Transcripts are disabled for this video.")
    except VideoUnavailable:
        st.error("Video is unavailable.")
    except NoTranscriptFound:
        st.error("No transcripts found in any language.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
    return None, None

# Generate summary using Gemini in the chosen language
def generate_gemini_content(transcript_text, summary_language):
    prompt = (
        f"You are a YouTube video summarizer. Summarize the following video transcript "
        f"in {summary_language}, providing the key points within 350 words. Please provide the summary of the text given here: "
    )
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        st.error(f"Gemini API Error: {e}")
        return None

# Streamlit UI
st.title("🎥 YouTube Transcript to Detailed Notes Converter")

# User input for YouTube URL
youtube_link = st.text_input("Enter YouTube Video Link:")

# Language selection for summary
summary_language = st.selectbox("Choose summary language:", ["English", "Hindi"])

# Map to language codes for transcript fetching
lang_code_map = {
    "English": "en",
    "Hindi": "hi"
}

if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        thumbnail_url = f"http://img.youtube.com/vi/{video_id}/0.jpg"
        st.image(thumbnail_url, use_container_width=True)
    else:
        st.error("Invalid YouTube link.")

if st.button("Get summary of the video"):
    if not youtube_link:
        st.error("Please enter a YouTube video link first.")
    else:
        preferred_lang_code = lang_code_map.get(summary_language, "en")
        with st.spinner("Fetching transcript..."):
            transcript_text, transcript_lang = extract_transcript_details(youtube_link, preferred_lang_code)

        if transcript_text:
            # Show which language transcript was actually fetched
            st.info(f"Transcript language detected: {transcript_lang}")

            with st.spinner("Generating summary..."):
                summary = generate_gemini_content(transcript_text, summary_language)

            if summary:
                st.markdown("📝 **Detailed Notes**")
                st.write(summary)
                st.success("Done ✅")
