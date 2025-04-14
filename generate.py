import requests
import dotenv
import os

# Load environment variables from .env file
dotenv.load_dotenv()
HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")
if HEYGEN_API_KEY is None:
    raise ValueError("HEYGEN_API_KEY environment variable not set.")


def generate_video(api_key, avatar_id, voice_id, input_text, speed=1.0):
    url = "https://api.heygen.com/v2/video/generate"
    headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
    data = {
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,
                    "avatar_style": "normal",
                },
                "voice": {
                    "type": "text",
                    "input_text": input_text,
                    "voice_id": voice_id,
                    "speed": speed,
                },
            }
        ],
        "dimension": {"width": 1280, "height": 720},
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()


avatar_id = "Brandon_expressive_public"
voice_id = "1bd001e7e50f421d891986aad5158bc8"
text = "Hello, this is a test video."

res = generate_video(
    api_key=HEYGEN_API_KEY,
    avatar_id=avatar_id,
    voice_id=voice_id,
    input_text=text,
    speed=1.0,
)

if res.error:
    print("Error:", res.error)
else:
    data = res.data
    video_id = data.video_id
