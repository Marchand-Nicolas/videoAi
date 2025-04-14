from moviepy import (
    VideoFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    ImageClip,
)
from datetime import datetime
import numpy as np
from PIL import Image, ImageDraw, ImageFont

overlay_size = 400
margin = 30


def parse_ass_dialogues(ass_path):
    dialogues = []
    with open(ass_path, encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        if line.startswith("Dialogue:"):
            parts = line.strip().split(",", 9)  # Only split first 9 commas
            start = parts[1]
            end = parts[2]
            text = parts[9].replace("\\n", "\n")
            dialogues.append(
                {
                    "start": parse_ass_time(start),
                    "end": parse_ass_time(end),
                    "text": text,
                }
            )
    return dialogues


from moviepy import TextClip, ColorClip, CompositeVideoClip, ImageClip
import numpy as np
from PIL import Image, ImageDraw


def render_subtitles(
    dialogues, video_size, bottom_margin=60, font_size=36, padding=20, corner_radius=15
):
    subtitle_clips = []

    for line in dialogues:
        # Load font (safe fallback to default)
        try:
            font = ImageFont.truetype("Arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        # Create text image
        text = line["text"]
        max_width = int(video_size[0] * 0.8)

        # Measure multiline text
        temp_img = Image.new("RGBA", (max_width, 1), (0, 0, 0, 0))
        draw = ImageDraw.Draw(temp_img)
        lines = []
        words = text.split()
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            width = draw.textlength(test_line, font=font)
            if width > max_width:
                lines.append(current_line.strip())
                current_line = word + " "
            else:
                current_line = test_line
        lines.append(current_line.strip())

        line_height = font.getbbox("Hg")[3]  # Approximate line height
        text_height = len(lines) * line_height
        text_width = max([draw.textlength(l, font=font) for l in lines])

        # Create background box
        box_w = int(text_width + padding * 2)
        box_h = int(text_height + padding * 2)
        bg_img = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 200))

        # Rounded corners (mask)
        mask = Image.new("L", (box_w, box_h), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle(
            (0, 0, box_w, box_h), radius=corner_radius, fill=255
        )
        bg_img.putalpha(mask)

        # Draw text on top
        draw = ImageDraw.Draw(bg_img)
        for i, text_line in enumerate(lines):
            y = padding + i * line_height
            draw.text((padding, y), text_line, font=font, fill="white")

        # Convert to ImageClip
        clip = ImageClip(np.array(bg_img)).with_duration(line["end"] - line["start"])
        clip = clip.with_position(("center", video_size[1] - box_h - bottom_margin))
        clip = clip.with_start(line["start"]).with_end(line["end"])

        subtitle_clips.append(clip)

    return subtitle_clips


def parse_ass_time(t):
    # Format: H:MM:SS.cs
    dt = datetime.strptime(t.strip(), "%H:%M:%S.%f")
    return dt.hour * 3600 + dt.minute * 60 + dt.second + dt.microsecond / 1e6


# Load videos
background = VideoFileClip("screen.mp4")
overlay = VideoFileClip("generated.mp4").resized((overlay_size, overlay_size))

# Extend background if needed
if background.duration < overlay.duration:
    freeze_duration = overlay.duration - background.duration
    last_frame = background.to_ImageClip(t=background.duration - 0.04).with_duration(
        freeze_duration
    )
    background = concatenate_videoclips([background, last_frame])
else:
    background = background.subclip(0, overlay.duration)

# Position overlay
position = (background.w - overlay_size - margin, margin)

# Parse and render subtitles
dialogues = parse_ass_dialogues("caption.ass")
subtitle_clips = render_subtitles(dialogues, video_size=(background.w, background.h))

# Combine everything
final = CompositeVideoClip(
    [background, overlay.with_position(position)] + subtitle_clips
)

# Export
final.write_videofile("output.mp4", codec="libx264", audio_codec="aac")
