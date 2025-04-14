import requests
import dotenv
import os
import time

# Load environment variables from .env file
dotenv.load_dotenv()
HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")
if HEYGEN_API_KEY is None:
    raise ValueError("HEYGEN_API_KEY environment variable not set.")


def generate_video(api_key, avatar_id, voice_id, input_text, caption, speed=1.0):
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
        "dimension": {"width": 720, "height": 720},
        "caption": caption,
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()


avatar_id = "Brandon_expressive_public"
voice_id = "1bd001e7e50f421d891986aad5158bc8"
text = "Did you know you can explore the fossil record of life — all from your screen?\
Welcome to the Fossils category on Wikimedia Commons — a treasure trove of ancient life, from ammonites to mammoths.\
With over 40 subcategories, you can dive into fossils by age, location, or type. Even 3D scans.\
From detailed fossil preservation stages to stunning quality and valued images, this archive is perfect for students, researchers, and the simply curious.\
Want more info? Each entry connects to deeper knowledge through Wikipedia, authority records, and more.\
And guess what — you can contribute too. Share your fossil discoveries and become part of this living archive.\
Dig into Earth's past — one fossil at a time. Explore the Fossils category on Wikimedia Commons today."

res = generate_video(
    api_key=HEYGEN_API_KEY,
    avatar_id=avatar_id,
    voice_id=voice_id,
    input_text=text,
    caption=True,
    speed=1.0,
)

print("Response:", res)

if res["error"]:
    print("Error:", res["error"])
else:
    data = res["data"]
    video_id = data["video_id"]

    def get_status(video_id):
        url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
        headers = {"X-Api-Key": HEYGEN_API_KEY}
        response = requests.get(url, headers=headers)
        return response.json()

    status = "waiting"
    data = None
    while status != "completed":
        res = get_status(video_id)
        if res["data"]["error"]:
            print("Error:", res["data"]["error"])
            break
        else:
            data = res["data"]
            status = data["status"]
        print("⏳ Waiting for video generation...")
        time.sleep(3)

    print("✨ AI video generation completed.")
    video_url = data["video_url"]

    # Download video as "generated.mp4"

    video_response = requests.get(video_url)
    with open("generated.mp4", "wb") as f:
        f.write(video_response.content)
    print("🎥 Video downloaded as generated.mp4")
