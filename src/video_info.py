import re
import os
import requests
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp

class GetVideo:
    @staticmethod
    def extract_video_id(url):
        pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
        match = re.search(pattern, url)
        return match.group(1) if match else None

    @staticmethod
    def setup_proxy():
        proxy = os.environ.get("PROXY_URL")
        if proxy:
            os.environ["HTTP_PROXY"] = proxy
            os.environ["HTTPS_PROXY"] = proxy
        return proxy

    @staticmethod
    def get_metadata(url):
        # Always try to get title first
        proxy = GetVideo.setup_proxy()
        ydl_opts = {'quiet': True, 'proxy': proxy if proxy else None, 'no_warnings': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                return info_dict.get('title', 'Unknown Title'), info_dict.get('id', 'Unknown ID')
        except:
            # Fallback metadata via Invidious (more likely to be unblocked)
            try:
                video_id = GetVideo.extract_video_id(url)
                # Using a popular public Invidious instance
                inv_res = requests.get(f"https://invidious.snopyta.org/api/v1/videos/{video_id}", timeout=5)
                data = inv_res.json()
                return data.get('title', 'Unknown Title'), video_id
            except:
                return "Unknown Title", GetVideo.extract_video_id(url)

    @staticmethod
    def get_transcript(video_id):
        proxy = GetVideo.setup_proxy()
        proxies = {"http": proxy, "https": proxy} if proxy else None
        
        # METHOD 1: Primary extraction (Direct)
        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'], proxies=proxies)
            return GetVideo._format_transcript(transcript_data)
        except Exception as e:
            print(f"Primary fetch failed: {e}")

        # METHOD 2: Fallback extraction (Invidious API - Free & Stealthy)
        # We try multiple instances as they are community run
        instances = ["https://invidious.snopyta.org", "https://yewtu.be", "https://iv.ggtyler.dev"]
        for instance in instances:
            try:
                # Invidious has a captions API that is often not blocked
                res = requests.get(f"{instance}/api/v1/captions/{video_id}?label=English", timeout=7)
                if res.status_code == 200:
                    data = res.json()
                    # Invidious returns simple list, we format it
                    transcript_data = [{'text': c['text'], 'start': float(c['start']), 'duration': float(c['duration'])} for c in data.get('captions', [])]
                    if transcript_data:
                        return GetVideo._format_transcript(transcript_data)
            except:
                continue

        return None, "All extraction methods blocked by YouTube. Please use Manual Mode."

    @staticmethod
    def _format_transcript(data):
        raw_data_dicts = [
            {'text': d['text'], 'start': d.get('start', 0.0), 'duration': d.get('duration', 0.0)} 
            for d in data
        ]
        transcript = " ".join([d['text'] for d in data])
        return transcript, raw_data_dicts
