from espeakng import ESpeakNG
from pydub import AudioSegment
import os, tempfile, random, subprocess
from moviepy.editor import VideoFileClip, ImageClip, AudioFileClip, CompositeVideoClip, concatenate_audioclips, concatenate_videoclips
from gtts import gTTS

def text_to_mp3(text, output_file):
    # Create a temporary WAV file to store the synthesized speech
    with tempfile.NamedTemporaryFile(delete=False) as temp_wav_file:
        temp_wav_path = temp_wav_file.name

    # Synthesize speech using the espeak command-line tool and save it to the temporary WAV file
    command = f'espeak -w "{temp_wav_path}" "{text}"'
    subprocess.run(command, shell=True, check=True)

    # Load the synthesized speech as an AudioSegment
    audio_segment = AudioSegment.from_wav(temp_wav_path)

    # Export the audio_segment as an MP3 file
    audio_segment.export(output_file, format="mp3")

    # Delete the temporary WAV file
    os.remove(temp_wav_path)

def create_video( post, comments ):

    final_audio, audio_durations = generate_audio( post, comments )

    input_video = 'minecraft_parkour.mp4'
    output_video = 'output_video.mp4'

    # Define the desired aspect ratio for the phone screen
    phone_aspect_ratio = 9 / 16  # Width:Height ratio

    # Read the input video
    input_clip = VideoFileClip( input_video )

    # Choose a random 10-second clip
    video_duration = input_clip.duration
    start_time = random.uniform( 0, video_duration - final_audio.duration )
    end_time = start_time + final_audio.duration
    random_clip = input_clip.subclip(start_time, end_time)

    # Calculate the target width and height based on the aspect ratio
    target_width = int(input_clip.size[1] * phone_aspect_ratio)
    target_height = input_clip.size[1]

    # Calculate the left and right padding to center the video horizontally
    padding_left = int((input_clip.size[0] - target_width) / 2)

    # Crop the video with center coordinates
    cropped_clip = random_clip.crop(x1=padding_left, x2=padding_left + target_width, y1=0, y2=target_height)

    video_clips = []

    prev_duration = 0
    for i, duration in enumerate(audio_durations):
        # Calculate the segment start and end times based on the current duration
        segment_start = prev_duration
        segment_end = prev_duration + duration
        
        # Create a new cropped_clip for the current segment
        segment_clip = input_clip.subclip(start_time + segment_start, start_time + segment_end)
        cropped_clip = segment_clip.crop(x1=padding_left, x2=padding_left + target_width, y1=0, y2=target_height)

        image = ImageClip(f"reddit_image_{i}.png", duration=duration)
        image = image.resize(width=input_clip.size[1] * phone_aspect_ratio - 20)
        image = image.set_position((10, 50))
        overlay = CompositeVideoClip([cropped_clip, image])
        output_clip = overlay

        # Append the output_clip to the video_clips list
        video_clips.append(output_clip)

        prev_duration += duration

    # Concatenate the video clips after the loop
    final_video = concatenate_videoclips(video_clips)

    # Set the audio and write the result to a file
    final_video = final_video.set_audio(final_audio)
    final_video.write_videofile(output_video, codec='libx264')

    # Close the video clips to release resources
    final_video.close()
    input_clip.close()

def generate_audio( post, comments ):

    text_to_mp3( post.title, "title.mp3" )
    
    comment_mp3s = []
    for i, comment in enumerate( comments ):
        text_to_mp3( comment.body, f"comment{i}.mp3" )
        comment_mp3s.append( f"comment{i}.mp3" )

    audio_clips = []
    audio_clips.append( AudioFileClip( 'title.mp3' ) )
    for audio_file in comment_mp3s:
        audio_clips.append( AudioFileClip( audio_file ) )

    final_audio = concatenate_audioclips( audio_clips )

    audio_durations = []
    for audio_clip in audio_clips:
        duration = audio_clip.duration
        audio_durations.append(duration)

    return final_audio, audio_durations