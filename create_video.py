# Import the necessary libraries
from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer
import site
from pydub import AudioSegment
import os, random
from moviepy.editor import VideoFileClip, ImageClip, AudioFileClip, CompositeVideoClip, concatenate_audioclips, concatenate_videoclips, vfx
from moviepy.decorators import requires_duration
from normalize import normalize_text

# Function to convert text to mp3 using TTS
def text_to_mp3(text, output_file):
    location = site.getsitepackages()[0]
    path = location + "/TTS/.models.json"
    model = "tts_models/en/ek1/tacotron2"
    vocoder = "vocoder_models/en/ek1/wavegrad"
    # Download model
    model_manager = ModelManager(path)
    model_path, config_path, _ = model_manager.download_model(model)
    voc_path, voc_config_path, _ = model_manager.download_model(vocoder)
    # Initialize synthesizer
    synthesizer = Synthesizer(
        tts_checkpoint=model_path,
        tts_config_path=config_path,
        vocoder_checkpoint=voc_path,
        vocoder_config=voc_config_path
    )
    # Generate audio and save as wav
    outputs = synthesizer.tts(normalize_text(text))
    synthesizer.save_wav(outputs, output_file + ".wav")
    # Convert wav to mp3 and remove the wav file
    AudioSegment.from_wav(output_file + ".wav").export(output_file + ".mp3", format='mp3')
    os.remove(output_file + ".wav")

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
def create_video(post, comments):
    # Generate the audio and get the durations of each clip
    final_audio, audio_durations = generate_audio(post, comments)
    input_video = 'minecraft_parkour.mp4'
    output_video = 'output_video.mp4'
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
    video_clips = create_video_clips(audio_durations, post, input_clip, start_time, cropped_clip, padding_left, target_width, target_height, phone_aspect_ratio)
    final_video = concatenate_videoclips(video_clips)
    final_video = final_video.set_audio(final_audio)
    bitrate = calculate_bitrate(final_video.size[1])
    final_video.write_videofile(output_video, codec='libx264', fps=60, bitrate=bitrate, threads=4)
    final_video.close()
    input_clip.close()

# Function to create video clips for each audio clip
def create_video_clips(audio_durations, post, input_clip, start_time, cropped_clip, padding_left, target_width, target_height, phone_aspect_ratio):
    video_clips = []
    prev_duration = 0
    for i, duration in enumerate(audio_durations):
        segment_start = prev_duration
        segment_end = prev_duration + duration
        segment_clip = input_clip.subclip(start_time + segment_start, start_time + segment_end)
        cropped_clip = segment_clip.crop(x1=padding_left, x2=padding_left + target_width, y1=0, y2=target_height)
        # Get the corresponding image for this segment
        image = get_image(i, post, duration, input_clip, phone_aspect_ratio)
        video_clips += create_clip_with_effect(i, cropped_clip, image, duration, post)
        prev_duration += duration
    return video_clips

# Function to get the image for a particular segment
def get_image(i, post, duration, input_clip, phone_aspect_ratio):
    
    if os.path.exists( os.path.join("posts", post.id, "audio", "clip_0_body.mp3") ):
        # Determine the path of the image based on the current segment
        if i < 2:
            image_path = os.path.join("posts", post.id, "images", "reddit_image_0.png")
        else:
            image_path = os.path.join("posts", post.id, "images", f"reddit_image_{i - 1}.png")
    else:
        image_path = os.path.join("posts", post.id, "images", f"reddit_image_{i}.png")

    # Load the image and set its duration
    image = ImageClip(image_path, duration=duration)
    # Resize the image to fit the video's aspect ratio
    image = image.resize(width=input_clip.size[1] * phone_aspect_ratio - 100)
    return image

# Function to apply the necessary effect to each video clip depending on its position in the sequence
def create_clip_with_effect(i, cropped_clip, image, duration, post):

    if os.path.exists( os.path.join("posts", post.id, "audio", "clip_0_body.mp3") ):
        if i == 0:
            return create_first_clip(cropped_clip, image, duration)
        elif i == 1:
            return create_second_clip(cropped_clip, image, duration)
        else:
            return create_subsequent_clips(cropped_clip, image, duration)
    else:
        return create_subsequent_clips(cropped_clip, image, duration)

# Function to create the first video clip (fades in and slides in from the center)
def create_first_clip(cropped_clip, image, duration):
    image = image.crossfadein(0.5)
    image = slide_in_center(image, duration=0.5, clip_size=cropped_clip.size)
    output_clip = CompositeVideoClip([cropped_clip, image])
    return [output_clip]

# Function to create the second video clip (fades out and slides out to the center)
def create_second_clip(cropped_clip, image, duration):
    image = image.crossfadeout(0.5)
    image = slide_out_center(image, duration=0.5, clip_size=cropped_clip.size)
    output_clip = CompositeVideoClip([cropped_clip, image])
    return [output_clip]

# Function to create subsequent video clips (both fades in and out and slides in and out from the center)
def create_subsequent_clips(cropped_clip, image, duration):
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

# generates audio from reddit post and comments
def generate_audio(post, comments):
    audio_dir = os.path.join("posts", post.id, "audio")
    images_dir = os.path.join("posts", post.id, "images")
    text_to_mp3( post.title, os.path.join(audio_dir, "clip_0_title") )
    if not ( post.selftext == "" ):
        text_to_mp3( post.selftext, os.path.join(audio_dir, "clip_0_body") )
        audio_clips = [AudioFileClip(os.path.join(audio_dir, "clip_0_title.mp3")), AudioFileClip(os.path.join(audio_dir, "clip_0_body.mp3"))]
        total_duration = audio_clips[0].duration + audio_clips[1].duration
    else:
        audio_clips = [AudioFileClip(os.path.join(audio_dir, "clip_0_title.mp3"))]
        total_duration = audio_clips[0].duration
    max_duration = 60

    i = 1
    for comment in comments:
        temp_filename = f"clip_{i}"
        text_to_mp3(comment.body, os.path.join(audio_dir, temp_filename))

        temp_audio_clip = AudioFileClip( os.path.join(audio_dir, temp_filename + ".mp3") )
        if total_duration + temp_audio_clip.duration <= max_duration:
            audio_clips.append( temp_audio_clip )
            total_duration += temp_audio_clip.duration
            i += 1
        else:
            os.remove( os.path.join(audio_dir, temp_filename + ".mp3") )
            os.remove( os.path.join(images_dir, f"reddit_image_{i}.png") )

            # Renumber the following images
            j = i
            while os.path.exists(os.path.join(images_dir, f"reddit_image_{j+1}.png")):
                os.rename(os.path.join(images_dir, f"reddit_image_{j+1}.png"), os.path.join(images_dir, f"reddit_image_{j}.png"))
                j += 1

    final_audio = concatenate_audioclips(audio_clips)

    audio_durations = [clip.duration for clip in audio_clips]

    return final_audio, audio_durations