from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys

# Add the root directory to sys.path so the 'src' module can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from src.video_info import GetVideo
    from src.model import Model
    from src.prompt import Prompt
    from src.timestamp_formatter import TimestampFormatter
except ImportError:
    # Fallback for different Vercel structure
    from video_info import GetVideo
    from model import Model
    from prompt import Prompt
    from timestamp_formatter import TimestampFormatter

from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/transcript")
@app.get("/transcript") # Catch-all for routing
async def get_transcript(url: str):
    try:
        video_id = GetVideo.extract_video_id(url)
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
        title, _ = GetVideo.get_metadata(url)
        transcript, raw_list = GetVideo.get_transcript(video_id)
        
        if not transcript:
            raise HTTPException(status_code=404, detail="Transcript not available or blocked by YouTube")
        
        return {"title": title, "transcript": transcript, "raw": raw_list}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/ai_process")
async def ai_process(data: dict = Body(...)):
    transcript = data.get("transcript")
    action = data.get("action")
    model_type = data.get("model_type", "Gemini")
    model_version = data.get("model_version", "gemini-2.0-flash")

    try:
        engine = Model(model_type, model_version)
        if action == "summary":
            prompt = Prompt.get_summary_prompt()
            result = engine.generate(prompt, transcript)
        elif action == "timestamp":
            prompt = Prompt.get_timestamp_prompt()
            raw_output = engine.generate(prompt, transcript)
            result = TimestampFormatter.format(raw_output)
        elif action == "quiz":
            prompt = Prompt.get_quiz_prompt()
            result = engine.generate(prompt, transcript)
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route to serve internal static files from /static folder
app.mount("/assets", StaticFiles(directory="static"), name="assets")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')
