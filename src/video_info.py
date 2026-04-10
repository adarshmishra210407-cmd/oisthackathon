import re
import os
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
        ydl_opts = {
            'quiet': True,
            'proxy': proxy if proxy else None,
            'no_warnings': True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                return info_dict.get('title', 'Unknown Title'), info_dict.get('id', 'Unknown ID')
        except Exception:
            return "Unknown Title", "Unknown ID"

    @staticmethod
    def get_transcript(video_id):
        proxy = os.environ.get("PROXY_URL")
        proxies = {"http": proxy, "https": proxy} if proxy else None
        
        try:
            # We use the proxy for both listing and fetching
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id, proxies=proxies)
            
            # Prefer manual transcripts
            try:
                selected_transcript = transcript_list.find_manually_created_transcript()
            except:
                selected_transcript = transcript_list.find_generated_transcript(['en'])
                
            raw_data = selected_transcript.fetch()
            
            # Format the data for our JS frontend
            raw_data_dicts = [
                {'text': d['text'], 'start': d.get('start', 0.0), 'duration': d.get('duration', 0.0)} 
                for d in raw_data
            ]
            
            transcript = " ".join([d['text'] for d in raw_data])
            return transcript, raw_data_dicts
        except Exception as e:
            return None, str(e)
