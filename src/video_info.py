import re
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp

class GetVideo:
    @staticmethod
    def extract_video_id(url):
        # regex for extraction of youtube video id
        pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
        match = re.search(pattern, url)
        return match.group(1) if match else None

    @staticmethod
    def get_metadata(url):
        ydl_opts = {'quiet': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                return info_dict.get('title', 'Unknown Title'), info_dict.get('id', 'Unknown ID')
        except Exception:
            return "Unknown Title", "Unknown ID"

    @staticmethod
    def get_transcript(video_id):
        try:
            # Get the list of all available transcripts
            transcript_list = YouTubeTranscriptApi().list(video_id)
            all_transcripts = list(transcript_list)
            
            if not all_transcripts:
                return None, "No transcripts available for this video."

            # Automatically choose the best available transcript (prefer manual over auto-generated)
            # Regardless of the language code. 
            manual_transcripts = [t for t in all_transcripts if not t.is_generated]
            
            if manual_transcripts:
                selected_transcript = manual_transcripts[0]
            else:
                selected_transcript = all_transcripts[0]
                
            raw_data = selected_transcript.fetch()
            
            # The new version returns a list of FetchedTranscriptSnippet objects, not dicts
            raw_data_dicts = [
                {'text': d.text, 'start': getattr(d, 'start', 0.0), 'duration': getattr(d, 'duration', 0.0)} 
                for d in raw_data
            ]
            
            transcript = " ".join([d.text for d in raw_data])
            return transcript, raw_data_dicts
        except Exception as e:
            return None, str(e)
