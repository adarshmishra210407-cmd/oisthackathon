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
    def get_metadata(url):
        proxy = os.environ.get("PROXY_URL")
        ydl_opts = {'quiet': True, 'proxy': proxy if proxy else None, 'no_warnings': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                return info_dict.get('title', 'Unknown Title'), info_dict.get('id', 'Unknown ID')
        except:
            return "Unknown Title", GetVideo.extract_video_id(url)

    @staticmethod
    def get_transcript(video_id):
        proxy = os.environ.get("PROXY_URL")
        proxies = {"http": proxy, "https": proxy} if proxy else None
        
        # METHOD 1: Primary extraction
        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'], proxies=proxies)
            return GetVideo._format_transcript(transcript_data)
        except Exception as e:
            print(f"Primary fetch failed: {e}")

        # METHOD 2: Advanced Mirror Fallback (Using stable instances)
        instances = [
            "https://inv.nadeko.net",
            "https://invidious.namazso.eu",
            "https://invidious.snopyta.org",
            "https://yewtu.be"
        ]
        
        for instance in instances:
            try:
                # Some instances use different API paths
                res = requests.get(f"{instance}/api/v1/captions/{video_id}?label=English", timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    captions = data.get('captions', [])
                    if not captions: continue
                    transcript_data = [{'text': c['text'], 'start': float(c['start']), 'duration': float(c['duration'])} for c in captions]
                    return GetVideo._format_transcript(transcript_data)
            except:
                continue

        # METHOD 3: The "Last Resort" API (Scraper Fallback)
        try:
            # Using a public transcription proxy if available
            res = requests.get(f"https://api.allorigins.win/get?url={requests.utils.quote(f'https://www.youtube.com/watch?v={video_id}')}", timeout=5)
            # This is complex to parse, but we try anyway
            if res.status_code == 200:
                 pass # Placeholder for advanced parsing if needed
        except:
            pass

        return None, "Blocked"

    @staticmethod
    def _format_transcript(data):
        raw_data_dicts = [
            {'text': d['text'], 'start': d.get('start', 0.0), 'duration': d.get('duration', 0.0)} 
            for d in data
        ]
        transcript = " ".join([d['text'] for d in data])
        return transcript, raw_data_dicts
