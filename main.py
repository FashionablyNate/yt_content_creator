from dataclasses import dataclass
import os, asyncio, knapsack, shutil
from take_screenshot import take_screenshot_post, take_screenshot_comment
from reddit import connect, get_post, get_comments
from create_video import create_video, generate_audio
from database import video_exists, insert_video
from moviepy.editor import AudioFileClip, ImageClip
from upload_video import get_authenticated_service, initialize_upload

description = '''

📝 Description:

Welcome to another exciting episode of Reddit Stories over Minecraft Parkour! In this video, we dive into some of the most interesting Reddit threads while showcasing some thrilling Minecraft Parkour action. If you're a fan of Minecraft, Reddit stories, or both, this video is for you!

Join me as I navigate through pixelated landscapes and obstacles, all while narrating some of the best stories Reddit has to offer. From life advice to hilarious anecdotes, we've got a wide range of Reddit posts covered in this episode.

Make sure to stick around until the end to catch some epic parkour moves and hear the conclusion of our Reddit Stories!

🔗 Links:

Reddit: www.reddit.com
Minecraft: www.minecraft.net
Minecraft Parkour Video: https://www.youtube.com/watch?v=n_Dv4...

📺 Check out my other videos: [Insert playlist or specific video links]

👍 If you enjoyed this video, don't forget to LIKE, SHARE, and SUBSCRIBE for more content like this! Leave a comment below to let me know what you think, and which Reddit threads you'd like to hear in the next video!

🔔 Hit the bell icon to get notified every time I post a new video. Thanks for watching!
'''

def create_content_post( post ):
    audio_clip = AudioFileClip( generate_audio( post.title + " " + post.selftext, post.id, post.id ) )
    image_clip = ImageClip( asyncio.run( take_screenshot_post( post ) ) )
    return Content( post, image_clip, audio_clip )

def create_content_comment( post, comment ):
    audio_clip = AudioFileClip( generate_audio( comment.body, comment.id, post.id ) )
    image_clip = ImageClip( asyncio.run( take_screenshot_comment( post, comment ) ) )
    return Content( comment, image_clip, audio_clip )

def remove_directories(directory):
    for root, dirs, files in os.walk(directory, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            shutil.rmtree(os.path.join(root, dir))
    os.rmdir(directory)


reddit = connect()
posts, subreddit_name = get_post( reddit )

@dataclass
class Content:
    object: any
    image: any
    audio: any

content_dict = {

}

for post in posts:
    if not video_exists( post.id ):
        if not os.path.exists( "posts" ):
            os.mkdir( "posts" )
        if not os.path.exists( "posts/" + post.id ):
            os.mkdir( "posts/" + post.id )
        if not os.path.exists( "posts/" + post.id + "/images" ):
            os.mkdir( "posts/" + post.id + "/images" )
        if not os.path.exists( "posts/" + post.id + "/audio" ):
            os.mkdir( "posts/" + post.id + "/audio" )
        print( "Processing Post: " + "https://reddit.com" + post.permalink )
        content_dict[post.id] = create_content_post( post )
        
        if ( content_dict[post.id].audio.duration > 60 ):
            insert_video( post.id )
            remove_directories( "posts/" + post.id )
            continue
        else:
            comments = get_comments( post )
            duration = []
            upvotes = []
            ids = []
            keys_to_remove = []
            for comment in comments:
                print( "Processing Comment: " + "https://reddit.com" + comment.permalink )
                try:
                    content_dict[comment.id] = create_content_comment( post, comment )
                    duration.append( content_dict[comment.id].audio.duration )
                    upvotes.append( content_dict[comment.id].object.ups )  # Assuming comment.score is the upvote count
                    ids.append(comment.id)
                except Exception as e:
                    content_dict[comment.id] = None
                    print( f"Error: {e}" )

            _, indices = knapsack.knapsack(duration, upvotes).solve(60 - content_dict[post.id].audio.duration)

            selected_comments = [content_dict[ids[i]] for i in indices if content_dict[ids[i]] is not None]

            create_video( content_dict[post.id], selected_comments )
            insert_video( post.id )
            youtube = get_authenticated_service()
            file_path = os.path.join( "posts", post.id, "output_video.mp4" )
            initialize_upload( youtube, file_path, "public", subreddit_name + " " + post.title, "🔴 r/AskWomen: " + post.title + description )
            break