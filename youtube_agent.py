import streamlit as st
import google.generativeai as genai
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import re

# Configure Gemini API
genai.configure(api_key="AIzaSyCd5_L41Tmd87XnbzGN4-7sN1-u0tmFYN")  # Replace with your API key
model = genai.GenerativeModel("gemini-2.5-flash")

# YouTube API Key - Replace with your own
YOUTUBE_API_KEY = "AIzaSyB7XDT5VOC8fqXM2dH7Sv0NuPJYWbIWpbc"  # Get from Google Cloud Console

def search_youtube(topic, max_results=5):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(
        q=topic + " tutorial learn",
        part='snippet',
        type='video',
        order='relevance',
        maxResults=max_results
    )
    response = request.execute()
    videos = []
    for item in response['items']:
        video_id = item['id']['videoId']
        title = item['snippet']['title']
        description = item['snippet']['description']
        url = f"https://www.youtube.com/watch?v={video_id}"
        videos.append({
            'id': video_id,
            'title': title,
            'description': description,
            'url': url
        })
    return videos

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([entry['text'] for entry in transcript])
        return text
    except Exception as e:
        return f"Transcript not available: {str(e)}"

def summarize_text(text, title):
    if "Transcript not available" in text:
        # Summarize description instead
        prompt = f"Summarize this YouTube video based on its title and description. Title: {title}. Description: {text}"
    else:
        prompt = f"Summarize this YouTube video transcript in 2-3 sentences. Transcript: {text[:2000]}"  # Limit to avoid token limits
    response = model.generate_content(prompt)
    return response.text

st.title("AI YouTube Learning Agent")

topic = st.text_input("Enter a topic to learn about:")

if st.button("Search and Summarize"):
    if topic:
        with st.spinner("Searching YouTube..."):
            videos = search_youtube(topic)
        
        if videos:
            st.subheader(f"Top Learning Videos for '{topic}'")
            for i, video in enumerate(videos, 1):
                st.write(f"**{i}. {video['title']}**")
                st.write(f"[Watch Video]({video['url']})")
                
                with st.spinner(f"Getting summary for video {i}..."):
                    transcript = get_transcript(video['id'])
                    summary = summarize_text(transcript, video['title'])
                
                st.write(f"**Summary:** {summary}")
                st.write("---")
        else:
            st.write("No videos found.")
    else:
        st.write("Please enter a topic.")