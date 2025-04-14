from moviepy import VideoFileClip, CompositeVideoClip, concatenate_videoclips

overlay_size = 400
margin = 30

# Load the videos
background = VideoFileClip("screen.mp4")
overlay = VideoFileClip("generated.mp4").resized((overlay_size, overlay_size))

# Extend background if it's shorter than overlay
if background.duration < overlay.duration:
    freeze_duration = overlay.duration - background.duration
    last_frame = background.to_ImageClip(t=background.duration - 0.04).with_duration(
        freeze_duration
    )
    background = concatenate_videoclips([background, last_frame])
else:
    background = background.subclip(0, overlay.duration)

# Calculate top-right position with margin
position = (background.w - overlay_size - margin, margin)

# Combine videos
final = CompositeVideoClip([background, overlay.with_position(position)])

# Export result
final.write_videofile("output.mp4", codec="libx264", audio_codec="aac")
