from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound
import google.generativeai as genai
from api import gemini_api_key
import re

genai.configure(api_key=gemini_api_key)

def extract_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([item['text'] for item in transcript])
        return full_text
    except NoTranscriptFound:
        return None

def summarize_text(text):
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"""
    Summarize the following YouTube video transcript into a well-structured summary with bullet points or clear sections, while keeping this short and simple:
    - Key Takeaways
    - Main Points Discussed
    - Conclusion

    Transcript:
    {text}
    """
    response = model.generate_content(prompt)
    return response.text

def clean_gemini_output(raw_text):
    cleaned = re.sub(r"\*\*(.*?)\*\*", lambda m: m.group(1).upper(), raw_text)
    cleaned = re.sub(r"^\s*\*\s*", "- ", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\*", "", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned

if __name__ == "__main__":
    youtube_url = input("Enter the YouTube URL: ")
    video_id = extract_video_id(youtube_url)
    
    if not video_id:
        print("Invalid YouTube URL.")
    else:
        transcript = get_transcript(video_id)
        if transcript is None:
            print("No transcript found for this video.")
        else:
            summary = summarize_text(transcript)
            formatted_summary = clean_gemini_output(summary)

            print("\n📄 Video Summary:\n")
            print(formatted_summary)
