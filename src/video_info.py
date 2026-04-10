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
    def setup_proxy():
        proxy = os.environ.get("PROXY_URL")
        if proxy:
            # Set global environment handles
            os.environ["HTTP_PROXY"] = proxy
            os.environ["HTTPS_PROXY"] = proxy
        return proxy

    @staticmethod
    def get_metadata(url):
        proxy = GetVideo.setup_proxy()
        ydl_opts = {
            'quiet': True,
            'proxy': proxy if proxy else None,
            'no_warnings': True,
            'nocheckcertificate': True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                return info_dict.get('title', 'Unknown Title'), info_dict.get('id', 'Unknown ID')
        except Exception as e:
            print(f"Metadata Error: {e}")
            return "Unknown Title", "Unknown ID"

    @staticmethod
    def get_transcript(video_id):
        proxy = GetVideo.setup_proxy()
        proxies = {"http": proxy, "https": proxy} if proxy else None
        
        try:
            # Direct proxy fetch
            try:
                transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'], proxies=proxies)
            except:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id, proxies=proxies)
                # Try English, then any available
                try:
                    selected_transcript = transcript_list.find_transcript(['en'])
                except:
                    selected_transcript = next(iter(transcript_list))
                transcript_data = selected_transcript.fetch()
                
            raw_data_dicts = [
                {'text': d['text'], 'start': d.get('start', 0.0), 'duration': d.get('duration', 0.0)} 
                for d in transcript_data
            ]
            
            transcript = " ".join([d['text'] for d in transcript_data])
            return transcript, raw_data_dicts
        except Exception as e:
            print(f"Detailed Transcript Error: {e}")
            return None, str(e)
