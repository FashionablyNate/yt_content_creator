# Import the necessary libraries
from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer
from pydub import AudioSegment
import os, random, site
from moviepy.editor import VideoFileClip, ImageClip, AudioFileClip, CompositeVideoClip, concatenate_audioclips, concatenate_videoclips
from moviepy.decorators import requires_duration
from normalize import normalize_text

# Function to convert text to mp3 using TTS
def text_to_mp3(text, output_file):
    location = site.getsitepackages()[0]
    path = location + "/TTS/.models.json"
    model = "tts_models/en/ljspeech/vits"
    # Download model
    model_manager = ModelManager(path)
    model_path, config_path, _ = model_manager.download_model(model)
    # Initialize synthesizer
    synthesizer = Synthesizer(
        tts_checkpoint=model_path,
        tts_config_path=config_path,
    )
    # Generate audio and save as wav
    outputs = synthesizer.tts(normalize_text(text))
    synthesizer.save_wav(outputs, output_file + ".wav")
    # Convert wav to mp3 and remove the wav file
    AudioSegment.from_wav(output_file + ".wav").speedup(playback_speed=1.2).export(output_file + ".mp3", format='mp3')
    os.remove(output_file + ".wav")

def generate_audio( text, id, post_id ):
    file = os.path.join( "posts", f"{post_id}", "audio", f"clip_{id}" )
    if os.path.exists( file + ".mp3" ):
        return file + ".mp3"
    text_to_mp3( text, file )
    return file + ".mp3"

# Function to apply slide in effect from a given side
def slide_in_center(clip, duration, clip_size, side='top'):
    w, h = clip_size
    pos_dict = {
        "top": lambda t: ("center", h * 0.15 - (h * 0.3 - h * 0.15) * (1 - t / duration) if t < duration else h * 0.15),
        "bottom": lambda t: ("center", h * 0.15 + (h * 0.3 - h * 0.15) * (1 - t / duration) if t < duration else h * 0.15),
    }
    return clip.set_position(pos_dict[side])

# Function to apply slide out effect from a given side
@requires_duration
def slide_out_center(clip, duration, clip_size, side='bottom'):
    w, h = clip_size
    ts = clip.duration - duration  # start time of the effect.
    pos_dict = {
        "top": lambda t: ("center", h * 0.15 - ((h * 0.3 - h * 0.15) * ((t - ts) / duration)) if t > ts else h * 0.15),
        "bottom": lambda t: ("center", h * 0.15 + ((h * 0.3 - h * 0.15) * ((t - ts) / duration)) if t > ts else h * 0.15),
    }
    return clip.set_position(pos_dict[side])

# Function to create a video from a post and its comments
def create_video(post, selected_comments):
    # Generate the audio and get the durations of each clip
    final_audio = concatenate_audioclips( [post.audio] + [comment.audio for comment in selected_comments] )
    input_video = 'minecraft_parkour.mp4'
    output_video = os.path.join( "posts", post.object.id, "output_video.mp4" )
    phone_aspect_ratio = 9 / 16
    input_clip = VideoFileClip(input_video)
    video_duration = input_clip.duration
    # Start time is a random point in the video, making sure the video length matches the audio length
    start_time = random.uniform(0, video_duration - final_audio.duration)
    end_time = start_time + final_audio.duration
    random_clip = input_clip.subclip(start_time, end_time)
    target_width = int(input_clip.size[1] * phone_aspect_ratio)
    target_height = input_clip.size[1]
    padding_left = int((input_clip.size[0] - target_width) / 2)
    cropped_clip = random_clip.crop(x1=padding_left, x2=padding_left + target_width, y1=0, y2=target_height)
    # Create video clips for each audio clip
    video_clips = create_video_clips( post, selected_comments, input_clip, start_time, cropped_clip, padding_left, target_width, target_height, phone_aspect_ratio)
    final_video = concatenate_videoclips( video_clips )
    final_video = final_video.set_audio(final_audio)
    bitrate = calculate_bitrate(final_video.size[1])
    final_video.write_videofile(output_video, codec='libx264', fps=60, bitrate=bitrate, threads=4)
    final_video.close()
    input_clip.close()

# Function to create video clips for each audio clip
def create_video_clips(post, selected_comments, input_clip, start_time, cropped_clip, padding_left, target_width, target_height, phone_aspect_ratio):
    video_clips = []
    prev_duration = 0
    for duration, image in zip([post.audio.duration] + [comment.audio.duration for comment in selected_comments], [post.image] + [comment.image for comment in selected_comments]):
        segment_start = prev_duration
        segment_end = prev_duration + duration
        segment_clip = input_clip.subclip(start_time + segment_start, start_time + segment_end)
        cropped_clip = segment_clip.crop(x1=padding_left, x2=padding_left + target_width, y1=0, y2=target_height)
        # Get the corresponding image for this segment
        image = image.resize(width=input_clip.size[1] * phone_aspect_ratio - 100)
        video_clips += create_clip(cropped_clip, image, duration)
        prev_duration += duration
    return video_clips

# Function to create subsequent video clips (both fades in and out and slides in and out from the center)
def create_clip(cropped_clip, image, duration):
    video_clips = []
    cropped_clip1 = cropped_clip.subclip(0, duration / 2)
    cropped_clip2 = cropped_clip.subclip(duration / 2, duration)
    first_half = image.subclip(duration / 2, duration)
    first_half = first_half.crossfadein(0.5)
    first_half = slide_in_center(first_half, duration=0.5, clip_size=cropped_clip.size)
    second_half = image.subclip(0, duration / 2)
    second_half = second_half.crossfadeout(0.5)
    second_half = slide_out_center(second_half, duration=0.5, clip_size=cropped_clip.size)
    output_clip1 = CompositeVideoClip([cropped_clip1, first_half])
    output_clip2 = CompositeVideoClip([cropped_clip2, second_half])
    video_clips.append(output_clip1)
    video_clips.append(output_clip2)
    return video_clips

# Function to calculate the bitrate based on the video's height
def calculate_bitrate(height):
    if height == 2160:
        return "45M"
    elif height == 1440:
        return "20M"
    elif height == 1080:
        return "12M"
    else:
        return "8M"